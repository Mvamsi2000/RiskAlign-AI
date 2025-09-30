"""AI provider interfaces and shared errors."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Mapping

Message = Mapping[str, str]


class AIProviderError(RuntimeError):
    """Raised when the underlying AI provider call fails."""


class AIProvider(ABC):
    """Common interface implemented by all AI providers."""

    @abstractmethod
    def chat(self, messages: List[Message], **kwargs: Any) -> str:
        """Execute a chat-style completion and return the content string."""

    @abstractmethod
    def name(self) -> str:
        """Return a human-friendly provider name."""
