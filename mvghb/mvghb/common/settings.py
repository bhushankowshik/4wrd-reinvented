"""Runtime settings for mvghb. Reads from env."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv_once() -> None:
    """Load mvghb/.env into os.environ if present and not already loaded.

    Tiny loader — no external dotenv dependency. Lines like KEY=VALUE
    only; ignores comments and blanks. Existing env wins (env > .env).
    """
    if os.environ.get("_MVGHB_DOTENV_LOADED") == "1":
        return
    here = Path(__file__).resolve().parents[2]
    env_path = here / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    os.environ["_MVGHB_DOTENV_LOADED"] = "1"


_load_dotenv_once()


def _b64dec_strict(value: str, *, expected_len: int) -> bytes:
    raw = base64.b64decode(value, validate=True)
    if len(raw) != expected_len:
        raise ValueError(
            f"KEK decoded length {len(raw)} != expected {expected_len}"
        )
    return raw


@dataclass(frozen=True)
class Settings:
    gov_dsn: str
    kek: bytes
    system_version: str
    wal_dir: str

    @property
    def kek_id(self) -> str:
        # Stable identifier for a given KEK — first 8 bytes of SHA-256(KEK).
        import hashlib
        return hashlib.sha256(self.kek).hexdigest()[:16]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    kek_b64 = os.environ.get("MVGHB_KEK")
    if not kek_b64:
        raise RuntimeError(
            "MVGHB_KEK env var not set. Run `mvghb bootstrap init` to generate one."
        )
    kek = _b64dec_strict(kek_b64, expected_len=32)
    return Settings(
        gov_dsn=os.environ.get(
            "MVGHB_GOV_DSN",
            "postgresql+psycopg://noc:noc@localhost:5434/noc_gov",
        ),
        kek=kek,
        system_version=os.environ.get("MVGHB_SYSTEM_VERSION", "mvghb-w1-0.1.0"),
        wal_dir=os.environ.get("MVGHB_WAL_DIR", "/tmp/mvghb-wal"),
    )


def reset_settings_cache() -> None:
    get_settings.cache_clear()
