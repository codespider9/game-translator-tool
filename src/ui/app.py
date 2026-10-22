import sys
from pathlib import Path

# Add project root directory to system path
sys.path.append(str(Path(__file__).parent.parent.parent))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.core.detector import GameEngineDetector
from src.parsers.unreal_locres import UnrealLocresParser
from src.ai.gemini_provider import GeminiTranslator

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GameTranslatorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Universal Game Translator Tool")
        self.geometry("800x580")

        self.selected_folder = None
        self.detected_engine = None

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self, text="Universal Game Translator", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_title.pack(pady=(20, 10))

        # Folder Selection Frame
        self.frame_folder = ctk.CTkFrame(self)
        self.frame_folder.pack(pady=10, padx=20, fill="x")

        self.btn_select = ctk.CTkButton(
            self.frame_folder, text="Select Game Folder", command=self.select_directory
        )
        self.btn_select.pack(side="left", padx=10, pady=10)

        self.lbl_folder_path = ctk.CTkLabel(
            self.frame_folder, text="No folder selected", text_color="gray"
        )
        self.lbl_folder_path.pack(side="left", padx=10)

        # Engine Status Info
        self.lbl_engine_info = ctk.CTkLabel(
            self, text="Engine Status: Waiting for directory selection...", font=ctk.CTkFont(size=14)
        )
        self.lbl_engine_info.pack(pady=10)

        # Gemini API Key Input Frame
        self.frame_api = ctk.CTkFrame(self)
        self.frame_api.pack(pady=10, padx=20, fill="x")

        self.lbl_api = ctk.CTkLabel(self.frame_api, text="Gemini API Key:")
        self.lbl_api.pack(side="left", padx=10, pady=10)

        self.entry_api = ctk.CTkEntry(
            self.frame_api, placeholder_text="Enter your Gemini API key here...", show="*"
        )
        self.entry_api.pack(side="left", fill="x", expand=True, padx=10)

        # Action Buttons
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.pack(pady=15, padx=20, fill="x")

        self.btn_extract = ctk.CTkButton(
            self.frame_actions,
            text="Extract Game Texts",
            command=self.extract_texts,
            state="disabled",
        )
        self.btn_extract.pack(side="left", padx=15, pady=10, expand=True)

        self.btn_translate = ctk.CTkButton(
            self.frame_actions,
            text="Translate with Gemini AI",
            command=self.translate_texts,
            state="disabled",
        )
        self.btn_translate.pack(side="left", padx=15, pady=10, expand=True)

        # Log & Output Area
        self.txt_log = ctk.CTkTextbox(self, height=180)
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_message("System initialized. Please select a game folder to start.")

    def log_message(self, message: str):
        self.txt_log.insert("end", f"> {message}\n")
        self.txt_log.see("end")

    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.lbl_folder_path.configure(text=folder, text_color="white")
            self.log_message(f"Selected directory: {folder}")

            detector = GameEngineDetector(folder)
            res = detector.detect_engine()
            self.detected_engine = res.get("engine")

            self.lbl_engine_info.configure(
                text=f"Detected Engine: {self.detected_engine} | Status: {res.get('status')}",
                text_color="#4CAF50" if self.detected_engine != "Unknown" else "#FF9800",
            )

            if self.detected_engine != "Unknown":
                self.btn_extract.configure(state="normal")

    def extract_texts(self):
        if not self.selected_folder:
            return

        self.log_message("Starting text extraction phase...")

        if self.detected_engine == "Unreal Engine":
            # Search for .locres files
            locres_files = list(Path(self.selected_folder).rglob("*.locres"))
            if not locres_files:
                self.log_message("No .locres localization files found in directory.")
                messagebox.showwarning("Warning", "No .locres files found.")
                return

            self.log_message(f"Found {len(locres_files)} .locres file(s). Extracting...")
            parser = UnrealLocresParser(str(locres_files[0]))
            extracted = parser.extract_strings()

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Extraction complete! Saved to: {output_file.name}")
            self.btn_translate.configure(state="normal")
        else:
            self.log_message(f"Parser for {self.detected_engine} is under development.")

    def translate_texts(self):
        api_key = self.entry_api.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter a valid Gemini API Key.")
            return

        json_path = Path(self.selected_folder) / "extracted_strings.json"
        if not json_path.exists():
            messagebox.showerror("Error", "Extracted text file not found. Extract texts first.")
            return

        self.log_message("Sending texts to Gemini API for translation...")
        # Translation process initiation logic
        translator = GeminiTranslator(api_key=api_key)
        self.log_message("Translation pipeline active. (Check API logs for status)")


if __name__ == "__main__":
    app = GameTranslatorApp()
    app.mainloop()