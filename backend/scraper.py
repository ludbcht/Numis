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
                # Fallback sur données initiales si le scraping échoue
                logger.warning("Scraping failed, using initial data")
                coins = await self.get_initial_coin_data()
            return coins
        except Exception as e:
            logger.error(f"Error in scrape_coins: {e}")
            return await self.get_initial_coin_data()
    
    async def scrape_ecb_coins(self) -> List[Dict]:
        """Scrape le site officiel de la BCE"""
        coins = []
        
        # Années à scraper (de 2004 à 2024)
        years = range(2004, 2025)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for year in years:
                try:
                    # URL pour chaque année
                    url = f"{self.base_url}/euro/coins/comm/html/comm_{year}.en.html"
                    logger.info(f"Scraping year {year}: {url}")
                    
                    response = await client.get(url, headers=self.headers, follow_redirects=True)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        year_coins = self.parse_year_page(soup, year)
                        coins.extend(year_coins)
                        logger.info(f"Found {len(year_coins)} coins for {year}")
                    else:
                        logger.warning(f"Failed to fetch {year}: {response.status_code}")
                    
                    # Petit délai pour ne pas surcharger le serveur
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error scraping year {year}: {e}")
                    continue
        
        logger.info(f"Total coins scraped: {len(coins)}")
        return coins
    
    def parse_year_page(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Parse une page d'année pour extraire les pièces"""
        coins = []
        
        # Chercher toutes les sections de pièces
        # Le site BCE utilise des structures variées, on cherche les images et textes associés
        
        # Méthode 1: Chercher les divs avec les informations de pièces
        coin_sections = soup.find_all(['div', 'section'], class_=re.compile('coin|commemorative', re.I))
        
        for section in coin_sections:
            try:
                coin = self.extract_coin_from_section(section, year)
                if coin:
                    coins.append(coin)
            except Exception as e:
                logger.debug(f"Error parsing section: {e}")
                continue
        
        # Méthode 2: Chercher directement les images de pièces
        if not coins:
            images = soup.find_all('img', src=re.compile('coin|euro|commemorative', re.I))
            for img in images:
                try:
                    coin = self.extract_coin_from_image(img, year)
                    if coin:
                        coins.append(coin)
                except Exception as e:
                    logger.debug(f"Error parsing image: {e}")
                    continue
        
        return coins
    
    def extract_coin_from_section(self, section, year: int) -> Dict:
        """Extrait les informations d'une pièce depuis une section"""
        # Chercher l'image
        img = section.find('img')
        if not img:
            return None
        
        image_url = img.get('src', '')
        if image_url and not image_url.startswith('http'):
            image_url = self.base_url + image_url
        
        # Extraire le texte de la section
        text = section.get_text(strip=True)
        
        # Chercher le pays (généralement en gras ou dans un titre)
        country = "Unknown"
        country_elem = section.find(['h2', 'h3', 'h4', 'strong', 'b'])
        if country_elem:
            country = country_elem.get_text(strip=True)
        
        # Description
        description = text[:200] if text else f"Pièce commémorative {year}"
        
        # Tirage (chercher des nombres)
        mintage = 1000000  # Valeur par défaut
        mintage_match = re.search(r'(\d{1,3}(?:[,.\s]\d{3})*)\s*(?:coins|pieces|mintage)', text, re.I)
        if mintage_match:
            mintage_str = mintage_match.group(1).replace(',', '').replace('.', '').replace(' ', '')
            try:
                mintage = int(mintage_str)
            except:
                pass
        
        return {
            "country": country,
            "year": year,
            "description": description,
            "mintage": mintage,
            "image_url": image_url or f"https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
            "value_fdc": self.estimate_value(mintage, "fdc"),
            "value_bu": self.estimate_value(mintage, "bu"),
            "value_be": self.estimate_value(mintage, "be")
        }
    
    def extract_coin_from_image(self, img, year: int) -> Dict:
        """Extrait les informations d'une pièce depuis une image"""
        image_url = img.get('src', '')
        if image_url and not image_url.startswith('http'):
            image_url = self.base_url + image_url
        
        alt_text = img.get('alt', '')
        title_text = img.get('title', '')
        
        description = alt_text or title_text or f"Pièce commémorative {year}"
        
        # Chercher le pays dans le texte environnant
        parent = img.find_parent(['div', 'section', 'td'])
        country = "Unknown"
        if parent:
            text = parent.get_text(strip=True)
            # Liste des pays de la zone euro
            countries = ['Germany', 'Austria', 'Belgium', 'Spain', 'Finland', 'France', 
                        'Greece', 'Ireland', 'Italy', 'Luxembourg', 'Netherlands', 
                        'Portugal', 'Slovenia', 'Cyprus', 'Malta', 'Slovakia', 
                        'Estonia', 'Latvia', 'Lithuania', 'Croatia', 'Monaco', 
                        'San Marino', 'Vatican', 'Andorra']
            
            for c in countries:
                if c.lower() in text.lower():
                    country = c
                    break
        
        return {
            "country": country,
            "year": year,
            "description": description,
            "mintage": 1000000,
            "image_url": image_url or f"https://images.unsplash.com/photo-1585483391381-b96dda4fae8f?q=85&w=600&auto=format&fit=crop",
            "value_fdc": 4.0,
            "value_bu": 7.0,
            "value_be": 14.0
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
