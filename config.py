"""
Configuration management for JIRA Ticket Generator

Loads settings from .env file using python-dotenv
"""

import os
from typing import Optional, Literal
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

LLMProvider = Literal['openai', 'anthropic', 'ollama']


class Config:
    """Application configuration"""

    # Jira Configuration
    jira_url: str = os.getenv('JIRA_URL', '')
    jira_email: str = os.getenv('JIRA_EMAIL', '')
    jira_api_token: str = os.getenv('JIRA_API_TOKEN', '')
    jira_project: str = os.getenv('DEFAULT_PROJECT_KEY', '')

    # LLM Configuration
    llm_provider: LLMProvider = os.getenv('LLM_PROVIDER', 'openai').lower()  # type: ignore
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'llama3:8b')
    llm_model: str = os.getenv('LLM_MODEL', 'gpt-4-turbo')

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate required configuration

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check Jira config
        if not cls.jira_url:
            errors.append("JIRA_URL not set in .env")
        if not cls.jira_email:
            errors.append("JIRA_EMAIL not set in .env")
        if not cls.jira_api_token:
            errors.append("JIRA_API_TOKEN not set in .env")

        # Check LLM config
        if cls.llm_provider == 'openai' and not cls.openai_api_key:
            errors.append("OPENAI_API_KEY not set in .env (LLM_PROVIDER=openai)")
        elif cls.llm_provider == 'anthropic' and not cls.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY not set in .env (LLM_PROVIDER=anthropic)")
        elif cls.llm_provider == 'ollama' and not cls.ollama_base_url:
            errors.append("OLLAMA_BASE_URL not set in .env (LLM_PROVIDER=ollama)")

        if cls.llm_provider not in ['openai', 'anthropic', 'ollama']:
            errors.append(f"Invalid LLM_PROVIDER: {cls.llm_provider} (must be 'openai', 'anthropic', or 'ollama')")

        return errors

    @classmethod
    def get_llm_client(cls):
        """
        Get initialized LLM client based on provider

        Returns:
            OpenAI, Anthropic, or Ollama client instance
        """
        if cls.llm_provider == 'openai':
            try:
                from openai import OpenAI
                return OpenAI(api_key=cls.openai_api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        elif cls.llm_provider == 'anthropic':
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=cls.anthropic_api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        elif cls.llm_provider == 'ollama':
            try:
                from openai import OpenAI
                # Ollama uses OpenAI-compatible API
                return OpenAI(
                    base_url=cls.ollama_base_url + '/v1',
                    api_key='ollama'  # Ollama doesn't require a real API key
                )
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        else:
            raise ValueError(f"Invalid LLM provider: {cls.llm_provider}")

    @classmethod
    def has_llm_configured(cls) -> bool:
        """Check if LLM is properly configured"""
        if cls.llm_provider == 'openai':
            return bool(cls.openai_api_key)
        elif cls.llm_provider == 'anthropic':
            return bool(cls.anthropic_api_key)
        elif cls.llm_provider == 'ollama':
            return bool(cls.ollama_base_url)
        return False


# Singleton instance
config = Config()
