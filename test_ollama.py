#!/usr/bin/env python3
"""
Quick test script for Ollama integration
Tests if Ollama is accessible and can generate responses
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("OLLAMA INTEGRATION TEST")
print("=" * 60)

# Check configuration
ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'llama3:8b')

print(f"\nConfiguration:")
print(f"  OLLAMA_BASE_URL: {ollama_url}")
print(f"  OLLAMA_MODEL: {ollama_model}")

# Test Ollama server
print(f"\n1. Testing Ollama server...")
try:
    import requests
    response = requests.get(f"{ollama_url}/api/version", timeout=5)
    if response.status_code == 200:
        print(f"✅ Ollama server is running")
        print(f"   Version: {response.json().get('version', 'unknown')}")
    else:
        print(f"❌ Ollama server returned status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Cannot connect to Ollama server: {e}")
    print(f"\n   Make sure Ollama is installed and running:")
    print(f"   - Install: curl -fsSL https://ollama.com/install.sh | sh")
    print(f"   - Start: ollama serve")
    sys.exit(1)

# Check if model is available
print(f"\n2. Checking if model '{ollama_model}' is available...")
try:
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    models = [model['name'] for model in response.json().get('models', [])]

    if ollama_model in models or f"{ollama_model}:latest" in models:
        print(f"✅ Model '{ollama_model}' is available")
    else:
        print(f"❌ Model '{ollama_model}' not found")
        print(f"\n   Available models: {', '.join(models) if models else 'None'}")
        print(f"\n   Download the model:")
        print(f"   ollama pull {ollama_model}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking models: {e}")
    sys.exit(1)

# Test with OpenAI-compatible API
print(f"\n3. Testing OpenAI-compatible API...")
try:
    from openai import OpenAI

    client = OpenAI(
        base_url=ollama_url + '/v1',
        api_key='ollama'
    )

    print(f"   Sending test prompt...")
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Ollama!' in exactly those words."}
        ],
        temperature=0.3,
        max_tokens=50
    )

    answer = response.choices[0].message.content.strip()
    print(f"✅ Got response from Ollama!")
    print(f"   Response: {answer}")

except Exception as e:
    print(f"❌ Error testing API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test with actual JIRA ticket extraction
print(f"\n4. Testing JIRA ticket extraction with Ollama...")
try:
    from config import config
    from agents.extraction_agent import ExtractionAgent

    # Temporarily set provider to ollama
    original_provider = config.llm_provider
    config.llm_provider = 'ollama'

    llm_client = config.get_llm_client()
    agent = ExtractionAgent(llm_client, issue_type='task')

    test_text = "Create a login page with email and password fields"
    print(f"   Test input: '{test_text}'")

    result = agent.extract(test_text, "TEST")

    print(f"✅ Successfully extracted tickets!")
    print(f"   Epics: {len(result.epics)}")
    print(f"   Tasks: {sum(len(epic.tasks) for epic in result.epics)}")
    print(f"   Bugs: {len(result.bugs)}")
    print(f"   Stories: {len(result.stories)}")

    # Restore original provider
    config.llm_provider = original_provider

except Exception as e:
    print(f"❌ Error testing extraction: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print(f"\nOllama is working correctly! You can now use it by setting:")
print(f"  LLM_PROVIDER=ollama")
print(f"  OLLAMA_MODEL={ollama_model}")
print(f"\nTo switch providers, just change LLM_PROVIDER in .env to:")
print(f"  - 'openai' for OpenAI GPT-4")
print(f"  - 'anthropic' for Claude")
print(f"  - 'ollama' for local Llama 3")
