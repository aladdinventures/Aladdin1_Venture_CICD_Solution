"""
AI Provider Factory
YouTube Automation System v2.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from typing import Optional, Dict, Type
from .base import AIProvider, AIProviderType
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider

class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    _providers: Dict[str, Type[AIProvider]] = {
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
    }
    
    @classmethod
    def create(
        cls,
        provider_name: str,
        **config
    ) -> AIProvider:
        """
        Create AI provider instance
        
        Args:
            provider_name: Name of the provider (openai, deepseek, ollama)
            **config: Provider-specific configuration
            
        Returns:
            AIProvider instance
            
        Example:
            # OpenAI
            provider = AIProviderFactory.create(
                'openai',
                api_key='sk-...',
                model='gpt-3.5-turbo'
            )
            
            # Ollama (self-hosted, free)
            provider = AIProviderFactory.create(
                'ollama',
                base_url='http://localhost:11434',
                model='llama2'
            )
            
            # DeepSeek (cost-effective)
            provider = AIProviderFactory.create(
                'deepseek',
                api_key='sk-...'
            )
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class(**config)
    
    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[AIProvider]
    ):
        """
        Register a custom AI provider
        
        Args:
            name: Provider name
            provider_class: Provider class (must inherit from AIProvider)
            
        Example:
            class MyCustomProvider(AIProvider):
                # Implementation
                pass
            
            AIProviderFactory.register_provider('custom', MyCustomProvider)
        """
        if not issubclass(provider_class, AIProvider):
            raise TypeError(
                f"{provider_class} must inherit from AIProvider"
            )
        
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def create_from_config(cls, config: dict) -> AIProvider:
        """
        Create provider from configuration dictionary
        
        Args:
            config: Configuration with 'provider' key and provider-specific keys
            
        Example:
            config = {
                'provider': 'openai',
                'api_key': 'sk-...',
                'model': 'gpt-3.5-turbo'
            }
            provider = AIProviderFactory.create_from_config(config)
        """
        if 'provider' not in config:
            raise ValueError("Configuration must include 'provider' key")
        
        provider_name = config.pop('provider')
        return cls.create(provider_name, **config)

# Convenience functions
def create_openai_provider(
    api_key: str,
    model: str = "gpt-3.5-turbo",
    **kwargs
) -> OpenAIProvider:
    """Create OpenAI provider"""
    return AIProviderFactory.create(
        'openai',
        api_key=api_key,
        model=model,
        **kwargs
    )

def create_ollama_provider(
    base_url: str = "http://localhost:11434",
    model: str = "llama2",
    **kwargs
) -> OllamaProvider:
    """Create Ollama provider (self-hosted, free)"""
    return AIProviderFactory.create(
        'ollama',
        base_url=base_url,
        model=model,
        **kwargs
    )

def create_best_available_provider(**kwargs) -> AIProvider:
    """
    Create the best available provider based on environment
    
    Priority:
    1. OpenAI (if API key available)
    2. DeepSeek (if API key available)
    3. Ollama (if server is running)
    
    Returns:
        AIProvider instance
    """
    import os
    
    # Try OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        return create_openai_provider(openai_key, **kwargs)
    
    # Try DeepSeek
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        return AIProviderFactory.create(
            'deepseek',
            api_key=deepseek_key,
            **kwargs
        )
    
    # Try Ollama
    try:
        import aiohttp
        import asyncio
        
        async def check_ollama():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        'http://localhost:11434/api/tags',
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        return response.status == 200
            except:
                return False
        
        if asyncio.run(check_ollama()):
            return create_ollama_provider(**kwargs)
    except:
        pass
    
    raise RuntimeError(
        "No AI provider available. Please set up one of:\n"
        "1. OpenAI: Set OPENAI_API_KEY environment variable\n"
        "2. DeepSeek: Set DEEPSEEK_API_KEY environment variable\n"
        "3. Ollama: Install and run Ollama (https://ollama.ai/)"
    )
