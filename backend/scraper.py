import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class CoinScraper:
    """Web scraper pour les pièces de 2 euros commémoratives"""
    
    def __init__(self):
        self.base_url = "https://en.numista.com"
        self.coins_data = []
    
    async def scrape_coins(self) -> List[Dict]:
        """Scrape les données des pièces de 2 euros commémoratives"""
        # Pour ce MVP, nous allons créer une base de données manuelle
        # avec les principales pièces de 2 euros commémoratives
        coins = await self.get_initial_coin_data()
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
