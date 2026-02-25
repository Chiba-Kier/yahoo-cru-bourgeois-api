import pandas as pd
from typing import List, Dict, Any
import os
import glob

class DataManager:
    def __init__(self, data_root: str = "data"):
        self.data_root = data_root

    def load_master_data(self, classification: str) -> List[Dict[str, Any]]:
        """
        Reads all CSV files within a classification folder (e.g., 'data/cru_bourgeois/*.csv')
        and merges them into a single list of records.
        """
        folder_path = os.path.join(self.data_root, classification)
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Classification folder not found: {folder_path}")

        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        all_records = []

        for file_path in csv_files:
            df = pd.read_csv(file_path)
            # Add metadata from file name (e.g., certification year)
            year = os.path.splitext(os.path.basename(file_path))[0]
            df["source_year"] = year
            
            # Clean data
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            df = df.where(pd.notnull(df), None)
            
            all_records.extend(df.to_dict(orient="records"))
        
        return all_records

    def get_search_tasks(self, classification: str = "cru_bourgeois") -> List[Dict[str, Any]]:
        """
        Prepares search tasks for a given classification.
        """
        master_data = self.load_master_data(classification)
        tasks = []
        
        for entry in master_data:
            query = entry.get("search_name_kana") or entry.get("search_name_ascii") or entry.get("chateau_name")
            
            tasks.append({
                "original_name": entry.get("chateau_name"),
                "query": query,
                "appellation": entry.get("appellation"),
                "year": entry.get("source_year")
            })
            
        return tasks

if __name__ == "__main__":
    # Test with the new structure
    try:
        manager = DataManager()
        tasks = manager.get_search_tasks("cru_bourgeois")
        print(f"Search Tasks for 'cru_bourgeois' (Total: {len(tasks)}):")
        for task in tasks:
            print(f"- {task['original_name']} ({task['year']}) -> Query: '{task['query']}'")
    except Exception as e:
        print(f"Error: {e}")
