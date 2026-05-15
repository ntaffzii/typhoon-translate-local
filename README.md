# Typhoon Translate Local

A local, controllable translation application for Thai ↔ English, utilizing the powerful `scb10x/typhoon-translate1.5-4b` model.

This project provides a modern, native **Desktop GUI** (built with PySide6) that allows you to easily interact with the translation model directly from your computer, ensuring absolute privacy and data security. 

![Application Preview](https://via.placeholder.com/800x500.png?text=Typhoon+Translate+Desktop+GUI) *(Add a screenshot of the app here)*

## ✨ Features
*   **100% Local & Private:** Your data never leaves your machine.
*   **Controllable Translations:** Provide strict custom rules (e.g., specific terminology, formal/informal tone, formatting) that the model will strictly follow.
*   **Native Desktop GUI:** A snappy, responsive desktop application built with Qt (PySide6) that works offline like a standard program.
*   **Dual Inference Backends:** 
    *   **Ollama (Recommended):** Connects to your local Ollama server for easy model management.
    *   **LlamaCPP (.gguf):** Runs `.gguf` files natively using CPU/GPU without needing external servers.
*   **Standalone Executable:** Can be packaged into a `.exe` file so you can run it on other Windows devices without installing Python.

---

## 🚀 Quick Start (Using Pre-built `.exe`)

If you just want to use the application without dealing with Python code:

1. Download the latest `TyphoonTranslate` release from the [Releases](https://github.com/your-username/repo-name/releases) page.
2. Extract the folder.
3. (If using `.gguf`) Place your `typhoon-translate1.5-4b.gguf` file inside the `models/` directory next to the executable.
4. Double-click `TyphoonTranslate.exe` to launch the app!

---

## 💻 Developer Setup

If you want to run from source, modify the code, or build the executable yourself.

### 1. Prerequisites & Environment

Ensure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/your-username/repo-name.git
cd repo-name

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install PySide6
```

### 2. Backend Engine Setup

You can choose between two backend engines to run the AI model:

#### Option A: Ollama (Recommended, Easiest)
1. Install [Ollama](https://ollama.com/).
2. Pull the Typhoon translation model:
   ```bash
   ollama run scb10x/typhoon-translate1.5-4b:latest
   ```
3. Start the application and select **"Ollama"** from the Backend Engine dropdown.

#### Option B: LlamaCPP (For `.gguf` files with GPU Acceleration)
1. Install the `llama-cpp-python` binding. 
   * *Windows Users:* To enable **GPU Acceleration (CUDA)** without installing C++ Build Tools, use the pre-compiled wheel for CUDA 12.4:
     ```bash
     pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
     ```
2. Download the `.gguf` model file from the [SCB 10X Hugging Face repo](https://huggingface.co/scb10x/typhoon-translate1.5-4b).
3. Create a `models/` folder in the project root and place the `.gguf` file there.
4. Start the application and select **"LlamaCPP (.gguf)"** from the Backend Engine dropdown.

### 3. Running the App
```bash
python gui_app.py
```

*(Note: The repository also contains `app.py`, which is a legacy web-based UI built with Gradio. You can run `python app.py` if you prefer a web-browser interface over the desktop GUI).*

---

## 📦 Building the Executable (.exe)

You can package the Python application into a standalone Windows executable using PyInstaller.

```bash
# Ensure your virtual environment is active
.\.venv\Scripts\activate

# Install pyinstaller if you haven't already
pip install pyinstaller

# Build the application
pyinstaller --noconsole --onedir --name "TyphoonTranslate" gui_app.py
```

The compiled application will be located in the `dist/TyphoonTranslate` folder. 

**Note on Distribution:** If you distribute the folder and expect users to use LlamaCPP, they must create a `models` folder inside the `dist/TyphoonTranslate` directory and place their `.gguf` file inside it.

---

## ⚙️ Configuration
You can customize defaults using a `.env` file in the root directory (or next to the `.exe`):

*   `LLAMA_MODEL_PATH`: Path to your `.gguf` model (default: `./models/typhoon-translate1.5-4b.gguf`)
*   `OLLAMA_API_URL`: URL to your Ollama server (default: `http://localhost:11434/api/generate`)
*   `OLLAMA_MODEL_NAME`: The model name used in Ollama (default: `typhoon-translate:latest`)

## 🙏 Acknowledgements
* The [Typhoon Translate 1.5](https://huggingface.co/scb10x/typhoon-translate1.5-4b) model was created and open-sourced by **SCB 10X**.
* Built with [PySide6](https://doc.qt.io/qtforpython-6/), [Ollama](https://ollama.com/), and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python).
