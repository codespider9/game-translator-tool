import customtkinter as ctk
from typing import Dict


class TranslationEditorWindow(ctk.CTkToplevel):
    """Side-by-side manual string review and edit window."""

    def __init__(self, parent, original_data: Dict[str, str], translated_data: Dict[str, str]):
        super().__init__(parent)

        self.title("Manual Translation Editor & Reviewer")
        self.geometry("900x600")

        self.original_data = original_data
        self.translated_data = translated_data.copy()
        self.entries = {}

        # Header Label
        self.lbl_header = ctk.CTkLabel(
            self, text="Translation Review & Fine-Tuning", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_header.pack(pady=10)

        # Scrollable Frame for String Rows
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self._build_grid_rows()

        # Save Action Button
        self.btn_save = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.btn_save.pack(pady=10)

    def _build_grid_rows(self):
        row = 0
        for key, orig_text in self.original_data.items():
            trans_text = self.translated_data.get(key, orig_text)

            # Original Text Display
            lbl_orig = ctk.CTkLabel(
                self.scroll_frame, text=orig_text, anchor="w", wraplength=380, justify="left"
            )
            lbl_orig.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

            # Editable Translated Text Entry
            entry_trans = ctk.CTkEntry(self.scroll_frame, width=400)
            entry_trans.insert(0, trans_text)
            entry_trans.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

            self.entries[key] = entry_trans
            row += 1

    def save_changes(self):
        for key, entry in self.entries.items():
            self.translated_data[key] = entry.get()
        print("Manual updates saved locally.")
        self.destroy()