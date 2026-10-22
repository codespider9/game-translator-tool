# Universal Game Translator Tool 🎮🌐

An open-source, flexible desktop application designed to simplify game localization for modders and translators. It automatically detects game engines, extracts readable strings, and integrates with AI services (Google Gemini, OpenAI, Ollama) alongside traditional manual translation.

---

## Key Features ✨

- **Automatic Engine Detection:** Detects game engine types (Unreal Engine, Unity, Ren'Py, etc.) from game directories.
- **Unified Text Extraction:** Extracts hardcoded or packed texts into simple `JSON` / `CSV` formats.
- **AI Translation Router:** Context-aware AI translation via Gemini API, OpenAI API, or Local LLMs (Ollama) with tag protection.
- **Side-by-Side Editor:** Interactive GUI for reviewing and editing translations line-by-line.
- **Arabic & RTL Support:** Native Arabic text shaping and bidi support for engines that lack right-to-left layout capabilities.

---

## Project Roadmap 🗺️

- [x] Initial Repository Architecture Setup
- [ ] Unreal Engine (`.locres`) Extractor & Repacker (Phase 1 Target)
- [ ] Unity Engine Text Asset Extractor
- [ ] Gemini API Integration with Tag Safeguards
- [ ] CustomTkinter Graphical User Interface (GUI)

---

## Getting Started 🚀

### Prerequisites

- Python 3.10+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/codespider9/game-translator-tool.git](https://github.com/codespider9/game-translator-tool.git)
   cd game-translator-tool
