import re
import json
from pathlib import Path
from typing import Dict, Any


class RenPyScriptParser:
    """Parser for Ren'Py script files (.rpy) extracting dialogue strings."""

    def __init__(self, game_dir: str):
        self.game_dir = Path(game_dir)
        self.texts: Dict[str, Dict[str, str]] = {}

    def extract_strings(self) -> Dict[str, Dict[str, str]]:
        """Scans game directory for .rpy script files and extracts dialogue entries."""
        if not self.game_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.game_dir}")

        extracted_data = {}
        rpy_files = list(self.game_dir.rglob("*.rpy"))

        # Regex pattern to match Ren'Py dialogue lines: character "dialogue text"
        dialogue_pattern = re.compile(r'^\s*(?:[a-zA-Z0-9_]+\s+)?"([^"]+)"\s*$')

        for file_path in rpy_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
                file_dict = {}

                for idx, line in enumerate(lines):
                    line_clean = line.strip()
                    # Skip comments and internal label definitions
                    if line_clean.startswith("#") or line_clean.startswith("label "):
                        continue

                    match = dialogue_pattern.match(line_clean)
                    if match:
                        text = match.group(1)
                        if len(text) > 2:  # Ignore trivial strings
                            file_dict[f"line_{idx}"] = text

                if file_dict:
                    extracted_data[file_path.stem] = file_dict
            except Exception as e:
                print(f"Error parsing Ren'Py file {file_path.name}: {e}")

        self.texts = extracted_data
        return extracted_data

    def export_to_json(self, output_path: str) -> bool:
        """Exports extracted strings to JSON format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to export JSON: {e}")
            return False