"""
smart_router.py
---------------
Simplified router for openclaude — llama.cpp (llama-server) only.

All routing goes directly to the local llama-server instance started
by start.bat. No external API keys required.

Usage:
    from smart_router import SmartRouter
    router = SmartRouter()
    await router.initialize()
    result = await router.route(messages, model)

.env config:
    LLAMACPP_BASE_URL=http://localhost:8080   (default)
    LLAMACPP_PORT=8080                        (default)
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

LLAMACPP_BASE_URL = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8080")
LLAMACPP_PORT = int(os.getenv("LLAMACPP_PORT", "8080"))


@dataclass
class Provider:
    name: str
    ping_url: str
    cost_per_1k_tokens: float
    model: str
    latency_ms: float = 9999.0
    healthy: bool = True
    request_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 9999.0

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def api_key(self) -> Optional[str]:
        return None

    @property
    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

    def score(self, strategy: str = "balanced") -> float:
        if not self.healthy:
            return float("inf")
        return (self.avg_latency_ms / 1000.0) + (self.error_rate * 500)


def build_default_providers() -> list[Provider]:
    model = os.getenv("OPENAI_MODEL", "local-model")
    return [
        Provider(
            name="llamacpp",
            ping_url=f"{LLAMACPP_BASE_URL}/v1/models",
            cost_per_1k_tokens=0.0,
            model=model,
        ),
    ]


class SmartRouter:
    """Routes openclaude requests to the local llama-server instance."""

    def __init__(
        self,
        providers: Optional[list[Provider]] = None,
        strategy: Optional[str] = None,
        fallback_enabled: Optional[bool] = None,
    ):
        self.providers = providers or build_default_providers()
        self.strategy = strategy or os.getenv("ROUTER_STRATEGY", "balanced")
        self.fallback_enabled = (
            fallback_enabled if fallback_enabled is not None
            else os.getenv("ROUTER_FALLBACK", "true").lower() == "true"
        )
        self._initialized = False

    async def initialize(self) -> None:
        logger.info("SmartRouter: checking llama-server availability...")
        await asyncio.gather(
            *[self._ping_provider(p) for p in self.providers],
            return_exceptions=True,
        )
        available = [p for p in self.providers if p.healthy]
        if available:
            logger.info(f"SmartRouter ready. llama-server at {LLAMACPP_BASE_URL}")
        else:
            logger.warning(
                f"SmartRouter: llama-server not reachable at {LLAMACPP_BASE_URL}. "
                "Run start.bat to launch llama-server first."
            )
        self._initialized = True

    async def _ping_provider(self, provider: Provider) -> None:
        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(provider.ping_url)
                elapsed_ms = (time.monotonic() - start) * 1000
                if resp.status_code in (200, 401, 403):
                    provider.healthy = True
                    provider.latency_ms = elapsed_ms
                    provider.avg_latency_ms = elapsed_ms
                    logger.info(f"SmartRouter: llamacpp OK ({elapsed_ms:.0f}ms)")
                else:
                    provider.healthy = False
                    logger.warning(f"SmartRouter: llamacpp unhealthy (status={resp.status_code})")
        except Exception as e:
            provider.healthy = False
            logger.warning(f"SmartRouter: llamacpp unreachable — {e}")

    def select_provider(self, is_large_request: bool = False) -> Optional[Provider]:
        available = [p for p in self.providers if p.healthy]
        return min(available, key=lambda p: p.score(self.strategy)) if available else None

    def get_model_for_provider(
        self,
        provider: Provider,
        claude_model: str,
        is_large_request: bool = False,
    ) -> str:
        return provider.model

    def is_large_request(self, messages: list[dict]) -> bool:
        return sum(len(str(m.get("content", ""))) for m in messages) > 2000

    def _update_latency(self, provider: Provider, duration_ms: float) -> None:
        alpha = 0.3
        provider.avg_latency_ms = alpha * duration_ms + (1 - alpha) * provider.avg_latency_ms

    async def route(
        self,
        messages: list[dict],
        claude_model: str = "claude-sonnet",
        attempt: int = 0,
        exclude_providers: Optional[list[str]] = None,
    ) -> dict:
        if not self._initialized:
            await self.initialize()

        available = [
            p for p in self.providers
            if p.healthy and (not exclude_providers or p.name not in exclude_providers)
        ]

        if not available:
            raise RuntimeError(
                f"SmartRouter: llama-server not available at {LLAMACPP_BASE_URL}. "
                "Run start.bat to launch it automatically."
            )

        provider = available[0]
        model = self.get_model_for_provider(
            provider, claude_model,
            is_large_request=self.is_large_request(messages),
        )
        logger.debug(f"SmartRouter: routing to llamacpp/{model}")
        return {
            "provider": provider.name,
            "model": model,
            "api_key": "none",
            "base_url": LLAMACPP_BASE_URL,
            "provider_object": provider,
        }

    async def record_result(
        self, provider_name: str, success: bool, duration_ms: float,
    ) -> None:
        provider = next((p for p in self.providers if p.name == provider_name), None)
        if not provider:
            return
        provider.request_count += 1
        if success:
            self._update_latency(provider, duration_ms)
        else:
            provider.error_count += 1
            if provider.request_count >= 3 and provider.error_rate > 0.7:
                logger.warning(f"SmartRouter: llamacpp error rate {provider.error_rate:.0%}, marking unhealthy")
                provider.healthy = False
                asyncio.create_task(self._recheck_provider(provider, delay=60))

    async def _recheck_provider(self, provider: Provider, delay: float = 60) -> None:
        await asyncio.sleep(delay)
        await self._ping_provider(provider)
        if provider.healthy:
            logger.info("SmartRouter: llamacpp recovered")

    def status(self) -> list[dict]:
        return [
            {
                "provider": p.name,
                "healthy": p.healthy,
                "configured": p.is_configured,
                "latency_ms": round(p.avg_latency_ms, 1),
                "cost_per_1k": p.cost_per_1k_tokens,
                "requests": p.request_count,
                "errors": p.error_count,
                "error_rate": f"{p.error_rate:.1%}",
                "base_url": LLAMACPP_BASE_URL,
                "score": round(p.score(self.strategy), 3) if p.healthy else "N/A",
            }
            for p in self.providers
        ]