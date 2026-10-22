import json
import csv
from pathlib import Path
from typing import Dict, Any


class GodotTranslationParser:
    """Parser for Godot Engine translation CSVs and resource text files."""

    def __init__(self, game_dir: str):
        self.game_dir = Path(game_dir)
        self.texts: Dict[str, Dict[str, str]] = {}

    def extract_strings(self) -> Dict[str, Dict[str, str]]:
        """Scans directory for Godot CSV translation sheets and text assets."""
        if not self.game_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.game_dir}")

        extracted_data = {}
        csv_files = list(self.game_dir.rglob("*.csv"))

        for csv_path in csv_files:
            try:
                file_dict = {}
                with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if not header or len(header) < 2:
                        continue

                    # Read key-value pairs (Key, en, ar...)
                    for row in reader:
                        if len(row) >= 2 and row[0].strip():
                            key = row[0].strip()
                            source_val = row[1].strip()
                            file_dict[key] = source_val

                if file_dict:
                    extracted_data[csv_path.stem] = file_dict
            except Exception as e:
                print(f"Error parsing Godot CSV {csv_path.name}: {e}")

        self.texts = extracted_data
        return extracted_data

    def export_to_json(self, output_path: str) -> bool:
        """Exports extracted Godot strings to a structured JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to export JSON: {e}")
            return False