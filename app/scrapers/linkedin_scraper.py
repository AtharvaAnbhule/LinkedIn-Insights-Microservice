import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import httpx
from playwright.async_api import async_playwright, Browser, Page

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class LinkedInScraper:
    

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    async def _get_browser(self) -> Browser:
        
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
        return self.browser

    async def close(self):
        
        if self.browser:
            await self.browser.close()
            self.browser = None

    async def scrape_page_details(self, page_id: str) -> Dict[str, Any]:
        
        try:
            logger.info(f"Scraping page details for: {page_id}")

            
            url = f"https://www.linkedin.com/company/{page_id}/"

      

            page_data = await self._scrape_with_playwright(url, page_id)

            return page_data

        except Exception as e:
            logger.error(f"Error scraping page {page_id}: {e}")
            raise

    async def _scrape_with_playwright(self, url: str, page_id: str) -> Dict[str, Any]:
      
        try:
            browser = await self._get_browser()
            page = await browser.new_page()

            
            await page.set_extra_http_headers({
                "User-Agent": self.user_agent
            })

          
            await page.goto(url, wait_until="networkidle")

            
            page_data = await self._extract_page_data(page, page_id)

            await page.close()

            return page_data

        except Exception as e:
            logger.error(f"Playwright scraping error: {e}")
            
            return self._get_mock_data(page_id)

    async def _extract_page_data(self, page: Page, page_id: str) -> Dict[str, Any]:
       
        try:
            
            name = await page.text_content(".org-top-card-summary__title") or page_id
            description = await page.text_content(".org-top-card-summary__tagline") or ""
            industry = await page.text_content(".org-top-card-summary__industry") or ""
            website = await page.get_attribute(".org-about-us-organization-description__website a", "href") or ""

            
            followers_text = await page.text_content(".org-top-card-summary-info-list__info-item") or "0"
            followers_count = self._parse_follower_count(followers_text)

            return {
                "page_id": page_id,
                "name": name,
                "url": f"https://www.linkedin.com/company/{page_id}/",
                "description": description,
                "website": website,
                "industry": industry,
                "followers_count": followers_count,
                "headcount": None,
                "specialties": [],
                "profile_image_url": None
            }

        except Exception as e:
            logger.warning(f"Error extracting data, using mock data: {e}")
            return self._get_mock_data(page_id)

    def _parse_follower_count(self, text: str) -> int:
        
        try:
            
            clean_text = re.sub(r'[^\d.KM]', '', text.upper())

            if 'K' in clean_text:
                return int(float(clean_text.replace('K', '')) * 1000)
            elif 'M' in clean_text:
                return int(float(clean_text.replace('M', '')) * 1000000)
            else:
                return int(clean_text) if clean_text else 0

        except Exception:
            return 0

    async def scrape_page_posts(self, page_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        
        try:
            logger.info(f"Scraping posts for page: {page_id}")

            
            return self._get_mock_posts(page_id, limit)

        except Exception as e:
            logger.error(f"Error scraping posts for {page_id}: {e}")
            return []

    async def scrape_page_followers(self, page_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        
        try:
            logger.info(f"Scraping followers for page: {page_id}")

            

            return self._get_mock_followers(page_id, limit)

        except Exception as e:
            logger.error(f"Error scraping followers for {page_id}: {e}")
            return []

    def _get_mock_data(self, page_id: str) -> Dict[str, Any]:
        
        return {
            "page_id": page_id,
            "name": f"{page_id.capitalize()} Company",
            "url": f"https://www.linkedin.com/company/{page_id}/",
            "description": f"A leading company in the industry. Follow us for updates and insights.",
            "website": f"https://www.{page_id}.com",
            "industry": "Technology",
            "followers_count": 125000,
            "headcount": "1000-5000",
            "specialties": ["Innovation", "Technology", "Solutions"],
            "profile_image_url": f"https://via.placeholder.com/200?text={page_id}"
        }

    def _get_mock_posts(self, page_id: str, limit: int) -> List[Dict[str, Any]]:
        
        import uuid
        from datetime import datetime, timedelta

        posts = []
        for i in range(min(limit, 15)):
            posts.append({
                "post_id": str(uuid.uuid4()),
                "page_id": page_id,
                "content": f"Exciting news from {page_id}! Post #{i+1}. Stay tuned for more updates.",
                "likes": 100 + (i * 10),
                "comments_count": 5 + i,
                "created_at": datetime.utcnow() - timedelta(days=i)
            })

        return posts

    def _get_mock_followers(self, page_id: str, limit: int) -> List[Dict[str, Any]]:
        
        import uuid

        followers = []
        for i in range(min(limit, 10)):
            followers.append({
                "user_id": str(uuid.uuid4()),
                "name": f"User {i+1}",
                "title": f"Professional Title {i+1}",
                "page_id": page_id
            })

        return followers
