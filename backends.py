from abc import ABC, abstractmethod
import requests
import json
import logging
import time
import os
from prompt_manager import PromptManager
# Add CUDA to DLL search path for Windows (Python 3.8+)
# This must be done BEFORE importing llama_cpp
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin"
if os.name == 'nt' and os.path.exists(cuda_path):
    try:
        # Override CUDA_PATH to point to 12.4 for llama-cpp-python
        os.environ["CUDA_PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4"
        # Also add to PATH just in case
        if cuda_path not in os.environ["PATH"]:
            os.environ["PATH"] = cuda_path + os.pathsep + os.environ["PATH"]

        # Using a set to avoid adding the same directory multiple times if the module is reloaded
        if not hasattr(os, '_cuda_dll_added'):
            os.add_dll_directory(cuda_path)
            os._cuda_dll_added = True
    except Exception as e:
        print(f"Warning: Failed to add CUDA DLL directory: {e}")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationBackend(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str, rules: str = "", temperature: float = 0.2, max_tokens: int = 8192) -> tuple[str, float, float]:
        """Returns a tuple of (translated_text, time_taken_seconds, tokens_per_second)"""
        pass


class LlamaCppBackend(TranslationBackend):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.llm = None
        self._load_model()

    def _load_model(self):
        try:
            from llama_cpp import Llama
            logger.info(f"Loading LlamaCPP model from {self.model_path}")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=8192,  # Suggested by docs
                n_gpu_layers=-1, # Offload all layers to GPU
                n_threads=4, # Adjust based on CPU
                verbose=True # Keep logs clean
            )
            import llama_cpp
            if llama_cpp.llama_supports_gpu_offload():
                logger.info("GPU acceleration is ENABLED for LlamaCPP.")
            else:
                logger.info("GPU acceleration is DISABLED (CPU only) for LlamaCPP.")
            logger.info("LlamaCPP model loaded successfully.")
        except ImportError:
            logger.error("llama-cpp-python is not installed. Please install it.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def translate(self, text: str, source_lang: str, target_lang: str, rules: str = "", temperature: float = 0.2, max_tokens: int = 8192) -> tuple[str, float, float]:
        if not self.llm:
            return "Error: LlamaCPP model is not loaded. Check model path and requirements.", 0.0, 0.0

        prompt = PromptManager.get_prompt(text, source_lang, target_lang, rules)
        messages = PromptManager.format_chat_template(prompt)

        start_time = time.time()
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Extract completion tokens for speed calculation
            completion_tokens = response.get('usage', {}).get('completion_tokens', 0)
            tps = completion_tokens / elapsed if elapsed > 0 else 0.0
            
            result_text = response['choices'][0]['message']['content'].strip()
            return result_text, elapsed, tps
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return f"Translation Error: {e}", 0.0, 0.0


class OllamaBackend(TranslationBackend):
    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model_name: str = "scb10x/typhoon-translate1.5-4b:latest"):
        self.api_url = api_url
        self.model_name = model_name

    def translate(self, text: str, source_lang: str, target_lang: str, rules: str = "", temperature: float = 0.2, max_tokens: int = 8192) -> tuple[str, float, float]:
        prompt = PromptManager.get_prompt(text, source_lang, target_lang, rules)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 8192
            }
        }

        start_time = time.time()
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            text_out = data.get("response", "").strip()
            completion_tokens = data.get("eval_count", 0) # Ollama's returned metric for tokens generated
            tps = completion_tokens / elapsed if elapsed > 0 else 0.0
            
            return text_out, elapsed, tps
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama translation failed: {e}")
            return f"Translation Error (Ollama): Make sure Ollama is running and the model '{self.model_name}' is pulled.\nDetails: {e}", 0.0, 0.0
