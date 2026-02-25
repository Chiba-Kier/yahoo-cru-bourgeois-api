import pandas as pd
from typing import List, Dict, Any, Optional
import os
import glob

class DataManager:
    def __init__(self, data_root: str = "data"):
        self.data_root = data_root

    def get_all_classifications(self) -> List[str]:
        """
        Lists all classification directories in the data root.
        """
        if not os.path.exists(self.data_root):
            return []
        return [
            d for d in os.listdir(self.data_root) 
            if os.path.isdir(os.path.join(self.data_root, d))
        ]

    def load_master_data(self, classification: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Reads all CSV files within a classification folder or all folders if None.
        """
        if classification:
            folders = [os.path.join(self.data_root, classification)]
        else:
            folders = [os.path.join(self.data_root, d) for d in self.get_all_classifications()]

        all_records = []

        for folder_path in folders:
            if not os.path.exists(folder_path):
                if classification: # Only raise if specific classification was requested
                    raise FileNotFoundError(f"Classification folder not found: {folder_path}")
                continue

            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            # Get classification name from folder path for record tagging
            current_classification = os.path.basename(folder_path)

            for file_path in csv_files:
                df = pd.read_csv(file_path)
                # Add metadata from file name (e.g., certification year)
                year = os.path.splitext(os.path.basename(file_path))[0]
                df["source_year"] = year
                df["classification"] = current_classification
                
                # Clean data
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
                df = df.where(pd.notnull(df), None)
                
                all_records.extend(df.to_dict(orient="records"))
        
        return all_records

    def get_search_tasks(self, classification: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Prepares search tasks for a given classification or all classifications.
        """
        master_data = self.load_master_data(classification)
        tasks = []
        
        for entry in master_data:
            query = entry.get("search_name_kana") or entry.get("search_name_ascii") or entry.get("chateau_name")
            
            tasks.append({
                "original_name": entry.get("chateau_name"),
                "query": query,
                "appellation": entry.get("appellation"),
                "year": entry.get("source_year"),
                "classification": entry.get("classification")
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
