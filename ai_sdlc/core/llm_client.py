"""
LLM Client for AI-SDLC

Provides abstraction layer for multiple LLM providers with support for
Anthropic Claude, OpenAI GPT-4, Azure OpenAI, and Databricks Foundation Models.
"""

import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None


class LLMProvider(Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    DATABRICKS = "databricks"


@dataclass
class LLMResponse:
    """Response from LLM generation."""

    content: str
    model: str
    provider: str
    tokens_used: int
    cost_usd: float
    latency_seconds: float
    finish_reason: str
    metadata: Dict[str, Any]


class LLMClient:
    """
    Universal LLM client supporting multiple providers.

    Supports:
    - Anthropic Claude (recommended)
    - OpenAI GPT-4
    - Azure OpenAI
    - Databricks Foundation Models
    """

    # Token costs per 1K tokens (input/output)
    PRICING = {
        "claude-sonnet-4-5": (0.003, 0.015),
        "claude-opus-4-5": (0.015, 0.075),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-4": (0.03, 0.06),
        "gpt-3.5-turbo": (0.0005, 0.0015),
    }

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 8000,
        timeout_seconds: int = 120,
        **kwargs,
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider name (anthropic, openai, azure_openai, databricks)
            model: Model name (default depends on provider)
            api_key: API key (if None, reads from env vars)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            timeout_seconds: Request timeout
            **kwargs: Provider-specific arguments
        """
        self.provider = LLMProvider(provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.kwargs = kwargs

        # Set default model based on provider
        if model is None:
            model = self._get_default_model()
        self.model = model

        # Initialize provider client
        self.client = self._initialize_client(api_key)

        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            LLMProvider.ANTHROPIC: "claude-sonnet-4-5",
            LLMProvider.OPENAI: "gpt-4-turbo",
            LLMProvider.AZURE_OPENAI: "gpt-4-turbo",
            LLMProvider.DATABRICKS: "databricks-meta-llama-3-70b-instruct",
        }
        return defaults[self.provider]

    def _initialize_client(self, api_key: Optional[str]) -> Any:
        """Initialize provider-specific client."""
        if self.provider == LLMProvider.ANTHROPIC:
            if anthropic is None:
                raise ImportError(
                    "anthropic package not installed. Install with: pip install anthropic"
                )
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key required. Set ANTHROPIC_API_KEY env var."
                )
            return anthropic.Anthropic(api_key=api_key)

        elif self.provider == LLMProvider.OPENAI:
            if openai is None:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
            return openai.OpenAI(api_key=api_key)

        elif self.provider == LLMProvider.AZURE_OPENAI:
            if openai is None:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
            api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = self.kwargs.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
            if not api_key or not endpoint:
                raise ValueError(
                    "Azure OpenAI requires API key and endpoint. "
                    "Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT env vars."
                )
            return openai.AzureOpenAI(api_key=api_key, azure_endpoint=endpoint)

        elif self.provider == LLMProvider.DATABRICKS:
            # Databricks Foundation Models use OpenAI-compatible API
            if openai is None:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
            workspace_url = self.kwargs.get("workspace_url") or os.getenv(
                "DATABRICKS_HOST"
            )
            token = api_key or os.getenv("DATABRICKS_TOKEN")
            if not workspace_url or not token:
                raise ValueError(
                    "Databricks requires workspace URL and token. "
                    "Set DATABRICKS_HOST and DATABRICKS_TOKEN env vars."
                )
            return openai.OpenAI(
                api_key=token, base_url=f"{workspace_url}/serving-endpoints"
            )

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _rate_limit(self) -> None:
        """Implement simple rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate text using configured LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse with generated content and metadata
        """
        self._rate_limit()

        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens

        start_time = time.time()

        if self.provider == LLMProvider.ANTHROPIC:
            response = self._generate_anthropic(
                prompt, system_prompt, temperature, max_tokens
            )
        elif self.provider in (LLMProvider.OPENAI, LLMProvider.AZURE_OPENAI):
            response = self._generate_openai(
                prompt, system_prompt, temperature, max_tokens
            )
        elif self.provider == LLMProvider.DATABRICKS:
            response = self._generate_databricks(
                prompt, system_prompt, temperature, max_tokens
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        latency = time.time() - start_time
        response.latency_seconds = latency

        return response

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Generate using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {"model": self.model, "max_tokens": max_tokens, "messages": messages}

        if system_prompt:
            kwargs["system"] = system_prompt

        if temperature > 0:
            kwargs["temperature"] = temperature

        response = self.client.messages.create(**kwargs)

        content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = input_tokens + output_tokens

        # Calculate cost
        pricing = self.PRICING.get(self.model, (0.003, 0.015))
        cost = (input_tokens / 1000 * pricing[0]) + (output_tokens / 1000 * pricing[1])

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider.value,
            tokens_used=total_tokens,
            cost_usd=cost,
            latency_seconds=0.0,  # Will be set by caller
            finish_reason=response.stop_reason or "complete",
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_id": response.model,
            },
        )

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Generate using OpenAI or Azure OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout_seconds,
        )

        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Calculate cost
        pricing = self.PRICING.get(self.model, (0.01, 0.03))
        cost = (input_tokens / 1000 * pricing[0]) + (output_tokens / 1000 * pricing[1])

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider.value,
            tokens_used=total_tokens,
            cost_usd=cost,
            latency_seconds=0.0,
            finish_reason=response.choices[0].finish_reason,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_id": response.model,
            },
        )

    def _generate_databricks(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Generate using Databricks Foundation Models."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout_seconds,
        )

        content = response.choices[0].message.content
        total_tokens = getattr(response.usage, "total_tokens", 0)

        # Databricks pricing varies by model - use conservative estimate
        cost = total_tokens / 1000 * 0.001  # $0.001 per 1K tokens estimate

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider.value,
            tokens_used=total_tokens,
            cost_usd=cost,
            latency_seconds=0.0,
            finish_reason=response.choices[0].finish_reason,
            metadata={"model_id": response.model},
        )

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses rough approximation: 1 token ≈ 4 characters for English.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pricing = self.PRICING.get(self.model, (0.003, 0.015))
        return (input_tokens / 1000 * pricing[0]) + (output_tokens / 1000 * pricing[1])

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"LLMClient(provider={self.provider.value}, model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens})"
        )
