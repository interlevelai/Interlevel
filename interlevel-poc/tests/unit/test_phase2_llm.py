"""
Phase 2: LLM Integration - Unit Tests
Tests for LLM client and Ollama provider
"""
import pytest


# LLM Client Tests (TASK-201)
def test_llm_client_initialization():
    """Test LLM client initializes with Ollama provider"""
    from src.llm.client import LLMClient

    # This will test Ollama connection
    try:
        client = LLMClient(provider="ollama")
        assert client is not None
        assert client.provider == "ollama"
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_llm_client_model_name():
    """Test getting model name from client"""
    from src.llm.client import LLMClient

    try:
        client = LLMClient(provider="ollama")
        assert client.model_name is not None
        assert len(client.model_name) > 0
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_llm_client_token_counting():
    """Test token counting estimation"""
    from src.llm.client import LLMClient

    try:
        client = LLMClient(provider="ollama")
        text = "This is a test sentence"
        token_count = client.count_tokens(text)

        # Rough check: ~4 characters per token
        assert token_count > 0
        assert token_count < len(text)
    except ConnectionError:
        pytest.skip("Ollama server not running")


# Ollama Provider Tests (TASK-202)
def test_ollama_provider_initialization():
    """Test Ollama provider initializes correctly"""
    from src.llm.providers.ollama import OllamaProvider

    try:
        provider = OllamaProvider()
        assert provider is not None
        assert provider.host == "http://localhost:11434"
        assert provider.model == "codellama"
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_ollama_provider_connection():
    """Test Ollama provider can connect to server"""
    from src.llm.providers.ollama import OllamaProvider

    try:
        provider = OllamaProvider()
        # If we get here, connection succeeded
        assert provider.host is not None
    except ConnectionError as e:
        pytest.skip(f"Ollama server not running: {e}")


def test_ollama_provider_model_name():
    """Test Ollama provider has model name"""
    from src.llm.providers.ollama import OllamaProvider

    try:
        provider = OllamaProvider()
        assert provider.model_name == "codellama"
    except ConnectionError:
        pytest.skip("Ollama server not running")


@pytest.mark.integration
def test_ollama_provider_generate():
    """Test Ollama can generate text (slow, requires Ollama running)"""
    from src.llm.providers.ollama import OllamaProvider

    try:
        provider = OllamaProvider()
        response = provider.generate("Say hello", max_tokens=20, temperature=0.5)

        assert response is not None
        assert len(response) > 0
    except ConnectionError:
        pytest.skip("Ollama server not running")


@pytest.mark.integration
def test_ollama_provider_chat():
    """Test Ollama chat functionality (slow, requires Ollama running)"""
    from src.llm.providers.ollama import OllamaProvider

    try:
        provider = OllamaProvider()
        messages = [{"role": "user", "content": "Say hello"}]
        response = provider.chat(messages, max_tokens=20, temperature=0.5)

        assert response is not None
        assert len(response) > 0
    except ConnectionError:
        pytest.skip("Ollama server not running")
