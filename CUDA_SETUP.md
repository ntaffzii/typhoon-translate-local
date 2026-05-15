# GPU Acceleration Setup Guide

To enable GPU acceleration for the `LlamaCPP` backend, your system must match the CUDA versions used to pre-compile the `llama-cpp-python` wheels. Currently, the most recent pre-compiled wheels require **CUDA 12.4**.

The application is configured to automatically detect and use CUDA 12.4 if installed in the default directory (`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4`).

## Setup Options

### Option 1: NVIDIA GPU (Recommended)
1.  **Install CUDA Toolkit 12.4:** Download and install from the [NVIDIA Archive](https://developer.nvidia.com/cuda-12-4-0-download-archive). You can have multiple versions of CUDA installed side-by-side.
2.  **Install GPU Backend:**
    ```bash
    .\.venv\Scripts\activate
    pip uninstall -y llama-cpp-python
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --no-cache-dir
    ```
3.  **Verify:** Run the app. You should see `GPU acceleration is ENABLED for LlamaCPP` in the logs.

### Option 2: AMD GPU (Vulkan)
If you have an AMD GPU (like Radeon 760M), use the **Ollama** backend:
1.  **Install Ollama.**
2.  **Enable Vulkan:** Set a user environment variable `OLLAMA_VULKAN` to `1`.
3.  **Restart Ollama** and select "Ollama" as the backend in the app.

### Option 3: Manual Build (For CUDA 13.x+)
If you must use a different CUDA version, you must build from source:
1.  Install **Visual Studio 2022 Build Tools** (with "Desktop development with C++").
2.  Install **CMake**.
3.  Run:
    ```bash
    set CMAKE_ARGS=-DGGML_CUDA=on
    set FORCE_CMAKE=1
    pip install llama-cpp-python --no-cache-dir
    ```

## Building the Executable
When using PyInstaller, you must explicitly include the `llama.dll` and ensure CUDA 12.4 is prioritized:

```bash
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin;" + $env:PATH
pyinstaller --noconsole --onedir --name "TyphoonTranslate" --clean -y --add-binary ".venv\Lib\site-packages\llama_cpp\lib\llama.dll;." gui_app.py
```

## Troubleshooting
-   **Phantom GPU:** If your NVIDIA GPU isn't detected, ensure your laptop is plugged into power and drivers are updated.
-   **DLL Load Error:** The app handles this programmatically, but ensure CUDA 12.4 is installed to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4`.
