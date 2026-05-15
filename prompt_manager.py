class PromptManager:
    """Handles the strict formatting required by Typhoon Translate 1.5"""

    @staticmethod
    def get_prompt(text: str, source_lang: str, target_lang: str, rules: str = "") -> str:
        """
        Generates the exact prompt string expected by the model.
        """
        if source_lang.lower() == "english" and target_lang.lower() == "thai":
            prompt = "Translate the following English text into Thai, strictly following the rules below and return only the translated text.\n"
        elif source_lang.lower() == "thai" and target_lang.lower() == "english":
            prompt = "Translate the following Thai text into English, strictly following the rules below and return only the translated text.\n"
        else:
            raise ValueError("Unsupported language pair. Must be English->Thai or Thai->English")

        if rules and rules.strip():
            prompt += f"Rules:\n{rules.strip()}\n"
        
        prompt += f"Source Text:\n\n{text.strip()}"
        
        return prompt

    @staticmethod
    def format_chat_template(prompt: str) -> list[dict]:
        """
        Formats the prompt into a generic chat message structure if needed by backends.
        The model documentation uses `apply_chat_template` with a system/user role, 
        but the example mainly shows a 'user' role containing the full prompt.
        """
        return [{"role": "user", "content": prompt}]
