import sys
import ollama
from src import config

class LLMFormatter:
    def __init__(self):
        self.model = config.OLLAMA_MODEL
        self.system_prompt = config.SYSTEM_PROMPT

    def format_text(self, raw_text: str) -> str:
        """
        Takes raw text from STT and optionally uses Ollama to 
        format and remove filler words.
        If AI formatting is disabled in config, it returns raw text.
        """
        if not config.USE_AI_FORMATTING:
            return raw_text

        if not raw_text.strip():
            return ""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': f'[TRANSCRIPTION]\n{raw_text}\n[/TRANSCRIPTION]'}
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Ollama error: {e}")
            # Fallback to raw text if error occurs
            return raw_text

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        formatter = LLMFormatter()
        test_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "uhh I think I want to, like, test the LLM"
        print(f"Raw Text: {test_text}")
        print("Formatting...")
        result = formatter.format_text(test_text)
        print(f"Formatted Text: {result}")
