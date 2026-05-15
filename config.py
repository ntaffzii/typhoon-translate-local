import os
import sys
from dotenv import load_dotenv

# Path resolution for PyInstaller
def get_base_path():
    """
    Get the base path, whether running as a script or a PyInstaller bundle.
    """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    # Model configuration
    # Look for models directory relative to the executable/script location
    LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", os.path.join(BASE_DIR, "models", "typhoon-translate1.5-4b.i1-Q6_K.gguf"))
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "typhoon-translate:latest") # Adjust based on actual ollama registry name if available, or custom

    # App configuration
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_MAX_TOKENS = 8192
