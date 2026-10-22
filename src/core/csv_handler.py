import csv
import json
from pathlib import Path
from typing import Dict, Any


class CSVTranslationHandler:
    """Utility to export/import extracted strings to/from CSV files for spreadsheet editing."""

    @staticmethod
    def export_json_to_csv(json_data: Dict[str, Dict[str, str]], output_csv_path: str) -> bool:
        """Flattens extracted JSON strings and writes to a standard CSV file."""
        try:
            with open(output_csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Namespace", "Key", "Original_Text", "Translation"])

                for namespace, keys_dict in json_data.items():
                    for key, orig_text in keys_dict.items():
                        writer.writerow([namespace, key, orig_text, ""])
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    @staticmethod
    def import_csv_to_json(input_csv_path: str) -> Dict[str, Dict[str, str]]:
        """Reads modified CSV file and reconstructs nested JSON translation dictionary."""
        reconstructed_data: Dict[str, Dict[str, str]] = {}
        try:
            with open(input_csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ns = row.get("Namespace", "Global")
                    key = row.get("Key", "")
                    trans = row.get("Translation", "").strip() or row.get("Original_Text", "")

                    if ns not in reconstructed_data:
                        reconstructed_data[ns] = {}

                    if key:
                        reconstructed_data[ns][key] = trans
            return reconstructed_data
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return {}