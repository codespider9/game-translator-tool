import os
from typing import Dict, Optional


class GameEngineDetector:
    """Detects game engine type based on directory structure and signature files."""

    def __init__(self, game_dir: str):
        self.game_dir = game_dir

    def detect_engine(self) -> Dict[str, Optional[str]]:
        if not os.path.exists(self.game_dir):
            return {"engine": "Unknown", "status": "Directory does not exist"}

        # Check for Unreal Engine signatures
        for root, dirs, files in os.walk(self.game_dir):
            if "Binaries" in dirs and ("Content" in dirs or "Engine" in dirs):
                return {"engine": "Unreal Engine", "status": "Detected via directory layout"}
            for file in files:
                if file.endswith(".locres"):
                    return {"engine": "Unreal Engine", "status": "Detected via .locres localization file"}

        # Check for Unity Engine signatures
        for root, dirs, files in os.walk(self.game_dir):
            if any(file.endswith(("_Data", "UnityPlayer.dll")) for file in files) or any(
                d.endswith("_Data") for d in dirs
            ):
                return {"engine": "Unity", "status": "Detected via Unity executable/data folder"}

        # Check for Ren'Py signatures
        for root, dirs, files in os.walk(self.game_dir):
            if "renpy" in dirs or any(file.endswith((".rpy", ".rpyc")) for file in files):
                return {"engine": "Ren'Py", "status": "Detected via Ren'Py script files"}

        # Check for Godot signatures
        for root, dirs, files in os.walk(self.game_dir):
            if any(file.endswith(".pck") for file in files):
                return {"engine": "Godot", "status": "Detected via .pck archive file"}

        return {"engine": "Unknown", "status": "Could not identify engine automatically"}