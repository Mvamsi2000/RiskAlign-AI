from __future__ import annotations

import logging
from typing import Iterable, List, Mapping, MutableMapping

from fastapi import Request

from .provider import AIProviderError
from .resolve import ProviderResolutionError, resolve_provider

logger = logging.getLogger(__name__)

Message = Mapping[str, str]
Conversation = List[Message]


def chat_with_provider(
    request: Request | None,
    messages: Iterable[Message],
    *,
    tenant_config: Mapping[str, str] | None = None,
    namespace: str | None = None,
    extra: MutableMapping[str, object] | None = None,
) -> Mapping[str, object]:
    """Execute a chat completion with the resolved provider."""

    message_list: Conversation = [dict(message) for message in messages if message.get("role") and message.get("content")]  # type: ignore[arg-type]
    if not message_list:
        raise ValueError("At least one valid message is required")

    provider_id, provider = resolve_provider(request, tenant_config, namespace=namespace)
    logger.info("AI chat request via %s provider", provider_id)

    try:
        completion = provider.chat(message_list)
    except AIProviderError as exc:
        logger.warning("AI provider %s failed: %s", provider_id, exc)
        raise

    full_history: Conversation = message_list + [{"role": "assistant", "content": completion}]
    response: MutableMapping[str, object] = {
        "provider": provider_id,
        "messages": full_history,
    }
    if extra is not None:
        response.update(extra)
    return response


__all__ = ["chat_with_provider", "Message", "Conversation"]
