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
from src.parsers.unity_assets import UnityAssetsParser
from src.parsers.renpy_script import RenPyScriptParser
from src.parsers.godot_pck import GodotTranslationParser
from src.ai.gemini_provider import GeminiTranslator
from src.ai.ollama_provider import OllamaTranslator
from src.ui.editor import TranslationEditorWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GameTranslatorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Universal Game Translator Tool")
        self.geometry("900x680")

        self.selected_folder = None
        self.detected_engine = None
        self.extracted_data = {}
        self.translated_data = {}
        self.target_locres_path = None

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

        # AI Provider Selection Frame
        self.frame_ai = ctk.CTkFrame(self)
        self.frame_ai.pack(pady=10, padx=20, fill="x")

        self.lbl_provider = ctk.CTkLabel(self.frame_ai, text="AI Provider:")
        self.lbl_provider.pack(side="left", padx=10, pady=10)

        self.combo_provider = ctk.CTkOptionMenu(
            self.frame_ai,
            values=["Google Gemini API", "Local Ollama (Offline)"],
            command=self.toggle_ai_provider_ui,
        )
        self.combo_provider.pack(side="left", padx=10)

        self.entry_api = ctk.CTkEntry(
            self.frame_ai, placeholder_text="Enter Gemini API key...", show="*"
        )
        self.entry_api.pack(side="left", fill="x", expand=True, padx=10)

        # Action Buttons Frame
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.pack(pady=10, padx=20, fill="x")

        self.btn_extract = ctk.CTkButton(
            self.frame_actions, text="1. Extract Texts", command=self.extract_texts, state="disabled"
        )
        self.btn_extract.pack(side="left", padx=5, pady=10, expand=True)

        self.btn_translate = ctk.CTkButton(
            self.frame_actions, text="2. Translate (AI)", command=self.translate_texts, state="disabled"
        )
        self.btn_translate.pack(side="left", padx=5, pady=10, expand=True)

        self.btn_edit = ctk.CTkButton(
            self.frame_actions, text="3. Manual Review", command=self.open_editor, state="disabled"
        )
        self.btn_edit.pack(side="left", padx=5, pady=10, expand=True)

        self.btn_repack = ctk.CTkButton(
            self.frame_actions, text="4. Repack & Save", command=self.repack_game_files, state="disabled"
        )
        self.btn_repack.pack(side="left", padx=5, pady=10, expand=True)

        # Log Console
        self.txt_log = ctk.CTkTextbox(self, height=220)
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_message("System ready. Select a game directory to begin.")

    def log_message(self, message: str):
        self.txt_log.insert("end", f"> {message}\n")
        self.txt_log.see("end")

    def toggle_ai_provider_ui(self, choice: str):
        if choice == "Local Ollama (Offline)":
            self.entry_api.configure(state="disabled", placeholder_text="Ollama uses local host (http://localhost:11434)")
        else:
            self.entry_api.configure(state="normal", placeholder_text="Enter Gemini API key...")

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

        self.log_message(f"Starting extraction for {self.detected_engine}...")

        if self.detected_engine == "Unreal Engine":
            locres_files = list(Path(self.selected_folder).rglob("*.locres"))
            if not locres_files:
                self.log_message("No .locres localization files found.")
                messagebox.showwarning("Warning", "No .locres files found in directory.")
                return

            self.target_locres_path = str(locres_files[0])
            self.log_message(f"Found target: {locres_files[0].name}. Parsing binary...")

            parser = UnrealLocresParser(self.target_locres_path)
            self.extracted_data = parser.extract_strings()

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Extraction complete! Saved to: {output_file.name}")
            self._enable_post_extraction_buttons()

        elif self.detected_engine == "Unity":
            parser = UnityAssetsParser(self.selected_folder)
            self.extracted_data = parser.extract_strings()

            if not self.extracted_data:
                self.log_message("No text assets found in Unity folder.")
                messagebox.showwarning("Warning", "No readable text assets found.")
                return

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Unity text extraction complete! Saved to: {output_file.name}")
            self._enable_post_extraction_buttons()

        elif self.detected_engine == "Ren'Py":
            parser = RenPyScriptParser(self.selected_folder)
            self.extracted_data = parser.extract_strings()

            if not self.extracted_data:
                self.log_message("No .rpy script files found.")
                messagebox.showwarning("Warning", "No .rpy script files found.")
                return

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Ren'Py script extraction complete! Saved to: {output_file.name}")
            self._enable_post_extraction_buttons()

        elif self.detected_engine == "Godot Engine":
            parser = GodotTranslationParser(self.selected_folder)
            self.extracted_data = parser.extract_strings()

            if not self.extracted_data:
                self.log_message("No translation CSV sheets found in Godot folder.")
                messagebox.showwarning("Warning", "No translation CSV files found.")
                return

            output_file = Path(self.selected_folder) / "extracted_strings.json"
            parser.export_to_json(str(output_file))

            self.log_message(f"Godot translation extraction complete! Saved to: {output_file.name}")
            self._enable_post_extraction_buttons()

    def _enable_post_extraction_buttons(self):
        self.btn_translate.configure(state="normal")
        self.btn_edit.configure(state="normal")
        self.btn_repack.configure(state="normal")

    def translate_texts(self):
        provider_choice = self.combo_provider.get()

        if provider_choice == "Google Gemini API":
            api_key = self.entry_api.get().strip()
            if not api_key:
                messagebox.showerror("Error", "Please enter a valid Gemini API Key.")
                return
            translator = GeminiTranslator(api_key=api_key)
            self.log_message("Translating via Google Gemini Cloud API...")
        else:
            translator = OllamaTranslator()
            self.log_message("Translating via Local Ollama (llama3)...")

        translated_full = {}
        for namespace, keys_dict in self.extracted_data.items():
            raw_translated = translator.translate_batch(keys_dict, target_language="Arabic")
            formatted_translated = ArabicTextFormatter.process_dictionary(raw_translated)
            translated_full[namespace] = formatted_translated

        self.translated_data = translated_full

        trans_file = Path(self.selected_folder) / "translated_strings.json"
        with open(trans_file, "w", encoding="utf-8") as f:
            json.dump(self.translated_data, f, ensure_ascii=False, indent=4)

        self.log_message(f"Translation complete & reshaped! Saved to: {trans_file.name}")

    def open_editor(self):
        sample_orig = self.extracted_data.get("Global", self.extracted_data.get(next(iter(self.extracted_data), ""), {}))
        sample_trans = self.translated_data.get("Global", self.translated_data.get(next(iter(self.translated_data), ""), {}))

        if not sample_orig:
            messagebox.showwarning("Warning", "No extracted strings available for review.")
            return

        editor_win = TranslationEditorWindow(self, sample_orig, sample_trans)
        editor_win.focus()

    def repack_game_files(self):
        if not self.translated_data:
            messagebox.showerror("Error", "No translated data to repack.")
            return

        if self.detected_engine == "Unreal Engine" and self.target_locres_path:
            output_path = Path(self.target_locres_path).with_suffix(".locres.new")
            parser = UnrealLocresParser(self.target_locres_path)
            success = parser.pack_to_locres(self.translated_data, str(output_path))

            if success:
                self.log_message(f"Repacked Unreal binary to: {output_path.name}")
                messagebox.showinfo("Success", f"Repacked binary saved to:\n{output_path.name}")
            else:
                messagebox.showerror("Error", "Failed to repack file.")

        elif self.detected_engine in ["Unity", "Ren'Py", "Godot Engine"]:
            clean_name = self.detected_engine.lower().replace(" ", "_")
            output_file = Path(self.selected_folder) / f"{clean_name}_translated_output.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.translated_data, f, ensure_ascii=False, indent=4)

            self.log_message(f"{self.detected_engine} asset pack saved to: {output_file.name}")
            messagebox.showinfo("Success", f"Saved to:\n{output_file.name}")


if __name__ == "__main__":
    app = GameTranslatorApp()
    app.mainloop()