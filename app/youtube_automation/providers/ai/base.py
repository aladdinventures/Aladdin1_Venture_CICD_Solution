"""
AI Provider Base Interface
YouTube Automation System v2.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AIModelType(Enum):
    """AI model types"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    EMBEDDING = "embedding"

class AIProviderType(Enum):
    """AI provider types"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class AIModelInfo:
    """AI model information"""
    name: str
    type: AIModelType
    context_length: int
    cost_per_1k_tokens: float
    supports_streaming: bool = False
    supports_functions: bool = False
    description: str = ""

class AIProvider(ABC):
    """Base interface for AI providers"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AI provider
        
        Args:
            api_key: API key for authentication
            model: Default model to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._validate_config()
    
    def _validate_config(self):
        """Validate provider configuration"""
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with generated text
        """
        pass
    
    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with generated message
        """
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured data (JSON) from prompt
        
        Args:
            prompt: Input prompt
            schema: JSON schema for output validation
            **kwargs: Additional parameters
            
        Returns:
            Dictionary matching the schema
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[AIModelInfo]:
        """
        Get list of available models
        
        Returns:
            List of AIModelInfo objects
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """
        Estimate cost for token count
        
        Args:
            tokens: Number of tokens
            model: Model name (uses default if not specified)
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        pass
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> AIResponse:
        """
        Generate text with automatic retry on failure
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number of retries
            **kwargs: Additional parameters
            
        Returns:
            AIResponse
        """
        import asyncio
        
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.generate_text(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
        
        raise last_error
    
    def get_provider_type(self) -> AIProviderType:
        """Get provider type"""
        return AIProviderType.CUSTOM
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.__class__.__name__.replace("Provider", "")
    
    def __repr__(self) -> str:
        return f"{self.get_provider_name()}(model={self.model})"

class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass

class AIProviderAuthError(AIProviderError):
    """Authentication error"""
    pass

class AIProviderRateLimitError(AIProviderError):
    """Rate limit exceeded"""
    pass

class AIProviderTimeoutError(AIProviderError):
    """Request timeout"""
    pass

class AIProviderInvalidRequestError(AIProviderError):
    """Invalid request"""
    pass
