import PyInstaller.__main__
from pathlib import Path

root_dir = Path(__file__).parent

PyInstaller.__main__.run(
    [
        str(root_dir / "src" / "ui" / "app.py"),
        "--onefile",
        "--noconsole",
        "--name=GameTranslatorTool",
        f"--add-data={root_dir / 'src'};src",
    ]
)