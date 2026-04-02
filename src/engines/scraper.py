import asyncio
import aiohttp
import re
import json
import random
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from ..utils.mahwous_logging import get_logger

_logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
]

class AsyncScraper:
    """محرك الكشط المطور V27.2 - النسخة المصفحة (Hardened Anti-Block)"""
    
    def __init__(self, concurrency=10, safe_mode=False):
        self.concurrency = 1 if safe_mode else concurrency
        self.safe_mode = safe_mode
        self.headers = self._get_random_headers()

    def _get_random_headers(self, url=""):
        """توليد ترويسات متصفح Chrome 124 حقيقية"""
        domain = urlparse(url).netloc if url else ""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Referer": f"https://{domain}/" if domain else "https://www.google.com/"
        }

    async def fetch(self, session, url, retries=3):
        """جلب محتوى الرابط مع التعامل المتقدم مع Cloudflare 1015/403"""
        for i in range(retries):
            try:
                # إضافة تأخير عشوائي (Jitter) لتجنب الاكتشاف
                if self.safe_mode:
                    await asyncio.sleep(random.uniform(3.0, 7.0)) # زيادة التأخير في V27.2
                else:
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                async with session.get(url, headers=self._get_random_headers(url), timeout=30) as response:
                    text = await response.text()
                    
                    if response.status == 200:
                        # كشف حجب Cloudflare النصي الكامن
                        if any(x in text.lower() for x in ["cloudflare", "ray id", "security check", "captcha", "1015"]):
                            _logger.warning(f"Cloudflare block detected on {url}. Waiting 20s...")
                            await asyncio.sleep(20)
                            continue
                        return text
                    
                    elif response.status in [403, 429, 1015]:
                        wait_time = (i + 1) * 30
                        _logger.warning(f"Blocked/Rate limited ({response.status}) on {url}. Waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    elif response.status == 404:
                        _logger.error(f"Not Found 404: {url}")
                        return None
                    else:
                        _logger.warning(f"Attempt {i+1} failed for {url}: {response.status}")
            except Exception as e:
                _logger.error(f"Error fetching {url}: {e}")
            
        return None

    async def resolve_sitemap(self, store_url):
        """محاولة إيجاد خريطة الموقع تلقائياً عبر مسارات سلة والمسارات القياسية"""
        parsed = urlparse(store_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        candidates = [
            urljoin(base, "sitemap_products_1.xml"), # سلة - المنتجات دائماً هنا
            urljoin(base, "sitemap.xml"),
            urljoin(base, "sitemap_index.xml"),
            urljoin(base, "robots.txt")
        ]
        
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            for url in candidates:
                content = await self.fetch(session, url)
                if content and ("urlset" in content or "sitemapindex" in content):
                    _logger.info(f"Sitemap resolved: {url}")
                    return url
                if "robots.txt" in url and content:
                    for line in content.splitlines():
                        if line.lower().startswith("sitemap:"):
                            return line.split(":", 1)[1].strip()
        return None

    async def get_urls_from_sitemap(self, sitemap_url):
        """استخراج كافة الروابط من خريطة الموقع مع دعم الـ Namespaces"""
        urls = []
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            content = await self.fetch(session, sitemap_url)
            if not content: return []
            
            # محاولة الاستخراج باستخدام Regex (أكثر مرونة مع Namespaces)
            urls = re.findall(r'<loc>(https?://[^<]+)</loc>', content)
            
            # إذا لم تنجح الـ Regex، نجرب BeautifulSoup
            if not urls:
                soup = BeautifulSoup(content, 'xml')
                urls = [loc.text for loc in soup.find_all('loc') if loc.text]
                
            # تحقق مما إذا كان فهرس خرائط (Sitemap Index)
            if any(x in content.lower() for x in ["sitemapindex", "sitemap_index"]):
                sub_urls = []
                for sub_loc in urls:
                    if any(x in sub_loc.lower() for x in ["product", "item", "page"]):
                        _logger.info(f"Navigating sub-sitemap: {sub_loc}")
                        sub_content = await self.fetch(session, sub_loc)
                        if sub_content:
                            sub_urls.extend(re.findall(r'<loc>(https?://[^<]+)</loc>', sub_content))
                urls = sub_urls

        # تصفية الروابط لضمان أنها للمنتجات (تحسين لمتأجر سلة وزد)
        product_urls = [u for u in urls if any(x in u.lower() for x in ["/products/", "/p/", "/item/", "/details/"])]
        
        if not product_urls:
            product_urls = [u for u in urls if not any(x in u.lower() for x in [".jpg", ".png", ".webp", "/category/", "/tags/", "/blog/"])]
            
        return list(set(product_urls))

    def extract_json_ld(self, html):
        """استخراج بيانات المنتج من JSON-LD"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") in ["Product", "http://schema.org/Product"]:
                            offers = item.get("offers", {})
                            if isinstance(offers, list): offers = offers[0]
                            
                            return {
                                "name": item.get("name"),
                                "price": offers.get("price") or item.get("price"),
                                "brand": item.get("brand", {}).get("name") if isinstance(item.get("brand"), dict) else item.get("brand"),
                                "barcode": item.get("sku") or item.get("gtin13") or item.get("gtin8") or item.get("mpn"),
                                "image": str(item.get("image", ""))
                            }
                except: continue
        except Exception as e:
            _logger.error(f"Error extracting JSON-LD: {e}")
        return None

    async def scrape_products(self, product_urls, progress_callback=None):
        """كشط روابط المنتجات مع التحكم في التوازي والتأخر"""
        results = []
        total = len(product_urls)
        
        # استخدام CookieJar واحد لكافة الجلسة لمحاكاة تصفح حقيقي
        connector = aiohttp.TCPConnector(limit_per_host=self.concurrency)
        async with aiohttp.ClientSession(connector=connector, cookie_jar=aiohttp.CookieJar()) as session:
            semaphore = asyncio.Semaphore(self.concurrency)
            
            async def bounded_fetch(url):
                async with semaphore:
                    html = await self.fetch(session, url)
                    if html:
                        data = self.extract_json_ld(html)
                        if data:
                            data['url'] = url
                            return data
                return None

            tasks = [bounded_fetch(url) for url in product_urls]
            done_count = 0
            for task in asyncio.as_completed(tasks):
                res = await task
                done_count += 1
                if res: results.append(res)
                if progress_callback:
                    progress_callback(done_count / total)
                    
        return results
