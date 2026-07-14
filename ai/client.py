import os
import json
from abc import ABC, abstractmethod
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class BaseAIClient(ABC):
    @abstractmethod
    def extract_structured_data(self, text: str, prompt_template: str) -> dict:
        pass

class OpenAICompatibleClient(BaseAIClient):
    """
    Handles both standard OpenAI and local Odysseus models via base_url configuration.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("AI_API_KEY", "local-key")
        )
        self.model = os.getenv("AI_MODEL_NAME", "gpt-4-turbo")

    def extract_structured_data(self, text: str, prompt_template: str) -> dict:
        try:
            # We strictly enforce JSON output via response_format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI Extraction failed: {str(e)}")
            raise

class AIClientFactory:
    @staticmethod
    def get_client() -> BaseAIClient:
        provider = os.getenv("AI_PROVIDER", "odysseus").lower()
        if provider in ["odysseus", "openai"]:
            return OpenAICompatibleClient()
        # Additional providers (Claude, Gemini) can be injected here.
        raise ValueError(f"Unsupported AI Provider: {provider}")
