import gradio as gr
from backends import LlamaCppBackend, OllamaBackend
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize backends lazily to avoid loading heavy models immediately if not selected
backends = {
    "LlamaCPP (.gguf)": None, 
    "Ollama": None
}

def get_backend(backend_name: str):
    if backend_name == "LlamaCPP (.gguf)":
        if backends[backend_name] is None:
            logger.info("Initializing LlamaCppBackend...")
            backends[backend_name] = LlamaCppBackend(model_path=Config.LLAMA_MODEL_PATH)
        return backends[backend_name]
    elif backend_name == "Ollama":
        if backends[backend_name] is None:
            logger.info("Initializing OllamaBackend...")
            backends[backend_name] = OllamaBackend(api_url=Config.OLLAMA_API_URL, model_name=Config.OLLAMA_MODEL_NAME)
        return backends[backend_name]
    else:
        raise ValueError(f"Unknown backend: {backend_name}")

def translate_action(text: str, direction: str, backend_choice: str, rules: str, temperature: float, max_tokens: int):
    if not text or not text.strip():
        return "Please enter text to translate."

    if direction == "English to Thai":
        source_lang = "English"
        target_lang = "Thai"
    else:
        source_lang = "Thai"
        target_lang = "English"

    try:
        backend = get_backend(backend_choice)
        translated_text, elapsed, tps = backend.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            rules=rules,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return f"{translated_text}\n\n---\n⏱️ Time: {elapsed:.2f}s | ⚡ Speed: {tps:.2f} token/s"
    except Exception as e:
        logger.error(f"Error during translation action: {e}")
        return f"An error occurred: {e}"

# Build Gradio UI
js_code = """
function() {
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            let wrapper = document.querySelector('#translate_btn');
            if (wrapper) {
                let btn = wrapper.tagName === 'BUTTON' ? wrapper : wrapper.querySelector('button');
                if (btn) {
                    e.preventDefault();
                    btn.click();
                }
            }
        } else if (e.key === 'Delete') {
            let wrapper = document.querySelector('#clear_btn');
            if (wrapper) {
                let btn = wrapper.tagName === 'BUTTON' ? wrapper : wrapper.querySelector('button');
                if (btn) {
                    btn.click();
                }
            }
        }
    });
}
"""

with gr.Blocks(title="Typhoon Translate 1.5 Local") as demo:
    gr.Markdown("# Typhoon Translate 1.5 Local")
    gr.Markdown("A local, controllable translation interface for Thai ↔ English.")

    with gr.Row():
        direction_dropdown = gr.Dropdown(
            choices=["English to Thai", "Thai to English"], 
            value="English to Thai", 
            label="Translation Direction"
        )
        backend_dropdown = gr.Dropdown(
            choices=["LlamaCPP (.gguf)", "Ollama"], 
            value="LlamaCPP (.gguf)", 
            label="Backend Engine"
        )

    with gr.Row():
        with gr.Column():
            source_text = gr.Textbox(lines=10, label="Source Text", placeholder="Enter text here...")
        with gr.Column():
            translated_text = gr.Textbox(lines=10, label="Translated Text", interactive=False)

    with gr.Row():
        translate_btn = gr.Button("Translate", variant="primary", elem_id="translate_btn")
        clear_btn = gr.Button("Clear", elem_id="clear_btn")

    with gr.Accordion("Prompt Control & Rules", open=True):
        rules_text = gr.Textbox(
            lines=4, 
            label="Translation Rules", 
            placeholder="e.g., 1. Translate 'Apple' as 'แอปเปิ้ล'.\n2. Use formal tone."
        )

    with gr.Accordion("Advanced Settings", open=False):
        temperature_slider = gr.Slider(minimum=0.0, maximum=1.0, value=Config.DEFAULT_TEMPERATURE, step=0.05, label="Temperature")
        max_tokens_slider = gr.Slider(minimum=256, maximum=16384, value=Config.DEFAULT_MAX_TOKENS, step=256, label="Max New Tokens")

    # Event Listeners
    translate_btn.click(
        fn=translate_action,
        inputs=[source_text, direction_dropdown, backend_dropdown, rules_text, temperature_slider, max_tokens_slider],
        outputs=translated_text
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=[],
        outputs=[source_text, translated_text]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, js=js_code)
