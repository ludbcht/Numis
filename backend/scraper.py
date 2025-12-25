import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict
import re
from scraper_2euros import TwoEurosScraper

logger = logging.getLogger(__name__)

class CoinScraper:
    """Web scraper pour les pièces de 2 euros commémoratives - combine BCE et 2euros.org"""
    
    def __init__(self):
        self.base_url_ecb = "https://www.ecb.europa.eu"
        self.coins_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_coins(self) -> List[Dict]:
        """Scrape les données des pièces depuis BCE et optionnellement 2euros.org"""
        try:
            logger.info("Starting scraping from ECB...")
            
            # Scraper la BCE pour les données officielles
            ecb_coins = await self.scrape_ecb_coins()
            logger.info(f"ECB scraping completed: {len(ecb_coins)} coins")
            
            if not ecb_coins:
                logger.warning("No coins found from ECB, using fallback data")
                return await self.get_initial_coin_data()
            
            # Tentative de scraper 2euros.org pour les données complémentaires (optionnel)
            try:
                logger.info("Attempting to scrape 2euros.org for additional data...")
                scraper_2euros = TwoEurosScraper()
                coins_2euros = await scraper_2euros.scrape_all_coins()
                logger.info(f"2euros.org scraping completed: {len(coins_2euros)} coins")
                
                if coins_2euros:
                    # Fusionner les données si disponibles
                    merged_coins = self.merge_coin_data(ecb_coins, coins_2euros)
                    logger.info(f"Merged with 2euros.org data: {len(merged_coins)} total coins")
                    return merged_coins
            except Exception as e:
                logger.warning(f"Could not scrape 2euros.org (optional): {e}")
            
            # Retourner les données BCE
            return ecb_coins
            
        except Exception as e:
            logger.error(f"Error in scrape_coins: {e}")
            return await self.get_initial_coin_data()
    
    def merge_coin_data(self, ecb_coins: List[Dict], coins_2euros: List[Dict]) -> List[Dict]:
        """Fusionne les données de la BCE et 2euros.org"""
        merged = []
        
        # Créer un index des pièces 2euros par pays+année
        euros_index = {}
        for coin in coins_2euros:
            key = f"{coin['country'].lower().strip()}_{coin['year']}"
            if key not in euros_index:
                euros_index[key] = []
            euros_index[key].append(coin)
        
        # Fusionner avec les données ECB (priorité aux données ECB pour description et tirage)
        for ecb_coin in ecb_coins:
            country_normalized = ecb_coin['country'].lower().strip()
            key = f"{country_normalized}_{ecb_coin['year']}"
            
            # Chercher une correspondance dans 2euros.org
            match_found = False
            if key in euros_index and euros_index[key]:
                # Prendre la première correspondance
                euros_coin = euros_index[key].pop(0)
                
                # Fusionner: garder les meilleures données de chaque source
                merged_coin = {
                    "country": ecb_coin['country'],  # ECB pour consistance
                    "year": ecb_coin['year'],
                    "description": ecb_coin['description'],  # ECB plus détaillé
                    "mintage": ecb_coin['mintage'],  # ECB officiel
                    "image_url": euros_coin['image_url'] if euros_coin['image_url'] and 'unsplash' not in euros_coin['image_url'] else ecb_coin['image_url'],  # Préférer 2euros si disponible
                    "value_fdc": euros_coin['value_fdc'],  # Prix de 2euros.org
                    "value_bu": euros_coin['value_bu'],
                    "value_be": euros_coin['value_be']
                }
                merged.append(merged_coin)
                match_found = True
            
            # Si pas de correspondance, garder la pièce ECB
            if not match_found:
                merged.append(ecb_coin)
        
        # Ajouter les pièces restantes de 2euros.org qui n'étaient pas dans ECB
        for coins_list in euros_index.values():
            merged.extend(coins_list)
        
        return merged
    
    async def scrape_ecb_coins(self) -> List[Dict]:
        """Scrape le site officiel de la BCE"""
        coins = []
        
        # Années à scraper (de 2004 à 2024)
        years = range(2004, 2025)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for year in years:
                try:
                    url = f"{self.base_url_ecb}/euro/coins/comm/html/comm_{year}.en.html"
                    logger.info(f"Scraping ECB year {year}: {url}")
                    
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
                image_url = self.base_url + image_url
        
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
