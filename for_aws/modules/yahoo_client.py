import os
import time
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class YahooShoppingClient:
    BASE_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"

    def __init__(self, client_id: Optional[str] = None):
        # Priority: explicit arg > env var
        self.client_id = client_id or os.getenv("YAHOO_CLIENT_ID")
        if not self.client_id:
            raise ValueError("YAHOO_CLIENT_ID not found in environment or .env file")

    def search_items(
        self, 
        query: str, 
        min_price: Optional[int] = None, 
        max_price: Optional[int] = None,
        results: int = 20,
        max_retries: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches for items on Yahoo! Shopping.
        Adheres to the 1 QPS rate limit by sleeping before the request.
        Uses exponential backoff for 429 errors.
        """
        params = {
            "appid": self.client_id,
            "query": query,
            "results": results,
            "in_stock": "true", # Only items in stock
        }

        if min_price is not None:
            params["price_from"] = min_price
        if max_price is not None:
            params["price_to"] = max_price

        for attempt in range(max_retries):
            # Base rate limiting: 1 QPS
            time.sleep(1)
            
            response = requests.get(self.BASE_URL, params=params)
            
            if response.status_code == 429:
                wait_time = (2 ** attempt) + 1 # Exponential backoff: 2, 3, 5, 9, 17...
                print(f"Rate limit hit (429). Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            
            try:
                response.raise_for_status()
                data = response.json()
                return data.get("hits", [])
            except requests.exceptions.HTTPError as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"HTTP Error: {e}. Retrying...")
                time.sleep(2)

        return []

if __name__ == "__main__":
    # Quick manual test
    try:
        client = YahooShoppingClient()
        test_queries = ["Chateau Tour Saint Bonnet", "トゥール サン ボネ"]
        
        for query in test_queries:
            print(f"\nSearching for: {query}...")
            items = client.search_items(query, min_price=1000, max_price=15000)
            
            print(f"Found {len(items)} items.")
            for item in items[:3]:
                print(f"- {item.get('name')} : {item.get('price')} JPY")
                print(f"  URL: {item.get('url')}")
    except Exception as e:
        print(f"Error: {e}")
