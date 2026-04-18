"""AgentInterface protocol — ensures uniform contract across
all agents and keeps the orchestrator decoupled from each
implementation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


InT = TypeVar("InT", bound=BaseModel)
OutT = TypeVar("OutT", bound=BaseModel)


class Agent(ABC, Generic[InT, OutT]):
    kind: str = "base"

    @abstractmethod
    def run(self, input: InT) -> OutT:  # noqa: A002
        """Run the agent. Implementations set output status
        appropriately for non-ok paths so the orchestrator
        can produce degraded recommendations (FR-B.1.4)."""
