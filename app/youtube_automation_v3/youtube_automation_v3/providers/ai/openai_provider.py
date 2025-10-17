"""
OpenAI Provider Implementation
YouTube Automation System v2.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

import time
import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI, OpenAIError, RateLimitError, AuthenticationError
import tiktoken

from .base import (
    AIProvider,
    AIResponse,
    AIModelInfo,
    AIModelType,
    AIProviderType,
    AIProviderError,
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderTimeoutError
)

class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation"""
    
    # Model pricing (per 1K tokens)
    MODEL_PRICING = {
        "gpt-3.5-turbo": 0.002,
        "gpt-3.5-turbo-16k": 0.003,
        "gpt-4": 0.03,
        "gpt-4-32k": 0.06,
        "gpt-4-turbo": 0.01,
        "gpt-4o": 0.005,
        "gpt-4o-mini": 0.00015,
    }
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        org_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Default model to use
            org_id: Organization ID (optional)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, model, **kwargs)
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=org_id
        )
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _validate_config(self):
        """Validate configuration"""
        if not self.api_key:
            raise AIProviderAuthError("OpenAI API key is required")
        
        if self.model not in self.MODEL_PRICING:
            print(f"Warning: Unknown model {self.model}, pricing may be inaccurate")
    
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
        """Generate text using OpenAI"""
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=self.get_provider_name(),
                tokens_used=response.usage.total_tokens,
                cost=self.estimate_cost(response.usage.total_tokens),
                latency_ms=latency_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )
            
        except AuthenticationError as e:
            raise AIProviderAuthError(f"OpenAI authentication failed: {str(e)}")
        except RateLimitError as e:
            raise AIProviderRateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except OpenAIError as e:
            raise AIProviderError(f"OpenAI error: {str(e)}")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate chat completion"""
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=self.get_provider_name(),
                tokens_used=response.usage.total_tokens,
                cost=self.estimate_cost(response.usage.total_tokens),
                latency_ms=latency_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            )
            
        except AuthenticationError as e:
            raise AIProviderAuthError(f"OpenAI authentication failed: {str(e)}")
        except RateLimitError as e:
            raise AIProviderRateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except OpenAIError as e:
            raise AIProviderError(f"OpenAI error: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates structured JSON data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                **kwargs
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise AIProviderError(f"Failed to parse JSON response: {str(e)}")
        except OpenAIError as e:
            raise AIProviderError(f"OpenAI error: {str(e)}")
    
    def get_available_models(self) -> List[AIModelInfo]:
        """Get available OpenAI models"""
        return [
            AIModelInfo(
                name="gpt-3.5-turbo",
                type=AIModelType.CHAT,
                context_length=4096,
                cost_per_1k_tokens=0.002,
                supports_streaming=True,
                supports_functions=True,
                description="Fast and cost-effective"
            ),
            AIModelInfo(
                name="gpt-4",
                type=AIModelType.CHAT,
                context_length=8192,
                cost_per_1k_tokens=0.03,
                supports_streaming=True,
                supports_functions=True,
                description="Most capable model"
            ),
            AIModelInfo(
                name="gpt-4-turbo",
                type=AIModelType.CHAT,
                context_length=128000,
                cost_per_1k_tokens=0.01,
                supports_streaming=True,
                supports_functions=True,
                description="Latest GPT-4 with large context"
            ),
            AIModelInfo(
                name="gpt-4o-mini",
                type=AIModelType.CHAT,
                context_length=128000,
                cost_per_1k_tokens=0.00015,
                supports_streaming=True,
                supports_functions=True,
                description="Affordable and intelligent small model"
            ),
        ]
    
    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """Estimate cost for token count"""
        model_name = model or self.model
        cost_per_1k = self.MODEL_PRICING.get(model_name, 0.002)
        return (tokens / 1000) * cost_per_1k
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback: rough estimation
            return len(text) // 4
    
    def get_provider_type(self) -> AIProviderType:
        """Get provider type"""
        return AIProviderType.OPENAI
    
    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """Stream text generation (generator)"""
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except OpenAIError as e:
            raise AIProviderError(f"OpenAI streaming error: {str(e)}")
