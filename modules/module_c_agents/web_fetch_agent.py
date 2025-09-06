"""
Web Fetch Agent for Module C
Extends existing agent system with web intelligence capabilities
"""

import asyncio
import aiohttp
import requests
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)

class WebFetchAgent:
    """Agent for fetching relevant documentation from the web"""
    
    def __init__(self):
        self.rag_url = "http://localhost:8002"
        self.allowed_domains = [
            "wiki.archlinux.org",
            "help.ubuntu.com", 
            "stackoverflow.com",
            "man7.org"
        ]
        self.rate_limit = 2.0  # seconds between requests
        self.last_request_time = {}
        
    def is_domain_allowed(self, url: str) -> bool:
        """Check if domain is in whitelist"""
        domain = urlparse(url).netloc.lower()
        return any(allowed in domain for allowed in self.allowed_domains)
    
    def respect_rate_limit(self, domain: str) -> bool:
        """Check and enforce rate limiting"""
        current_time = time.time()
        last_time = self.last_request_time.get(domain, 0)
        
        if current_time - last_time < self.rate_limit:
            return False
            
        self.last_request_time[domain] = current_time
        return True
    
    async def search_arch_wiki(self, query: str) -> List[Dict]:
        """Search Arch Wiki for relevant pages"""
        try:
            search_url = f"https://wiki.archlinux.org/api.php?action=opensearch&search={query}&limit=3&format=json"
            
            domain = "wiki.archlinux.org"
            if not self.respect_rate_limit(domain):
                await asyncio.sleep(self.rate_limit)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        if len(data) >= 4:
                            titles = data[1]
                            descriptions = data[2] 
                            urls = data[3]
                            
                            for title, desc, url in zip(titles[:2], descriptions[:2], urls[:2]):
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "description": desc,
                                    "source_type": "arch_wiki"
                                })
                        
                        return results
        except Exception as e:
            logger.error(f"Arch Wiki search failed: {e}")
            return []
    
    async def fetch_arch_wiki_content(self, url: str) -> Optional[str]:
        """Fetch content from Arch Wiki page"""
        try:
            if not self.is_domain_allowed(url):
                return None
                
            # Convert to raw content URL
            page_title = url.split("/")[-1]
            raw_url = f"https://wiki.archlinux.org/title/{page_title}?action=raw"
            
            domain = "wiki.archlinux.org"
            if not self.respect_rate_limit(domain):
                await asyncio.sleep(self.rate_limit)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(raw_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Basic cleanup of wiki markup
                        cleaned = self.clean_wiki_content(content)
                        return cleaned[:5000]  # Limit content size
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def clean_wiki_content(self, content: str) -> str:
        """Clean wiki markup from content"""
        import re
        
        # Remove templates and complex markup
        content = re.sub(r'\{\{[^}]*\}\}', '', content)
        content = re.sub(r'\[\[([^|\]]*)\|([^\]]*)\]\]', r'\2', content)
        content = re.sub(r'\[\[([^\]]*)\]\]', r'\1', content)
        content = re.sub(r'==+\s*([^=]*)\s*==+', r'\n\1\n', content)
        content = re.sub(r'^\*\s*', '• ', content, flags=re.MULTILINE)
        
        return content.strip()
    
    async def search_stackoverflow(self, query: str) -> List[Dict]:
        """Search Stack Overflow using their API"""
        try:
            api_url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "order": "desc",
                "sort": "relevance", 
                "q": query,
                "site": "stackoverflow",
                "tagged": "linux;bash",
                "pagesize": 2
            }
            
            domain = "stackoverflow.com"
            if not self.respect_rate_limit(domain):
                await asyncio.sleep(self.rate_limit)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get("items", []):
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("link", ""),
                                "score": item.get("score", 0),
                                "source_type": "stackoverflow",
                                "question_id": item.get("question_id")
                            })
                        
                        return results
        except Exception as e:
            logger.error(f"Stack Overflow search failed: {e}")
            return []
    
    async def upload_to_rag(self, content: str, title: str, url: str, source_type: str) -> bool:
        """Upload fetched content to RAG system"""
        try:
            # Create unique filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"web_{source_type}_{url_hash}.txt"
            
            # Format content with metadata
            formatted_content = f"""Source: {url}
Title: {title}
Type: {source_type}
Fetched: {time.ctime()}

{content}
"""
            
            files = {'files': (filename, formatted_content, 'text/plain')}
            response = requests.post(f"{self.rag_url}/upload", files=files, timeout=30)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to upload to RAG: {e}")
            return False
    
    async def execute_web_fetch(self, query: str, max_sources: int = 3) -> Dict:
        """Main execution method for web fetching task"""
        logger.info(f"Starting web fetch for query: {query}")
        
        results = {
            "query": query,
            "sources_found": 0,
            "sources_uploaded": 0,
            "sources": [],
            "errors": []
        }
        
        try:
            # Search multiple sources
            arch_results = await self.search_arch_wiki(query)
            so_results = await self.search_stackoverflow(query)
            
            all_sources = arch_results + so_results
            
            # Process results
            for source in all_sources[:max_sources]:
                try:
                    content = None
                    
                    if source["source_type"] == "arch_wiki":
                        content = await self.fetch_arch_wiki_content(source["url"])
                    
                    if content:
                        # Upload to RAG system
                        uploaded = await self.upload_to_rag(
                            content, 
                            source["title"], 
                            source["url"], 
                            source["source_type"]
                        )
                        
                        if uploaded:
                            results["sources_uploaded"] += 1
                            logger.info(f"Uploaded: {source['title']}")
                        
                        results["sources"].append({
                            "title": source["title"],
                            "url": source["url"],
                            "type": source["source_type"],
                            "uploaded": uploaded
                        })
                        
                except Exception as e:
                    error_msg = f"Error processing {source.get('title', 'unknown')}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            results["sources_found"] = len(all_sources)
            
        except Exception as e:
            error_msg = f"Web fetch execution failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results