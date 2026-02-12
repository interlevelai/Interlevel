"""
LLM client abstraction layer
Provides unified interface for different LLM providers
"""
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Unified LLM client interface"""

    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client with specified provider"""
        self.provider = provider or settings.LLM_PROVIDER
        self._client = None
        self._init_provider()

    def _init_provider(self):
        """Initialize the appropriate provider client"""
        logger.info(f"Initializing LLM provider: {self.provider}")

        if self.provider == "ollama":
            from src.llm.providers.ollama import OllamaProvider
            self._client = OllamaProvider()
        elif self.provider == "openai":
            from src.llm.providers.openai import OpenAIProvider
            self._client = OpenAIProvider()
        elif self.provider == "anthropic":
            from src.llm.providers.anthropic import AnthropicProvider
            self._client = AnthropicProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

        logger.info(f"LLM provider initialized: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text
        """
        logger.debug("Generating text", prompt_length=len(prompt), max_tokens=max_tokens)

        try:
            response = self._client.generate(prompt, max_tokens, temperature)
            logger.debug("Text generated successfully", response_length=len(response))
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Chat-style interaction with messages

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Assistant's response
        """
        logger.debug("Chat interaction", num_messages=len(messages))

        try:
            response = self._client.chat(messages, max_tokens, temperature)
            logger.debug("Chat response generated", response_length=len(response))
            return response
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        # This is a rough approximation
        return len(text) // 4

    @property
    def model_name(self) -> str:
        """Get current model name"""
        return self._client.model_name if hasattr(self._client, 'model_name') else "unknown"


class BaseLLMProvider:
    """Base class for LLM providers"""

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        raise NotImplementedError
