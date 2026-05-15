import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QPushButton, QSlider, QGroupBox,
    QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from backends import LlamaCppBackend, OllamaBackend
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class TranslatorWorker(QThread):
    finished = Signal(str, float, float)
    error = Signal(str)

    def __init__(self, text, source_lang, target_lang, backend_choice, rules, temp, max_tokens):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.backend_choice = backend_choice
        self.rules = rules
        self.temp = temp
        self.max_tokens = max_tokens

    def run(self):
        try:
            backend = get_backend(self.backend_choice)
            result, elapsed, tps = backend.translate(
                text=self.text,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                rules=self.rules,
                temperature=self.temp,
                max_tokens=self.max_tokens
            )
            self.finished.emit(result, elapsed, tps)
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typhoon Translate 1.5 Local")
        self.resize(1000, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        title_label = QLabel("Typhoon Translate 1.5 Local")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("A local, controllable translation interface for Thai ↔ English.")
        main_layout.addWidget(subtitle_label)

        # Controls Row
        controls_layout = QHBoxLayout()
        
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["English to Thai", "Thai to English"])
        controls_layout.addWidget(QLabel("Translation Direction:"))
        controls_layout.addWidget(self.direction_combo)

        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["LlamaCPP (.gguf)", "Ollama"])
        controls_layout.addWidget(QLabel("Backend Engine:"))
        controls_layout.addWidget(self.backend_combo)
        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        # Splitter for Source and Translated Text
        splitter = QSplitter(Qt.Horizontal)
        
        # Source Text Container
        source_container = QWidget()
        source_layout = QVBoxLayout(source_container)
        source_layout.setContentsMargins(0,0,0,0)
        
        src_header_layout = QHBoxLayout()
        src_header_layout.addWidget(QLabel("Source Text"))
        src_header_layout.addStretch()
        self.src_copy_btn = QPushButton("Copy")
        self.src_copy_btn.setMaximumWidth(80)
        self.src_copy_btn.clicked.connect(self.copy_source)
        src_header_layout.addWidget(self.src_copy_btn)
        source_layout.addLayout(src_header_layout)
        
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("Enter text here...")
        source_layout.addWidget(self.source_text)
        splitter.addWidget(source_container)

        # Translated Text Container
        translated_container = QWidget()
        translated_layout = QVBoxLayout(translated_container)
        translated_layout.setContentsMargins(0,0,0,0)
        
        tgt_header_layout = QHBoxLayout()
        tgt_header_layout.addWidget(QLabel("Translated Text"))
        tgt_header_layout.addStretch()
        
        self.metrics_label = QLabel("")
        self.metrics_label.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-right: 10px;")
        tgt_header_layout.addWidget(self.metrics_label)
        
        self.tgt_copy_btn = QPushButton("Copy")
        self.tgt_copy_btn.setMaximumWidth(80)
        self.tgt_copy_btn.clicked.connect(self.copy_translated)
        tgt_header_layout.addWidget(self.tgt_copy_btn)
        translated_layout.addLayout(tgt_header_layout)
        
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        translated_layout.addWidget(self.translated_text)
        splitter.addWidget(translated_container)

        main_layout.addWidget(splitter)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.translate_btn = QPushButton("Translate")
        self.translate_btn.setDefault(True)
        self.translate_btn.setStyleSheet("background-color: #2c3e50; color: white; padding: 8px; font-weight: bold;")
        self.translate_btn.clicked.connect(self.on_translate_clicked)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        
        action_layout.addWidget(self.translate_btn)
        action_layout.addWidget(self.clear_btn)
        main_layout.addLayout(action_layout)

        # Prompt Control & Rules
        rules_group = QGroupBox("Prompt Control & Rules")
        rules_layout = QVBoxLayout()
        self.rules_text = QTextEdit()
        self.rules_text.setPlaceholderText("e.g., 1. Translate 'Apple' as 'แอปเปิ้ล'.\n2. Use formal tone.")
        self.rules_text.setMaximumHeight(80)
        rules_layout.addWidget(self.rules_text)
        rules_group.setLayout(rules_layout)
        main_layout.addWidget(rules_group)

        # Advanced Settings
        adv_group = QGroupBox("Advanced Settings")
        adv_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100) # 0 to 1.0 represented as 0-100
        self.temp_slider.setValue(int(Config.DEFAULT_TEMPERATURE * 100))
        self.temp_label = QLabel(str(Config.DEFAULT_TEMPERATURE))
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/100.0:.2f}"))
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        adv_layout.addLayout(temp_layout)

        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max New Tokens:"))
        self.tokens_slider = QSlider(Qt.Horizontal)
        self.tokens_slider.setRange(256, 16384)
        self.tokens_slider.setSingleStep(256)
        self.tokens_slider.setValue(Config.DEFAULT_MAX_TOKENS)
        self.tokens_label = QLabel(str(Config.DEFAULT_MAX_TOKENS))
        self.tokens_slider.valueChanged.connect(lambda v: self.tokens_label.setText(str(v)))
        tokens_layout.addWidget(self.tokens_slider)
        tokens_layout.addWidget(self.tokens_label)
        adv_layout.addLayout(tokens_layout)

        adv_group.setLayout(adv_layout)
        main_layout.addWidget(adv_group)

        self.worker = None

        # Keyboard Shortcuts
        self.shortcut_translate_return = QShortcut(QKeySequence("Return"), self)
        self.shortcut_translate_return.activated.connect(self.on_translate_clicked)
        
        self.shortcut_translate_enter = QShortcut(QKeySequence("Enter"), self)
        self.shortcut_translate_enter.activated.connect(self.on_translate_clicked)

        self.shortcut_clear = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_clear.activated.connect(self.on_clear_clicked)

    def copy_source(self):
        QApplication.clipboard().setText(self.source_text.toPlainText())

    def copy_translated(self):
        QApplication.clipboard().setText(self.translated_text.toPlainText())

    def on_translate_clicked(self):
        text = self.source_text.toPlainText()
        if not text.strip():
            self.translated_text.setPlainText("Please enter text to translate.")
            return

        self.translate_btn.setEnabled(False)
        self.translate_btn.setText("Translating...")
        self.translated_text.setPlainText("Translating... Please wait.")
        self.metrics_label.setText("")

        direction = self.direction_combo.currentText()
        if direction == "English to Thai":
            source_lang = "English"
            target_lang = "Thai"
        else:
            source_lang = "Thai"
            target_lang = "English"

        backend_choice = self.backend_combo.currentText()
        rules = self.rules_text.toPlainText()
        temp = self.temp_slider.value() / 100.0
        max_tokens = self.tokens_slider.value()

        self.worker = TranslatorWorker(text, source_lang, target_lang, backend_choice, rules, temp, max_tokens)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def on_translation_finished(self, result, elapsed, tps):
        self.translated_text.setPlainText(result)
        self.metrics_label.setText(f"⏱️ {elapsed:.2f}s | ⚡ {tps:.2f} token/s")
        self.reset_translate_btn()

    def on_translation_error(self, err_msg):
        self.translated_text.setPlainText(f"An error occurred:\n{err_msg}")
        self.metrics_label.setText("")
        self.reset_translate_btn()
        
    def reset_translate_btn(self):
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("Translate")

    def on_clear_clicked(self):
        self.source_text.clear()
        self.translated_text.clear()
        self.metrics_label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern darkish fusion style to look consistent
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
