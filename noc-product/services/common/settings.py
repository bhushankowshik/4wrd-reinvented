from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "noc-product"
    system_version: str = "e6a-0.1.0"
    sop_corpus_version: str = "v1"

    noc_data_dsn: str = "postgresql+psycopg://noc:noc@noc-data:5432/noc_data"
    noc_gov_dsn: str = "postgresql+psycopg://noc:noc@noc-gov:5432/noc_gov"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_archive: str = "noc-archive"
    minio_bucket_staging: str = "noc-staging"

    vault_addr: str = "http://vault:8200"
    vault_token: str = "dev-root-token"
    vault_kek_path: str = "secret/data/noc-gov/kek/current"

    oidc_issuer: str = "http://dex:5556/dex"
    oidc_client_id: str = "noc-reviewer"
    oidc_client_secret: str = "noc-reviewer-secret"
    oidc_redirect_uri: str = "http://localhost:8080/auth/callback"

    model_backend: str = "ollama"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_reasoning_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout_sec: int = 120
    ollama_keepalive_sec: int = 60

    chain_write_url: str = "http://chain-write:7001"
    chain_write_wal_dir: str = "/var/wal"
    chain_write_stub_namespace: str = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"

    mock_ctts_url: str = "http://mock-ctts:8001"
    ctts_poll_interval_sec: int = 15

    session_secret: str = "change-me-dev-only"
    session_sliding_hours: int = 8
    session_absolute_hours: int = 12

    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"
    otel_service_namespace: str = "noc-product"
    prometheus_port: int = 9464


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
