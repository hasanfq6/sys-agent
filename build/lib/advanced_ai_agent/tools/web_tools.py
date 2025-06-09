"""
Web-related tools for searching, downloading, and web scraping.
"""

import requests
import json
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, Optional
from .base_tools import BaseTool

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class WebSearchTool(BaseTool):
    """Tool for web searching using DuckDuckGo."""
    
    def get_name(self) -> str:
        return "search_web"
    
    def get_description(self) -> str:
        return "Search the web using DuckDuckGo"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 5)",
                "required": False,
                "default": 5
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        query = kwargs["query"]
        max_results = kwargs.get("max_results", 5)
        
        try:
            self.log(f"Searching web for: {query}")
            
            # Use DuckDuckGo HTML interface
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if not HAS_BS4:
                return "BeautifulSoup4 is required for web search. Install with: pip install beautifulsoup4"
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract search results
            results = []
            result_elements = soup.select(".result")[:max_results]
            
            for element in result_elements:
                title_elem = element.select_one(".result__title a")
                snippet_elem = element.select_one(".result__snippet")
                url_elem = element.select_one(".result__url")
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    url = url_elem.get_text(strip=True) if url_elem else "N/A"
                    
                    results.append(f"🔗 **{title}**\n   {url}\n   {snippet}\n")
            
            if not results:
                return f"No search results found for: {query}"
            
            header = f"Web search results for '{query}':\n" + "=" * 50 + "\n"
            return header + "\n".join(results)
            
        except requests.RequestException as e:
            return f"Web search failed: {str(e)}"
        except Exception as e:
            return f"Error during web search: {str(e)}"


class WebScrapeTool(BaseTool):
    """Tool for scraping web pages."""
    
    def get_name(self) -> str:
        return "scrape_web"
    
    def get_description(self) -> str:
        return "Scrape content from a web page"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "URL to scrape",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "CSS selector to extract specific content (optional)",
                "required": False
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum content length (default: 2000)",
                "required": False,
                "default": 2000
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        url = kwargs["url"]
        selector = kwargs.get("selector")
        max_length = kwargs.get("max_length", 2000)
        
        try:
            self.log(f"Scraping: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            if not HAS_BS4:
                # Return raw text if BeautifulSoup is not available
                content = response.text[:max_length]
                return f"Raw content from {url}:\n{content}"
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            if selector:
                # Extract specific content using CSS selector
                elements = soup.select(selector)
                if elements:
                    content = "\n".join([elem.get_text(strip=True) for elem in elements])
                else:
                    content = f"No content found for selector: {selector}"
            else:
                # Extract all text content
                content = soup.get_text(separator="\n", strip=True)
            
            # Truncate if too long
            if len(content) > max_length:
                content = content[:max_length] + "... (truncated)"
            
            header = f"Content from {url}:\n" + "=" * 50 + "\n"
            return header + content
            
        except requests.RequestException as e:
            return f"Failed to fetch {url}: {str(e)}"
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"


class DownloadFileTool(BaseTool):
    """Tool for downloading files from URLs."""
    
    def get_name(self) -> str:
        return "download_file"
    
    def get_description(self) -> str:
        return "Download a file from a URL"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "URL to download from",
                "required": True
            },
            "filename": {
                "type": "string",
                "description": "Local filename to save as (optional)",
                "required": False
            },
            "max_size": {
                "type": "integer",
                "description": "Maximum file size in MB (default: 50)",
                "required": False,
                "default": 50
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        url = kwargs["url"]
        filename = kwargs.get("filename")
        max_size = kwargs.get("max_size", 50) * 1024 * 1024  # Convert to bytes
        
        try:
            self.log(f"Downloading: {url}")
            
            # If no filename provided, extract from URL
            if not filename:
                parsed_url = urlparse(url)
                filename = parsed_url.path.split('/')[-1]
                if not filename or '.' not in filename:
                    filename = "downloaded_file"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Stream download to handle large files
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > max_size:
                return f"File too large ({int(content_length) / 1024 / 1024:.1f}MB). Max allowed: {max_size / 1024 / 1024}MB"
            
            # Download file
            downloaded_size = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Check size limit during download
                        if downloaded_size > max_size:
                            f.close()
                            import os
                            os.remove(filename)
                            return f"Download cancelled: file exceeded size limit ({max_size / 1024 / 1024}MB)"
            
            file_size_mb = downloaded_size / 1024 / 1024
            return f"✅ Downloaded {url} to {filename} ({file_size_mb:.2f}MB)"
            
        except requests.RequestException as e:
            return f"Download failed: {str(e)}"
        except Exception as e:
            return f"Error downloading file: {str(e)}"


class APIRequestTool(BaseTool):
    """Tool for making HTTP API requests."""
    
    def get_name(self) -> str:
        return "api_request"
    
    def get_description(self) -> str:
        return "Make HTTP API requests (GET, POST, PUT, DELETE)"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "API endpoint URL",
                "required": True
            },
            "method": {
                "type": "string",
                "description": "HTTP method (GET, POST, PUT, DELETE)",
                "required": False,
                "default": "GET"
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers as JSON object",
                "required": False
            },
            "data": {
                "type": "object",
                "description": "Request data as JSON object",
                "required": False
            },
            "params": {
                "type": "object",
                "description": "URL parameters as JSON object",
                "required": False
            }
        }
    
    def execute(self, **kwargs) -> str:
        self.validate_parameters(**kwargs)
        
        url = kwargs["url"]
        method = kwargs.get("method", "GET").upper()
        headers = kwargs.get("headers", {})
        data = kwargs.get("data")
        params = kwargs.get("params")
        
        try:
            self.log(f"Making {method} request to: {url}")
            
            # Prepare request arguments
            request_kwargs = {
                "timeout": 15,
                "headers": headers
            }
            
            if params:
                request_kwargs["params"] = params
            
            if data and method in ["POST", "PUT", "PATCH"]:
                if isinstance(data, dict):
                    request_kwargs["json"] = data
                    headers.setdefault("Content-Type", "application/json")
                else:
                    request_kwargs["data"] = data
            
            # Make request
            response = requests.request(method, url, **request_kwargs)
            
            # Prepare response info
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url
            }
            
            # Try to parse JSON response
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text[:1000]  # Truncate long text responses
            
            # Format output
            output = f"API Response from {method} {url}:\n"
            output += f"Status: {response.status_code}\n"
            output += f"Content-Type: {response.headers.get('content-type', 'N/A')}\n"
            output += "=" * 50 + "\n"
            
            if isinstance(result["data"], dict):
                output += json.dumps(result["data"], indent=2)
            else:
                output += str(result["data"])
            
            return output
            
        except requests.RequestException as e:
            return f"API request failed: {str(e)}"
        except Exception as e:
            return f"Error making API request: {str(e)}"