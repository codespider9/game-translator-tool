import json
import re
from pathlib import Path
from typing import Dict, Any


class UnityAssetsParser:
    """Parser for Unity Engine TextAssets and plain JSON/CSV string files found in game data."""

    def __init__(self, game_dir: str):
        self.game_dir = Path(game_dir)
        self.texts: Dict[str, Dict[str, str]] = {}

    def extract_strings(self) -> Dict[str, Dict[str, str]]:
        """Scans Unity _Data directory for text assets and extracts strings."""
        if not self.game_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.game_dir}")

        extracted_data = {}

        # Look for _Data folder
        data_folders = list(self.game_dir.glob("*_Data"))
        target_dir = data_folders[0] if data_folders else self.game_dir

        # Scan for localized JSON, CSV, or TXT files inside Resources and StreamingAssets
        search_patterns = ["**/*.json", "**/*.csv", "**/*.txt"]
        found_files = []
        for pattern in search_patterns:
            found_files.extend(list(target_dir.rglob(pattern)))

        for file_path in found_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                # Attempt parsing as JSON
                if file_path.suffix == ".json":
                    parsed_json = json.loads(content)
                    if isinstance(parsed_json, dict):
                        # Filter key-value text pairs
                        str_dict = {
                            k: str(v)
                            for k, v in parsed_json.items()
                            if isinstance(v, (str, int))
                        }
                        if str_dict:
                            extracted_data[file_path.stem] = str_dict
                elif file_path.suffix in [".csv", ".txt"]:
                    lines = content.splitlines()
                    line_dict = {}
                    for idx, line in enumerate(lines[:500]):  # Limit sample size
                        if "=" in line or "," in line:
                            parts = re.split(r"[=,]", line, maxsplit=1)
                            if len(parts) == 2:
                                line_dict[parts[0].strip()] = parts[1].strip()
                    if line_dict:
                        extracted_data[file_path.stem] = line_dict
            except Exception as e:
                print(f"Skipping non-text asset {file_path.name}: {e}")

        self.texts = extracted_data
        return extracted_data

    def export_to_json(self, output_path: str) -> bool:
        """Saves extracted Unity strings to a structured JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to export JSON: {e}")
            return False