import json
import requests
from bs4 import BeautifulSoup

def get_text_from_url(url):
    try:
        request_header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding":"gzip, deflate, br, zstd",
            "accept-language":"en-US,en;q=0.9",
            "cache-control":"max-age=0",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        response = requests.get(url, headers=request_header)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(strip=True) # Extracts and cleans all text from the HTML
        return text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""