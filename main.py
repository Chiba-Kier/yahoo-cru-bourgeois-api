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

        for task in tasks:
            # Perform search
            hits = yahoo_client.search_items(
                query=task["query"],
                min_price=min_price,
                max_price=max_price
            )
            
            results.append({
                "chateau": task["original_name"],
                "classification": task.get("classification"),
                "certification_year": task["year"],
                "query_used": task["query"],
                "hit_count": len(hits),
                "items": [
                    {
                        "name": h.get("name"),
                        "price": h.get("price"),
                        "url": h.get("url"),
                        "store": h.get("store", {}).get("name")
                    } for h in hits
                ]
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
