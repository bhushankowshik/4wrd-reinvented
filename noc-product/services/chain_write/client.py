"""HTTP client for services that want to call Chain-Write
over the network rather than in-process.
"""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from services.common.settings import get_settings


class ChainWriteClient:
    def __init__(self, base_url: str | None = None, timeout_sec: float = 10.0) -> None:
        self._base = (base_url or get_settings().chain_write_url).rstrip("/")
        self._timeout = timeout_sec

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.5, max=4))
    def emit(
        self,
        entry_type: str,
        actor_id: str,
        actor_role: str,
        payload_ref: dict[str, Any],
        incident_id: UUID | None = None,
        sop_versions_pinned: list[dict[str, Any]] | None = None,
        class_enum: Literal["NORMAL", "OVERRIDE"] = "NORMAL",
        prev_chain_id: UUID | None = None,
    ) -> dict[str, Any]:
        resp = httpx.post(
            f"{self._base}/emit",
            json={
                "entry_type": entry_type,
                "actor_id": actor_id,
                "actor_role": actor_role,
                "incident_id": str(incident_id) if incident_id else None,
                "payload_ref": payload_ref,
                "sop_versions_pinned": sop_versions_pinned,
                "class_enum": class_enum,
                "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()
