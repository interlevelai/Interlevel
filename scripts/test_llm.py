"""
Test LLM provider connections
"""
import sys
from pathlib import Path

# Add interlevel-poc directory to path
poc_dir = Path(__file__).parent.parent / "interlevel-poc"
sys.path.insert(0, str(poc_dir))

from src.llm.client import LLMClient
from config.settings import settings


def test_generate():
    """Test basic text generation"""
    print("\n" + "="*60)
    print("Testing Text Generation")
    print("="*60)

    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Model: {client.model_name}")

    prompt = "Write a Python function that adds two numbers. Include docstring."
    print(f"\nPrompt: {prompt}\n")

    try:
        response = client.generate(prompt, max_tokens=500)
        print(f"Response:\n{response}\n")
        print("✅ Generation test passed")
        return True
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False


def test_chat():
    """Test chat-style interaction"""
    print("\n" + "="*60)
    print("Testing Chat Interaction")
    print("="*60)

    client = LLMClient()

    messages = [
        {"role": "system", "content": "You are a helpful Python programming assistant."},
        {"role": "user", "content": "How do I read a JSON file in Python? Be concise."}
    ]

    print("Messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    try:
        response = client.chat(messages, max_tokens=300)
        print(f"\nResponse:\n{response}\n")
        print("✅ Chat test passed")
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False


def test_token_counting():
    """Test token counting"""
    print("\n" + "="*60)
    print("Testing Token Counting")
    print("="*60)

    client = LLMClient()

    text = "This is a test sentence to count tokens."
    tokens = client.count_tokens(text)

    print(f"Text: {text}")
    print(f"Estimated tokens: {tokens}")

    print("✅ Token counting test passed")
    return True


if __name__ == "__main__":
    print("="*60)
    print("  Interlevel POC - LLM Provider Test")
    print("="*60)
    print(f"  Provider: {settings.LLM_PROVIDER}")
    print("="*60)

    passed = 0
    failed = 0

    try:
        if test_generate():
            passed += 1
        else:
            failed += 1
            
        if test_chat():
            passed += 1
        else:
            failed += 1
            
        if test_token_counting():
            passed += 1
        else:
            failed += 1

        print("\n" + "="*60)
        print(f"  Test Results: {passed} passed, {failed} failed")
        if failed == 0:
            print("  ✅ All LLM tests passed!")
        else:
            print(f"  ⚠️  {failed} test(s) failed")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
