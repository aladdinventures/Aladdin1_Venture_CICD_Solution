"""
Ollama Provider Implementation (Self-Hosted, Free)
YouTube Automation System v2.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

import time
import json
from typing import Dict, List, Optional, Any
import aiohttp

from .base import (
    AIProvider,
    AIResponse,
    AIModelInfo,
    AIModelType,
    AIProviderType,
    AIProviderError,
    AIProviderTimeoutError
)

class OllamaProvider(AIProvider):
    """
    Ollama self-hosted AI provider
    
    Ollama allows running LLMs locally:
    - Llama 2, Llama 3
    - Mistral, Mixtral
    - CodeLlama
    - And many more
    
    Benefits:
    - Completely free
    - No API costs
    - Privacy (data stays local)
    - No rate limits
    
    Setup:
    1. Install Ollama: https://ollama.ai/
    2. Pull a model: `ollama pull llama2`
    3. Run: `ollama serve`
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        **kwargs
    ):
        """
        Initialize Ollama provider
        
        Args:
            base_url: Ollama server URL
            model: Model name (e.g., llama2, mistral, codellama)
            **kwargs: Additional configuration
        """
        super().__init__(None, model, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.timeout = kwargs.get('timeout', 300)  # 5 minutes default
    
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
        """Generate text using Ollama"""
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    }
                }
                
                if stop:
                    payload["options"]["stop"] = stop
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AIProviderError(f"Ollama error: {error_text}")
                    
                    data = await response.json()
                    
                    latency_ms = (time.time() - start_time) * 1000
                    
                    return AIResponse(
                        content=data.get('response', ''),
                        model=self.model,
                        provider=self.get_provider_name(),
                        tokens_used=0,  # Ollama doesn't provide token count
                        cost=0.0,  # Self-hosted = FREE!
                        latency_ms=latency_ms,
                        metadata={
                            "done": data.get('done', False),
                            "context": data.get('context', []),
                            "total_duration": data.get('total_duration', 0),
                            "load_duration": data.get('load_duration', 0),
                            "prompt_eval_count": data.get('prompt_eval_count', 0),
                            "eval_count": data.get('eval_count', 0)
                        }
                    )
                    
        except aiohttp.ClientError as e:
            raise AIProviderError(f"Ollama connection error: {str(e)}")
        except asyncio.TimeoutError:
            raise AIProviderTimeoutError(f"Ollama request timed out after {self.timeout}s")
    
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
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AIProviderError(f"Ollama error: {error_text}")
                    
                    data = await response.json()
                    
                    latency_ms = (time.time() - start_time) * 1000
                    
                    return AIResponse(
                        content=data.get('message', {}).get('content', ''),
                        model=self.model,
                        provider=self.get_provider_name(),
                        tokens_used=0,
                        cost=0.0,  # FREE!
                        latency_ms=latency_ms,
                        metadata={
                            "done": data.get('done', False),
                            "total_duration": data.get('total_duration', 0)
                        }
                    )
                    
        except aiohttp.ClientError as e:
            raise AIProviderError(f"Ollama connection error: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        
        # Add JSON instruction to prompt
        json_prompt = f"""{prompt}

Please respond with valid JSON only, following this schema:
{json.dumps(schema, indent=2)}

JSON response:"""
        
        response = await self.generate_text(json_prompt, **kwargs)
        
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content.strip())
            
        except json.JSONDecodeError as e:
            raise AIProviderError(f"Failed to parse JSON from Ollama: {str(e)}")
    
    def get_available_models(self) -> List[AIModelInfo]:
        """Get available Ollama models"""
        return [
            AIModelInfo(
                name="llama2",
                type=AIModelType.CHAT,
                context_length=4096,
                cost_per_1k_tokens=0.0,  # FREE!
                supports_streaming=True,
                description="Meta's Llama 2 - General purpose"
            ),
            AIModelInfo(
                name="llama2:13b",
                type=AIModelType.CHAT,
                context_length=4096,
                cost_per_1k_tokens=0.0,
                supports_streaming=True,
                description="Llama 2 13B - Better quality"
            ),
            AIModelInfo(
                name="mistral",
                type=AIModelType.CHAT,
                context_length=8192,
                cost_per_1k_tokens=0.0,
                supports_streaming=True,
                description="Mistral 7B - Fast and capable"
            ),
            AIModelInfo(
                name="mixtral",
                type=AIModelType.CHAT,
                context_length=32768,
                cost_per_1k_tokens=0.0,
                supports_streaming=True,
                description="Mixtral 8x7B - Very capable"
            ),
            AIModelInfo(
                name="codellama",
                type=AIModelType.CODE_GENERATION,
                context_length=4096,
                cost_per_1k_tokens=0.0,
                supports_streaming=True,
                description="Specialized for code generation"
            ),
        ]
    
    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """Estimate cost (always 0 for self-hosted)"""
        return 0.0
    
    def count_tokens(self, text: str) -> int:
        """Rough token estimation"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def get_provider_type(self) -> AIProviderType:
        """Get provider type"""
        return AIProviderType.OLLAMA
    
    async def list_local_models(self) -> List[str]:
        """List models available on local Ollama instance"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data.get('models', [])]
                    return []
        except Exception:
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama library"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour for download
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """Stream text generation"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                                
        except Exception as e:
            raise AIProviderError(f"Ollama streaming error: {str(e)}")
