"""L1 — Harness core config.

Governs the four model tiers, token budgets, convergence rules, the
four bootstrap actors, and the chain connection surface. These are
stable across engagements; overrides happen in L2–L4.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# Model strings per the task knowledge contribution.
RESEARCH_MODEL = "claude-haiku-4-5-20251001"
PRODUCING_MODEL = "claude-sonnet-4-6"
ADVERSARIAL_MODEL = "claude-opus-4-6"


@dataclass(frozen=True)
class ModelTierConfig:
    """Model tier assignments per agent role."""
    research_model: str = RESEARCH_MODEL
    producing_model: str = PRODUCING_MODEL
    adversarial_model: str = ADVERSARIAL_MODEL

    research_max_tokens: int = 2048
    producing_max_tokens: int = 8192
    adversarial_max_tokens: int = 4096


@dataclass(frozen=True)
class TokenBudgetConfig:
    """Budgets applied when assembling Layer 3 packages."""
    producing_package_max_tokens: int = 50_000
    challenge_package_max_tokens: int = 20_000
    research_package_max_tokens: int = 10_000
    # Approximation factor (chars → tokens) used when enforcing budgets.
    chars_per_token: float = 4.0


@dataclass(frozen=True)
class ConvergenceRules:
    """Rules for convergence state transitions.

    Valid states are the INPUT-001 §3 trio. The `require_knowledge_in`
    set names the states that MUST carry a knowledge_contribution.
    Closing at `Exact` is the only state that satisfies gate discipline.
    """
    valid_states: tuple[str, ...] = ("Explorative", "Targeted", "Exact")
    require_knowledge_in: tuple[str, ...] = ("Explorative",)
    gate_close_state: str = "Exact"


@dataclass(frozen=True)
class ActorConfig:
    """Actor registry — the four bootstrap actors (MVGH-β Wave 1)."""
    human: str = "human"
    orchestrator: str = "orchestrator"
    producing_agent: str = "producing_agent"
    adversarial_agent: str = "adversarial_agent"
    research_agent: str = "producing_agent"  # Research writes under producing_agent actor (Haiku sibling); overrideable.


@dataclass(frozen=True)
class ChainConnectionConfig:
    """Chain substrate — uses MVGH-β Wave 1 settings by default."""
    gov_dsn_env: str = "MVGHB_GOV_DSN"
    kek_env: str = "MVGHB_KEK"
    wal_dir_env: str = "MVGHB_WAL_DIR"


@dataclass(frozen=True)
class HarnessCoreConfig:
    """L1 core config."""
    models: ModelTierConfig = field(default_factory=ModelTierConfig)
    token_budget: TokenBudgetConfig = field(default_factory=TokenBudgetConfig)
    convergence: ConvergenceRules = field(default_factory=ConvergenceRules)
    actors: ActorConfig = field(default_factory=ActorConfig)
    chain: ChainConnectionConfig = field(default_factory=ChainConnectionConfig)
    # Context-window for Layer 3 package (prior entries count).
    context_window: int = 5
    # Max PARTIAL/REJECTED loops per cycle before a cycle is abandoned.
    max_iterations: int = 3


DEFAULT_HARNESS_CORE = HarnessCoreConfig()
