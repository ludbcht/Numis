from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext
from scraper import CoinScraper

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None

class Coin(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    country: str
    year: int
    description: str
    mintage: int
    image_url: str
    value_fdc: float
    value_bu: float
    value_be: float

class CollectionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coin_id: str
    user_id: str
    condition: str  # FDC, BU, BE
    notes: Optional[str] = None
    added_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AddToCollectionRequest(BaseModel):
    coin_id: str
    condition: str
    notes: Optional[str] = None

class UpdateCollectionRequest(BaseModel):
    condition: Optional[str] = None
    notes: Optional[str] = None

class Stats(BaseModel):
    total_coins: int
    owned_coins: int
    completion_percentage: float
    total_value: float
    by_country: dict

# Initialize database
async def initialize_database():
    """Initialize database with coins and user"""
    # Check if user exists
    user = await db.users.find_one({"username": "Ludivine"})
    if not user:
        hashed_password = pwd_context.hash("Ludivine67")
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "username": "Ludivine",
            "password": hashed_password
        })
        logger.info("User Ludivine created")
    
    # Check if coins exist
    coin_count = await db.coins.count_documents({})
    if coin_count == 0:
        logger.info("Starting coin scraping from ECB website...")
        scraper = CoinScraper()
        coins_data = await scraper.scrape_coins()
        logger.info(f"Scraping completed. Inserting {len(coins_data)} coins...")
        for coin_data in coins_data:
            coin = Coin(**coin_data)
            await db.coins.insert_one(coin.model_dump())
        logger.info(f"Initialized {len(coins_data)} coins")

@app.on_event("startup")
async def startup_event():
    await initialize_database()

# Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = await db.users.find_one({"username": request.username}, {"_id": 0})
    
    if not user or not pwd_context.verify(request.password, user["password"]):
        return LoginResponse(
            success=False,
            message="Identifiants incorrects"
        )
    
    # Remove password from response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return LoginResponse(
        success=True,
        message="Connexion réussie",
        user=user_data
    )

@api_router.get("/coins", response_model=List[Coin])
async def get_coins(
    country: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None
):
    query = {}
    
    if country:
        query["country"] = country
    if year:
        query["year"] = year
    if search:
        query["$or"] = [
            {"description": {"$regex": search, "$options": "i"}},
            {"country": {"$regex": search, "$options": "i"}}
        ]
    
    coins = await db.coins.find(query, {"_id": 0}).sort("year", -1).to_list(1000)
    return coins

@api_router.get("/coins/{coin_id}", response_model=Coin)
async def get_coin(coin_id: str):
    coin = await db.coins.find_one({"id": coin_id}, {"_id": 0})
    if not coin:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    return coin

@api_router.get("/collection")
async def get_collection(user_id: str):
    collection_items = await db.collection.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    # Enrich with coin data
    result = []
    for item in collection_items:
        coin = await db.coins.find_one({"id": item["coin_id"]}, {"_id": 0})
        if coin:
            # Convert datetime to ISO string for JSON serialization
            if isinstance(item.get('added_date'), datetime):
                item['added_date'] = item['added_date'].isoformat()
            result.append({
                **item,
                "coin": coin
            })
    
    return result

@api_router.post("/collection/add")
async def add_to_collection(request: AddToCollectionRequest, user_id: str):
    # Check if coin exists
    coin = await db.coins.find_one({"id": request.coin_id}, {"_id": 0})
    if not coin:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    # Check if already in collection
    existing = await db.collection.find_one({
        "user_id": user_id,
        "coin_id": request.coin_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Pièce déjà dans la collection")
    
    collection_item = CollectionItem(
        coin_id=request.coin_id,
        user_id=user_id,
        condition=request.condition,
        notes=request.notes
    )
    
    doc = collection_item.model_dump()
    doc['added_date'] = doc['added_date'].isoformat()
    
    await db.collection.insert_one(doc)
    return {"success": True, "message": "Pièce ajoutée à la collection"}

@api_router.delete("/collection/{item_id}")
async def remove_from_collection(item_id: str, user_id: str):
    result = await db.collection.delete_one({"id": item_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    return {"success": True, "message": "Pièce retirée de la collection"}

@api_router.put("/collection/{item_id}")
async def update_collection_item(item_id: str, request: UpdateCollectionRequest, user_id: str):
    update_data = {}
    if request.condition:
        update_data["condition"] = request.condition
    if request.notes is not None:
        update_data["notes"] = request.notes
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    result = await db.collection.update_one(
        {"id": item_id, "user_id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    
    return {"success": True, "message": "Collection mise à jour"}

@api_router.get("/collection/stats", response_model=Stats)
async def get_stats(user_id: str):
    total_coins = await db.coins.count_documents({})
    
    collection_items = await db.collection.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    owned_coins = len(collection_items)
    
    # Calculate total value
    total_value = 0.0
    for item in collection_items:
        coin = await db.coins.find_one({"id": item["coin_id"]}, {"_id": 0})
        if coin:
            condition = item["condition"].lower()
            if condition == "fdc":
                total_value += coin["value_fdc"]
            elif condition == "bu":
                total_value += coin["value_bu"]
            elif condition == "be":
                total_value += coin["value_be"]
    
    # Group by country
    by_country = {}
    for item in collection_items:
        coin = await db.coins.find_one({"id": item["coin_id"]}, {"_id": 0})
        if coin:
            country = coin["country"]
            by_country[country] = by_country.get(country, 0) + 1
    
    completion_percentage = (owned_coins / total_coins * 100) if total_coins > 0 else 0
    
    return Stats(
        total_coins=total_coins,
        owned_coins=owned_coins,
        completion_percentage=round(completion_percentage, 2),
        total_value=round(total_value, 2),
        by_country=by_country
    )

@api_router.get("/countries")
async def get_countries():
    coins = await db.coins.find({}, {"_id": 0, "country": 1}).to_list(1000)
    countries = list(set(coin["country"] for coin in coins))
    return sorted(countries)

@api_router.get("/years")
async def get_years():
    coins = await db.coins.find({}, {"_id": 0, "year": 1}).to_list(1000)
    years = list(set(coin["year"] for coin in coins))
    return sorted(years, reverse=True)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
