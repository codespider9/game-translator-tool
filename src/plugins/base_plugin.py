from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParserPlugin(ABC):
    """Abstract base class for all game engine parser plugins."""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Returns the unique human-readable name of the engine plugin."""
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list:
        """Returns a list of file extensions supported by this plugin (e.g., ['.locres', '.json'])."""
        pass

    @abstractmethod
    def extract_strings(self, target_path: str) -> Dict[str, Dict[str, str]]:
        """Extracts localization strings from the specified path into a nested dictionary structure."""
        pass

    @abstractmethod
    def repack_strings(self, translated_data: Dict[str, Dict[str, str]], output_path: str) -> bool:
        """Repacks modified translations back into the engine native file format."""
        pass