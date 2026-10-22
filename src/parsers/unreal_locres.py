import struct
import json
from pathlib import Path
from typing import Dict, Any


class UnrealLocresParser:
    """Parser for Unreal Engine binary .locres (Localization Resource) files (UE4/UE5)."""

    LOCRES_MAGIC = b"\x0e\x14\x74\x75\x67\x4a\x03\xfc\x4a\x15\x90\x9d\xc3\x37\x7f\x1b"

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.texts: Dict[str, Dict[str, str]] = {}

    def _read_fstring(self, f) -> str:
        """Reads Unreal Engine FString structure (UTF-8 / UTF-16)."""
        length_bytes = f.read(4)
        if not length_bytes or len(length_bytes) < 4:
            return ""
        length = struct.unpack("<i", length_bytes)[0]

        if length == 0:
            return ""
        elif length > 0:
            # UTF-8 encoded string
            string_bytes = f.read(length)
            return string_bytes[:-1].decode("utf-8", errors="ignore")
        else:
            # UTF-16 encoded string (length is negative)
            length = -length
            string_bytes = f.read(length * 2)
            return string_bytes[:-2].decode("utf-16-le", errors="ignore")

    def extract_strings(self) -> Dict[str, Dict[str, str]]:
        """Parses binary .locres header, namespaces, keys, and string arrays."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        extracted_data = {}

        try:
            with open(self.file_path, "rb") as f:
                # Read 16-byte magic number
                magic = f.read(16)
                if magic != self.LOCRES_MAGIC:
                    print("Warning: Invalid or legacy .locres magic header.")

                # Version byte
                version = ord(f.read(1)) if magic == self.LOCRES_MAGIC else 0

                # Read string table / entries count
                entries_count_bytes = f.read(4)
                if len(entries_count_bytes) < 4:
                    return {}

                entries_count = struct.unpack("<I", entries_count_bytes)[0]

                for _ in range(entries_count):
                    namespace = self._read_fstring(f)
                    key_count = struct.unpack("<I", f.read(4))[0]
                    namespace_dict = {}

                    for _ in range(key_count):
                        key = self._read_fstring(f)
                        f.read(4)  # Hash check
                        source_string = self._read_fstring(f)
                        namespace_dict[key] = source_string

                    if namespace_dict:
                        extracted_data[namespace or "Global"] = namespace_dict

            self.texts = extracted_data
            return extracted_data
        except Exception as e:
            print(f"Error parsing .locres file binary: {e}")
            return {}

    def export_to_json(self, output_path: str) -> bool:
        """Saves parsed strings to a structured JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to export JSON: {e}")
            return False