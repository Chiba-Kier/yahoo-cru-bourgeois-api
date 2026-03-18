import os
import sys
import json

# modulesをインポートできるようにパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.data_manager import DataManager

def handler(event, context):
    """
    Reader Lambda Handler
    Triggered by HTTP (via Function URL or API Gateway).
    Reads the latest JSON result for a given classification from S3.
    """
    print(f"Reader started with event: {event}")
    
    # パラメータの取得 (API Gateway / Function URL の両方に対応)
    query_params = event.get("queryStringParameters", {}) or {}
    path_params = event.get("pathParameters", {}) or {}
    
    classification = path_params.get("classification") or query_params.get("classification")
    
    if not classification:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "classification parameter is required. (e.g. /search/medoc)"})
        }

    try:
        data_manager = DataManager()
        
        # S3から最新の結果 (latest.json) を取得
        results = data_manager.get_latest_results(classification)
        
        if "error" in results:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(results, ensure_ascii=False)
            }
            
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*" # CORS対応
            },
            "body": json.dumps(results, ensure_ascii=False)
        }

    except Exception as e:
        print(f"Error in Reader: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
