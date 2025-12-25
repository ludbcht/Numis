import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class CoinScraper:
    """Web scraper pour les pièces de 2 euros commémoratives depuis le site de la BCE"""
    
    def __init__(self):
        self.base_url = "https://www.ecb.europa.eu"
        self.coins_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_coins(self) -> List[Dict]:
        """Scrape les données des pièces de 2 euros commémoratives depuis la BCE"""
        try:
            coins = await self.scrape_ecb_coins()
            if not coins:
                logger.warning("Scraping failed, using initial data")
                coins = await self.get_initial_coin_data()
            return coins
        except Exception as e:
            logger.error(f"Error in scrape_coins: {e}")
            return await self.get_initial_coin_data()
    
    async def scrape_ecb_coins(self) -> List[Dict]:
        """Scrape le site officiel de la BCE en français"""
        coins = []
        
        # Années à scraper (de 2004 à 2024)
        years = range(2004, 2025)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for year in years:
                try:
                    # URL pour chaque année EN FRANÇAIS
                    url = f"{self.base_url}/euro/coins/comm/html/comm_{year}.fr.html"
                    logger.info(f"Scraping ECB year {year} (FR): {url}")
                    
                    response = await client.get(url, headers=self.headers, follow_redirects=True)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        year_coins = self.parse_year_page(soup, year)
                        coins.extend(year_coins)
                        logger.info(f"Found {len(year_coins)} coins for {year}")
                    else:
                        logger.warning(f"Failed to fetch {year}: {response.status_code}")
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error scraping year {year}: {e}")
                    continue
        
        logger.info(f"Total ECB coins scraped: {len(coins)}")
        return coins
    
    def parse_year_page(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Parse une page d'année pour extraire les pièces"""
        coins = []
        
        # Le site BCE utilise des div.box pour chaque pièce
        coin_boxes = soup.find_all('div', class_='box')
        
        for box in coin_boxes:
            try:
                coin = self.extract_coin_from_box(box, year)
                if coin:
                    coins.append(coin)
            except Exception as e:
                logger.debug(f"Error parsing box: {e}")
                continue
        
        return coins
    
    def extract_coin_from_box(self, box, year: int) -> Dict:
        """Extrait les informations d'une pièce depuis une box div"""
        # Chercher le pays dans le h3
        country = "Unknown"
        country_elem = box.find('h3')
        if country_elem:
            country = country_elem.get_text(strip=True)
        
        # Chercher l'image
        img = box.find('img')
        image_url = ""
        if img:
            image_url = img.get('src', '')
            if image_url and not image_url.startswith('http'):
                # S'assurer que le chemin commence par /
                if not image_url.startswith('/'):
                    image_url = '/' + image_url
                # Construire l'URL complète avec le bon chemin
                image_url = self.base_url + '/euro/coins/comm/html/' + image_url.lstrip('/')
        
        # Extraire les informations de la content-box
        content_box = box.find('div', class_='content-box')
        if not content_box:
            return None
        
        # Description
        description = "Pièce commémorative"
        feature_elem = content_box.find('p')
        if feature_elem:
            feature_text = feature_elem.get_text(strip=True)
            if ':' in feature_text:
                description = feature_text.split(':', 1)[1].strip()
            else:
                description = feature_text
        
        # Tirage (chercher "Issuing volume")
        mintage = 1000000
        text = content_box.get_text()
        mintage_match = re.search(r'Issuing volume[:\s]+([0-9,\s]+)', text, re.I)
        if mintage_match:
            mintage_str = mintage_match.group(1).replace(',', '').replace(' ', '').strip()
            try:
                mintage = int(mintage_str)
            except:
                mintage = 1000000
        
        return {
            "country": country,
            "year": year,
            "description": description[:200],
            "mintage": mintage,
            "image_url": image_url or f"https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
            "value_fdc": self.estimate_value(mintage, "fdc"),
            "value_bu": self.estimate_value(mintage, "bu"),
            "value_be": self.estimate_value(mintage, "be")
        }
    
    def estimate_value(self, mintage: int, condition: str) -> float:
        """Estime la valeur d'une pièce selon son tirage et son état"""
        # Valeurs de base selon le tirage
        if mintage < 100000:
            base_values = {"fdc": 15.0, "bu": 30.0, "be": 60.0}
        elif mintage < 500000:
            base_values = {"fdc": 8.0, "bu": 15.0, "be": 30.0}
        elif mintage < 1000000:
            base_values = {"fdc": 5.0, "bu": 10.0, "be": 20.0}
        elif mintage < 5000000:
            base_values = {"fdc": 4.0, "bu": 7.0, "be": 14.0}
        else:
            base_values = {"fdc": 3.0, "bu": 5.0, "be": 10.0}
        
        return base_values.get(condition, 4.0)
    
    async def get_initial_coin_data(self) -> List[Dict]:
        """Données initiales de secours si le scraping échoue"""
        return coins
    
    async def get_initial_coin_data(self) -> List[Dict]:
        """Données initiales des pièces de 2 euros commémoratives"""
        coins = [
            {
                "country": "France",
                "year": 2024,
                "description": "Jeux Olympiques et Paralympiques Paris 2024",
                "mintage": 5000000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.0,
                "value_bu": 8.0,
                "value_be": 15.0
            },
            {
                "country": "France",
                "year": 2023,
                "description": "200 ans de la naissance de Louis Pasteur",
                "mintage": 3000000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.5,
                "value_bu": 7.5,
                "value_be": 14.0
            },
            {
                "country": "France",
                "year": 2022,
                "description": "Simone Veil",
                "mintage": 4000000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.0,
                "value_bu": 7.0,
                "value_be": 13.0
            },
            {
                "country": "Allemagne",
                "year": 2024,
                "description": "Thuringe",
                "mintage": 30000000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 3.5,
                "value_bu": 6.0,
                "value_be": 12.0
            },
            {
                "country": "Allemagne",
                "year": 2023,
                "description": "Mecklembourg-Poméranie-Occidentale",
                "mintage": 30000000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 3.5,
                "value_bu": 6.0,
                "value_be": 12.0
            },
            {
                "country": "Italie",
                "year": 2024,
                "description": "150e anniversaire de la naissance de Guglielmo Marconi",
                "mintage": 3000000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.5,
                "value_bu": 8.0,
                "value_be": 15.0
            },
            {
                "country": "Italie",
                "year": 2023,
                "description": "150 ans de la mort d'Alessandro Manzoni",
                "mintage": 3000000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.0,
                "value_bu": 7.5,
                "value_be": 14.0
            },
            {
                "country": "Espagne",
                "year": 2024,
                "description": "Présidence du Conseil de l'UE",
                "mintage": 3000000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.0,
                "value_bu": 7.0,
                "value_be": 13.0
            },
            {
                "country": "Espagne",
                "year": 2023,
                "description": "Avila",
                "mintage": 1000000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.0,
                "value_bu": 9.0,
                "value_be": 16.0
            },
            {
                "country": "Belgique",
                "year": 2024,
                "description": "Présidence belge du Conseil de l'UE",
                "mintage": 200000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 6.0,
                "value_bu": 12.0,
                "value_be": 22.0
            },
            {
                "country": "Luxembourg",
                "year": 2024,
                "description": "200 ans de la Constitution",
                "mintage": 500000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.5,
                "value_bu": 10.0,
                "value_be": 18.0
            },
            {
                "country": "Portugal",
                "year": 2024,
                "description": "50 ans de la Révolution des Œillets",
                "mintage": 1000000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.0,
                "value_bu": 8.5,
                "value_be": 16.0
            },
            {
                "country": "Grèce",
                "year": 2024,
                "description": "150 ans de la naissance de Constantin Caratheodory",
                "mintage": 750000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.0,
                "value_bu": 9.0,
                "value_be": 17.0
            },
            {
                "country": "Pays-Bas",
                "year": 2024,
                "description": "Effigie du Roi Willem-Alexander",
                "mintage": 3000000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 4.0,
                "value_bu": 7.0,
                "value_be": 13.0
            },
            {
                "country": "Finlande",
                "year": 2024,
                "description": "Élections et démocratie",
                "mintage": 400000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.5,
                "value_bu": 10.0,
                "value_be": 18.0
            },
            {
                "country": "Monaco",
                "year": 2024,
                "description": "Prince Albert II",
                "mintage": 15000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 50.0,
                "value_bu": 100.0,
                "value_be": 200.0
            },
            {
                "country": "Vatican",
                "year": 2024,
                "description": "Pape François",
                "mintage": 80000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 20.0,
                "value_bu": 40.0,
                "value_be": 80.0
            },
            {
                "country": "San Marin",
                "year": 2024,
                "description": "500 ans de la mort du Pérugin",
                "mintage": 60000,
                "image_url": "https://images.unsplash.com/photo-1630856826965-f274fce8e532?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 25.0,
                "value_bu": 50.0,
                "value_be": 100.0
            },
            {
                "country": "Malte",
                "year": 2024,
                "description": "Jeux de l'Île",
                "mintage": 100000,
                "image_url": "https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 15.0,
                "value_bu": 30.0,
                "value_be": 60.0
            },
            {
                "country": "Autriche",
                "year": 2024,
                "description": "100 ans de la Radio autrichienne",
                "mintage": 1000000,
                "image_url": "https://images.unsplash.com/photo-1634108941345-3a6a66685563?q=85&w=600&auto=format&fit=crop",
                "value_fdc": 5.0,
                "value_bu": 8.5,
                "value_be": 16.0
            }
        ]
        return coins
