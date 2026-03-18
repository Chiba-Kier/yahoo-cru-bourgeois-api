import pandas as pd
from typing import List, Dict, Any, Optional
import os
import boto3
import json
import io
from datetime import datetime

class DataManager:
    def __init__(self, bucket_name: Optional[str] = None, data_root: str = "master/"):
        self.bucket_name = bucket_name or os.environ.get("S3_BUCKET_NAME")
        self.data_root = data_root
        self.s3 = boto3.client('s3')

    def get_all_classifications(self) -> List[str]:
        """
        Lists all classification 'folders' in the S3 master/ directory.
        """
        if not self.bucket_name:
            return []
            
        paginator = self.s3.get_paginator('list_objects_v2')
        result = paginator.paginate(Bucket=self.bucket_name, Prefix=self.data_root, Delimiter='/')
        
        classifications = []
        for page in result:
            for prefix in page.get('CommonPrefixes', []):
                # e.g., "master/medoc/" -> "medoc"
                name = prefix.get('Prefix').replace(self.data_root, "").strip("/")
                if name:
                    classifications.append(name)
        return classifications

    def load_master_data(self, classification: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Reads CSV files from S3 master/{classification}/ folder.
        """
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME is not set.")

        prefix = f"{self.data_root}{classification}/" if classification else self.data_root
        
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

        all_records = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj.get('Key')
                if not key.endswith('.csv'):
                    continue

                # Get classification and year from key
                # e.g., "master/medoc/1855.csv"
                parts = key.replace(self.data_root, "").split("/")
                current_class = parts[0]
                year = os.path.splitext(parts[-1])[0]

                # Download and read CSV
                response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                csv_content = response['Body'].read().decode('utf-8')
                df = pd.read_csv(io.StringIO(csv_content))

                # Add metadata
                df["source_year"] = year
                df["classification"] = current_class
                
                # Clean data
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                df = df.replace({pd.NA: None, float('nan'): None})
                
                all_records.extend(df.to_dict(orient="records"))
        
        return all_records

    def get_search_tasks(self, classification: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Prepares search tasks based on S3 master data.
        De-duplicates tasks by query string to avoid redundant Yahoo! API calls.
        """
        master_data = self.load_master_data(classification)
        tasks_map = {} # query -> task_info
        
        for entry in master_data:
            search_kana = entry.get("search_name_kana") or ""
            search_ascii = entry.get("search_name_ascii") or ""
            chateau_name = entry.get("chateau_name") or ""
            query = search_kana or search_ascii or chateau_name
            
            if not query or str(query).lower() == "nan":
                continue
            
            # 重複クエリは最初の1件のみ採用（APIコール節約）
            if query not in tasks_map:
                tasks_map[query] = {
                    "original_name": chateau_name,
                    "query": query,
                    "appellation": entry.get("appellation"),
                    "year": entry.get("source_year"),
                    "classification": entry.get("classification")
                }
        
        print(f"Prepared {len(tasks_map)} unique search tasks from {len(master_data)} master records.")
        return list(tasks_map.values())

    def save_results_to_s3(self, results: Dict[str, Any], prefix: str = "results/"):
        """
        Saves results to S3.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        classification = results.get('classification', 'all')
        
        # Save historical version
        history_key = f"{prefix}{classification}/{timestamp}.json"
        # Save 'latest' version for Reader
        latest_key = f"{prefix}{classification}/latest.json"
        
        body = json.dumps(results, ensure_ascii=False)
        
        # Save both
        self.s3.put_object(Bucket=self.bucket_name, Key=history_key, Body=body, ContentType='application/json')
        self.s3.put_object(Bucket=self.bucket_name, Key=latest_key, Body=body, ContentType='application/json')
        
        print(f"Results saved: {history_key} and {latest_key}")
        return latest_key

    def get_latest_results(self, classification: str, prefix: str = "results/") -> Dict[str, Any]:
        """
        Reads the 'latest.json' for a given classification from S3.
        Used by Reader Lambda.
        """
        key = f"{prefix}{classification}/latest.json"
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3.exceptions.NoSuchKey:
            return {"error": f"No results found for classification: {classification}"}
