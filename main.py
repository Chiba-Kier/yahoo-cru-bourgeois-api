from fastapi import FastAPI, Query, HTTPException, Path
from typing import List, Dict, Any, Optional
from modules.yahoo_client import YahooShoppingClient
from modules.data_manager import DataManager

app = FastAPI(
    title="Wine Classification Search API",
    description="特定の格付け銘柄をYahoo!ショッピングで検索するAPI",
    version="0.2.0"
)

# Initialize modules
try:
    yahoo_client = YahooShoppingClient()
    data_manager = DataManager()
except Exception as e:
    print(f"Initialization Error: {e}")
    yahoo_client = None

@app.get("/")
def read_root():
    return {"message": "Wine Classification Search API is running"}

@app.get("/search")
@app.get("/search/{classification}")
def search_wine_classification(
    classification: Optional[str] = None,
    min_price: Optional[int] = Query(None, description="最低価格 (JPY)"),
    max_price: Optional[int] = Query(None, description="最高価格 (JPY)"),
):
    """
    指定した格付け、または全ての銘柄をYahoo!ショッピングで検索します。
    """
    if not yahoo_client:
        raise HTTPException(status_code=500, detail="Yahoo! Client not initialized.")

    try:
        tasks = data_manager.get_search_tasks(classification)
        results = []

        # 5件ずつに分割して処理
        chunk_size = 5
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            
            # Yahoo! API の OR 検索は '|' を使用します
            # 例: (シャトー A) | (シャトー B) | (シャトー C)
            combined_query = " | ".join([f'({t["query"]})' for t in chunk])
            
            # まとめて検索
            hits = yahoo_client.search_items(
                query=combined_query,
                min_price=min_price,
                max_price=max_price,
                results=100
            )
            
            # 各シャトーごとに結果を振り分け
            for task in chunk:
                # CSVの表記そのままの検索クエリを使用（小文字化のみ）
                # 単語分割はせず、商品名にこの文字列がそのまま含まれているかを確認します
                search_query = task["query"].lower()
                matched_items = []
                
                for h in hits:
                    item_name = h.get("name", "").lower()
                    # 商品名にクエリ文字列がそのまま含まれているか判定
                    if search_query in item_name:
                        matched_items.append({
                            "name": h.get("name"),
                            "price": h.get("price"),
                            "url": h.get("url"),
                            "store": h.get("seller", {}).get("name") or h.get("store", {}).get("name"),
                            "image": h.get("image", {}).get("medium"),
                            "description": h.get("description"),
                            "review_rate": h.get("review", {}).get("rate"),
                            "review_count": h.get("review", {}).get("count"),
                            "in_stock": h.get("inStock"),
                            "code": h.get("code"),
                            "brand": h.get("brand", {}).get("name"),
                            "raw": h 
                        })
                
                results.append({
                    "chateau": task["original_name"],
                    "classification": task.get("classification"),
                    "certification_year": task["year"],
                    "query_used": task["query"],
                    "hit_count": len(matched_items),
                    "items": matched_items
                })

        return {
            "classification": classification or "all",
            "total_chateaux": len(tasks),
            "search_results": results
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Classification '{classification}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
