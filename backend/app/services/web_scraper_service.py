import httpx
import asyncio
from bs4 import BeautifulSoup
import re
from ..utils.logger import Logger

logger = Logger()

class WebScraperService:
    def __init__(self):
        # Timeout tối đa cho mỗi request
        self.timeout = 10.0
        # Số lượng URL tối đa để scrape
        self.max_urls = 3
        # Giới hạn ký tự cho mỗi URL (300 ký tự)
        self.max_chars_per_url = 300
        # Số ký tự trung bình cho một token (ước lượng)
        self.chars_per_token = 4

    async def scrape_urls(self, urls):
        """
        Scrape nội dung từ nhiều URL cùng một lúc
        
        Args:
            urls (list): Danh sách các URLs để scrape
            
        Returns:
            list: Danh sách kết quả scraping {url, title, content}
        """
        if not urls:
            return []
            
        # Giới hạn số lượng URL để scrape (tránh quá tải)
        urls_to_scrape = urls[:min(len(urls), self.max_urls)]
        logger.log_with_timestamp('WEB_SCRAPER', f'Scraping {len(urls_to_scrape)} URLs')
        
        # Scrape các URLs đồng thời
        tasks = [self.scrape_url(url) for url in urls_to_scrape]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Lọc kết quả và loại bỏ các lỗi
        scraped_contents = []
        for result in results:
            if isinstance(result, dict) and 'content' in result and result['content']:
                scraped_contents.append(result)
                logger.log_with_timestamp('SCRAPER_SUCCESS', f'Successfully scraped: {result["url"][:50]}')
            elif isinstance(result, Exception):
                logger.log_with_timestamp('SCRAPER_ERROR', f'Error: {str(result)}')
                
        return scraped_contents

    async def scrape_url(self, url):
        """
        Scrape nội dung từ một URL
        
        Args:
            url (str): URL để scrape
            
        Returns:
            dict: Thông tin đã scrape {url, title, content}
        """
        try:
            logger.log_with_timestamp('SCRAPER', f'Scraping URL: {url[:50]}')
            
            # Tạo headers để giả lập trình duyệt (tránh bị block)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # Thực hiện request với timeout
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                # Kiểm tra response status
                if response.status_code != 200:
                    logger.log_with_timestamp('SCRAPER_ERROR', f'HTTP Error: {response.status_code} for {url}')
                    return {'url': url, 'title': '', 'content': ''}
                
                # Parse HTML
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Trích xuất title
                title = self._extract_title(soup)
                
                # Trích xuất nội dung chính
                content = self._extract_relevant_content(soup)
                
                # Làm sạch nội dung và giới hạn ở 300 ký tự
                cleaned_content = self._clean_and_limit_content(content)
                
                return {
                    'url': url,
                    'title': title,
                    'content': cleaned_content
                }
                
        except Exception as e:
            logger.log_with_timestamp('SCRAPER_ERROR', f'Error scraping {url}: {str(e)}')
            return {'url': url, 'title': '', 'content': ''}
            
    def _extract_title(self, soup):
        """Trích xuất tiêu đề từ trang web"""
        if soup.title:
            return soup.title.text.strip()
        return ''
        
    def _extract_relevant_content(self, soup):
        """Trích xuất nội dung có ý nghĩa và phù hợp nhất từ trang web"""
        # Loại bỏ các phần không liên quan
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'form']):
            tag.decompose()
            
        # Ưu tiên nội dung từ các thẻ article hoặc main
        main_content = soup.find(['article', 'main', 'div[role="main"]', '[class*="content"]', '[id*="content"]'])
        
        if main_content:
            # Lấy các đoạn văn từ phần nội dung chính
            paragraphs = main_content.find_all('p')
            if paragraphs:
                # Lọc và sắp xếp các đoạn văn có nội dung có ý nghĩa (độ dài > 20 ký tự)
                meaningful_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                return '\n\n'.join(meaningful_paragraphs)
            else:
                # Nếu không tìm thấy thẻ p, lấy toàn bộ text từ nội dung chính
                return main_content.get_text(separator='\n\n', strip=True)
        else:
            # Nếu không tìm thấy phần chính, lấy các đoạn văn có ý nghĩa
            paragraphs = soup.find_all('p')
            meaningful_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
            return '\n\n'.join(meaningful_paragraphs)
            
    def _clean_and_limit_content(self, content):
        """Làm sạch nội dung văn bản và giới hạn ở 300 ký tự"""
        if not content:
            return ''
            
        # Loại bỏ nhiều khoảng trắng liên tiếp
        content = re.sub(r'\s+', ' ', content)
        
        # Loại bỏ các ký tự đặc biệt
        content = re.sub(r'[^\w\s.,;:?!()\'"-]', '', content)
        
        # Giới hạn chính xác 300 ký tự, đảm bảo không cắt giữa từ
        if len(content) > self.max_chars_per_url:
            # Tìm vị trí dấu cách gần nhất trước 300 ký tự
            cutoff = self.max_chars_per_url
            while cutoff > 0 and content[cutoff] != ' ':
                cutoff -= 1
                
            # Nếu không tìm thấy khoảng trắng, cắt tại 300 ký tự
            if cutoff == 0:
                cutoff = self.max_chars_per_url
                
            content = content[:cutoff] + "..."
        
        # Log số ký tự thực tế    
        logger.log_with_timestamp('CONTENT_SIZE', 
                               f'Content length: {len(content)} chars')
            
        return content.strip()
        
    def estimate_tokens(self, text):
        """Ước lượng số token cho một đoạn văn bản"""
        if not text:
            return 0
        # Ước lượng đơn giản: 1 token ~ 4 ký tự (trung bình)
        return len(text) // self.chars_per_token 