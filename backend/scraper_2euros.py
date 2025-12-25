import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class TwoEurosScraper:
    """Web scraper pour 2euros.org - informations complémentaires et prix"""
    
    def __init__(self):
        self.base_url = "https://www.2euros.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_all_coins(self) -> List[Dict]:
        """Scrape toutes les pièces du site 2euros.org"""
        all_coins = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Liste des pays de la zone euro
                countries = [
                    'andorra', 'austria', 'belgium', 'croatia', 'cyprus', 'estonia',
                    'finland', 'france', 'germany', 'greece', 'ireland', 'italy',
                    'latvia', 'lithuania', 'luxembourg', 'malta', 'monaco',
                    'netherlands', 'portugal', 'san-marino', 'slovakia', 'slovenia',
                    'spain', 'vatican'
                ]
                
                for country in countries:
                    try:
                        # URL des pièces commémoratives par pays
                        url = f"{self.base_url}/en/{country}-2-euro-commemorative-coins/"
                        logger.info(f"Scraping {country}: {url}")
                        
                        response = await client.get(url, headers=self.headers)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            country_coins = self.parse_country_page(soup, country)
                            all_coins.extend(country_coins)
                            logger.info(f"Found {len(country_coins)} coins for {country}")
                        
                        # Délai pour respecter le serveur
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error scraping country {country}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Error in scrape_all_coins: {e}")
        
        logger.info(f"Total coins scraped from 2euros.org: {len(all_coins)}")
        return all_coins
    
    def parse_country_page(self, soup: BeautifulSoup, country: str) -> List[Dict]:
        """Parse une page de pays pour extraire les pièces"""
        coins = []
        
        # Chercher les articles ou divs contenant les pièces
        coin_articles = soup.find_all(['article', 'div'], class_=re.compile('coin|post|entry', re.I))
        
        for article in coin_articles:
            try:
                coin = self.extract_coin_from_article(article, country)
                if coin:
                    coins.append(coin)
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        # Si pas trouvé avec cette méthode, chercher les images de pièces
        if not coins:
            img_containers = soup.find_all(['div', 'figure', 'a'], class_=re.compile('coin|image|thumbnail', re.I))
            for container in img_containers:
                try:
                    coin = self.extract_coin_from_container(container, country)
                    if coin:
                        coins.append(coin)
                except Exception as e:
                    logger.debug(f"Error parsing container: {e}")
                    continue
        
        return coins
    
    def extract_coin_from_article(self, article, country: str) -> Optional[Dict]:
        """Extrait les informations d'une pièce depuis un article"""
        # Image
        img = article.find('img')
        if not img:
            return None
        
        image_url = img.get('src', '') or img.get('data-src', '')
        if image_url and not image_url.startswith('http'):
            image_url = self.base_url + image_url
        
        # Titre/Description
        title = ""
        title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # Année (chercher dans le titre ou le texte)
        year = None
        text = article.get_text()
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            year = int(year_match.group(1))
        
        if not year:
            return None
        
        # Tirage
        mintage = 1000000
        mintage_match = re.search(r'(?:mintage|tirage|tiragem)[:\s]+([0-9,.]+)', text, re.I)
        if mintage_match:
            mintage_str = mintage_match.group(1).replace(',', '').replace('.', '').strip()
            try:
                mintage = int(mintage_str)
            except:
                pass
        
        # Prix (chercher des valeurs en euros)
        prices = self.extract_prices(text)
        
        return {
            "country": country.replace('-', ' ').title(),
            "year": year,
            "description": title[:200] if title else f"Pièce commémorative {year}",
            "mintage": mintage,
            "image_url": image_url,
            "value_fdc": prices.get('fdc', self.estimate_value(mintage, "fdc")),
            "value_bu": prices.get('bu', self.estimate_value(mintage, "bu")),
            "value_be": prices.get('be', self.estimate_value(mintage, "be"))
        }
    
    def extract_coin_from_container(self, container, country: str) -> Optional[Dict]:
        """Extrait les informations d'une pièce depuis un conteneur"""
        img = container.find('img')
        if not img:
            return None
        
        image_url = img.get('src', '') or img.get('data-src', '')
        if image_url and not image_url.startswith('http'):
            image_url = self.base_url + image_url
        
        # Chercher le titre dans les éléments proches
        title = ""
        for elem in [container, container.parent, container.find_next_sibling()]:
            if elem:
                title_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'a', 'p'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        break
        
        # Année
        year = None
        if title:
            year_match = re.search(r'\b(20\d{2})\b', title)
            if year_match:
                year = int(year_match.group(1))
        
        if not year:
            return None
        
        return {
            "country": country.replace('-', ' ').title(),
            "year": year,
            "description": title[:200] if title else f"Pièce commémorative {year}",
            "mintage": 1000000,
            "image_url": image_url,
            "value_fdc": self.estimate_value(1000000, "fdc"),
            "value_bu": self.estimate_value(1000000, "bu"),
            "value_be": self.estimate_value(1000000, "be")
        }
    
    def extract_prices(self, text: str) -> Dict[str, float]:
        """Extrait les prix du texte"""
        prices = {}
        
        # Chercher des patterns de prix
        # Ex: "FDC: 5€", "BU 10 EUR", "BE: €15"
        fdc_match = re.search(r'FDC[:\s]+[€$]?([0-9,.]+)', text, re.I)
        if fdc_match:
            try:
                prices['fdc'] = float(fdc_match.group(1).replace(',', '.'))
            except:
                pass
        
        bu_match = re.search(r'BU[:\s]+[€$]?([0-9,.]+)', text, re.I)
        if bu_match:
            try:
                prices['bu'] = float(bu_match.group(1).replace(',', '.'))
            except:
                pass
        
        be_match = re.search(r'BE[:\s]+[€$]?([0-9,.]+)', text, re.I)
        if be_match:
            try:
                prices['be'] = float(be_match.group(1).replace(',', '.'))
            except:
                pass
        
        return prices
    
    def estimate_value(self, mintage: int, condition: str) -> float:
        """Estime la valeur d'une pièce selon son tirage et son état"""
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
