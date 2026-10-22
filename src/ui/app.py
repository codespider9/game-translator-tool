import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

import customtkinter as ctk
from tkinter import filedialog
from src.core.detector import GameEngineDetector

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class GameTranslatorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Universal Game Translator Tool")
        self.geometry("700x450")

        # Header Label
        self.header_label = ctk.CTkLabel(
            self,
            text="Universal Game Translator",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.header_label.pack(pady=20)

        # Select Directory Button
        self.btn_select = ctk.CTkButton(
            self, text="Select Game Directory", command=self.select_directory
        )
        self.btn_select.pack(pady=10)

        # Status & Engine Info Output
        self.status_label = ctk.CTkLabel(
            self,
            text="No directory selected.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.status_label.pack(pady=10)

        self.engine_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.engine_label.pack(pady=10)

    def select_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.status_label.configure(
                text=f"Selected: {folder_selected}", text_color="white"
            )

            # Detect Game Engine
            detector = GameEngineDetector(folder_selected)
            result = detector.detect_engine()

            engine_name = result.get("engine", "Unknown")
            status_msg = result.get("status", "")

            self.engine_label.configure(
                text=f"Detected Engine: {engine_name}\n({status_msg})",
                text_color="#4CAF50" if engine_name != "Unknown" else "#FF9800",
            )


if __name__ == "__main__":
    app = GameTranslatorApp()
    app.mainloop()