import os
import sys

# modulesをインポートできるようにパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.yahoo_client import YahooShoppingClient
from modules.data_manager import DataManager

def handler(event, context):
    """
    Collector Lambda Handler
    Triggered by EventBridge.
    Reads master CSV from S3, searches Yahoo! API, and saves JSON results to S3.
    """
    print(f"Collector started with event: {event}")
    
    classification = event.get("classification")
    min_price = event.get("min_price")
    max_price = event.get("max_price")

    try:
        yahoo_client = YahooShoppingClient()
        data_manager = DataManager()
        
        # S3からマスタデータを読み込んでタスクを生成
        tasks = data_manager.get_search_tasks(classification)
        results = []

        # 5件ずつに分割してYahoo! APIを叩く（OR検索）
        chunk_size = 5
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            combined_query = " | ".join([f'({t["query"]})' for t in chunk])
            
            hits = yahoo_client.search_items(
                query=combined_query,
                min_price=min_price,
                max_price=max_price,
                results=100
            )
            
            for task in chunk:
                search_query = task["query"].lower()
                matched_items = []
                for h in hits:
                    if search_query in h.get("name", "").lower():
                        matched_items.append({
                            "name": h.get("name"),
                            "price": h.get("price"),
                            "url": h.get("url"),
                            "store": h.get("seller", {}).get("name") or h.get("store", {}).get("name"),
                            "image": h.get("image", {}).get("medium"),
                            "review_rate": h.get("review", {}).get("rate"),
                            "in_stock": h.get("inStock"),
                            "code": h.get("code")
                        })
                
                results.append({
                    "chateau": task["original_name"],
                    "classification": task.get("classification"),
                    "certification_year": task["year"],
                    "query_used": task["query"],
                    "hit_count": len(matched_items),
                    "items": matched_items
                })

        output = {
            "classification": classification or "all",
            "total_chateaux": len(tasks),
            "search_results": results
        }

        # S3に保存 (latest.json と 履歴用)
        latest_key = data_manager.save_results_to_s3(output)
        
        return {
            "statusCode": 200,
            "body": {
                "message": "Search completed and saved to S3",
                "classification": classification,
                "s3_key": latest_key
            }
        }

    except Exception as e:
        print(f"Error in Collector: {e}")
        return {
            "statusCode": 500,
            "body": str(e)
        }
