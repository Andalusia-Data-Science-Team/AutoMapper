import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain.llms.base import LLM
from openai import OpenAI

class FireworksLLM(LLM):
    model: str
    api_key: str
    base_url: str = "https://api.fireworks.ai/inference/v1"
    temperature: float = 0
    top_p: float = 0

    @property
    def _llm_type(self) -> str:
        return "fireworks"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert in medical coding and service mapping."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            top_p=self.top_p
        )
        return response.choices[0].message.content

def get_fireworks_llm() -> FireworksLLM:
    """Factory method to load API key from .env and return configured LLM."""
    load_dotenv()
    api_key = os.getenv("FIREWORKS_NEW_API_KEY")
    if not api_key:
        raise ValueError("FIREWORKS_NEW_API_KEY not found in environment variables.")
    return FireworksLLM(
        model="accounts/fireworks/models/deepseek-v3-0324",
        api_key=api_key
    )