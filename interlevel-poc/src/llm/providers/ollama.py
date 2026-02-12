"""
Ollama LLM provider implementation
Uses local Ollama server for inference
"""
from typing import List, Dict
import requests
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from config.settings import settings
from src.llm.client import BaseLLMProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""

    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.model_name = self.model

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to Ollama server at {self.host}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.host}. "
                f"Is the server running? Start with: ollama serve"
            )

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using Ollama"""
        url = f"{self.host}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise TimeoutError("Ollama generation timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Chat using Ollama"""
        url = f"{self.host}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama chat timed out")
            raise TimeoutError("Ollama chat timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
