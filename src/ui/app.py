import sys
import json
from pathlib import Path

# Add project root directory to system path
sys.path.append(str(Path(__file__).parent.parent.parent))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.core.detector import GameEngineDetector
from src.core.text_formatter import ArabicTextFormatter
from src.parsers.unreal_locres import UnrealLocresParser
from src.ai.gemini_provider import GeminiTranslator
from src.ui.editor import TranslationEditorWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GameTranslatorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Universal Game Translator Tool")
        self.geometry("850x620")

        self.selected_folder = None
        self.detected_engine = None
        self.extracted_data = {}
        self.translated_data = {}

        # Title
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

        # Engine Info
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

        # Action Buttons Frame
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.pack(pady=10, padx=20, fill="x")

        self.btn_extract = ctk.CTkButton(
            self.frame_actions, text="1. Extract Texts", command=self.extract_texts, state="disabled"
        )
        self.btn_extract.pack(side="left", padx=10, pady=10, expand=True)

        self.btn_translate = ctk.CTkButton(
            self.frame_actions, text="2. Translate (AI)", command=self.translate_texts, state="disabled"
        )
        self.btn_translate.pack(side="left", padx=10, pady=10, expand=True)

        self.btn_edit = ctk.CTkButton(
            self.frame_actions, text="3. Manual Review", command=self.open_editor, state="disabled"
        )
        self.btn_edit.pack(side="left", padx=10, pady=10, expand=True)

        # Log & Output Console
        self.txt_log = ctk.CTkTextbox(self, height=200)
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_message("System ready. Please select a game directory.")

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
            locres_files = list(Path(self.selected_folder).rglob("*.locres"))
            if not locres_files:
                self.log_message("No .locres localization files found.")
                messagebox.showwarning("Warning", "No .locres files found in directory.")
                return

            self.log_message(f"Found {len(locres_files)} .locres file(s). Extracting strings...")
            parser = UnrealLocresParser(str(locres_files[0]))
            self.extracted_data = parser.extract_strings()

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Extraction complete! Extracted file saved to: {output_file.name}")
            self.btn_translate.configure(state="normal")
            self.btn_edit.configure(state="normal")
        else:
            self.log_message(f"Parser for {self.detected_engine} is under construction.")

    def translate_texts(self):
        api_key = self.entry_api.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter a valid Gemini API Key.")
            return

        json_path = Path(self.selected_folder) / "extracted_strings.json"
        if not json_path.exists():
            messagebox.showerror("Error", "Extracted text file missing. Run extraction first.")
            return

        self.log_message("Translating extracted text via Gemini API...")
        translator = GeminiTranslator(api_key=api_key)

        # Standard sample extraction structure for testing
        raw_sample = self.extracted_data.get("SampleNamespace", {})
        translated_raw = translator.translate_batch(raw_sample, target_language="Arabic")

        # Apply Arabic Reshaping for proper display in-game
        self.translated_data = ArabicTextFormatter.process_dictionary(translated_raw)

        # Save translated result
        trans_file = Path(self.selected_folder) / "translated_strings.json"
        with open(trans_file, "w", encoding="utf-8") as f:
            json.dump(self.translated_data, f, ensure_ascii=False, indent=4)

        self.log_message(f"Translation complete! Saved to: {trans_file.name}")

    def open_editor(self):
        sample_orig = self.extracted_data.get("SampleNamespace", {})
        if not sample_orig:
            messagebox.showwarning("Warning", "No extracted strings available for review.")
            return

        editor_win = TranslationEditorWindow(self, sample_orig, self.translated_data)
        editor_win.focus()


if __name__ == "__main__":
    app = GameTranslatorApp()
    app.mainloop()