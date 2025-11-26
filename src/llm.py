import os
from typing import Generator
from openai import OpenAI

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # Using a fast, conversational model
        self.model = "meta-llama/llama-3.3-70b-instruct" 

    def generate_response(self, prompt: str, history: list[dict] = None) -> Generator[str, None, None]:
        """
        Generate a streaming response from the LLM.
        Yields chunks of text.
        """
        messages = history if history else []
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            print(f"LLM Error: {e}")
            yield "Sorry, I encountered an error."
