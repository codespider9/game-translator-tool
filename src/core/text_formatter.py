import arabic_reshaper
from bidi.algorithm import get_display


class ArabicTextFormatter:
    """Handles Arabic right-to-left shaping and bidi text formatting for unsupported game engines."""

    @staticmethod
    def reshape_text(text: str) -> str:
        """Reshapes and applies BiDi algorithm to raw Arabic strings."""
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception as e:
            print(f"Error shaping Arabic text: {e}")
            return text

    @staticmethod
    def process_dictionary(data: dict) -> dict:
        """Recursively processes dictionary strings to apply Arabic shaping."""
        formatted_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                formatted_data[key] = ArabicTextFormatter.process_dictionary(value)
            elif isinstance(value, str):
                formatted_data[key] = ArabicTextFormatter.reshape_text(value)
            else:
                formatted_data[key] = value
        return formatted_data