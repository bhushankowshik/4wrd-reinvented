"""Four-layer configuration system per INPUT-001 §5.

Stacks general → specific without re-implementation:

  L1 harness  →  L2 domain  →  L3 specialisation  →  L4 engagement

Later layers override earlier. The loader exposes one `HarnessConfig`
dataclass assembled from all four layers.
"""
from harness.config.harness_config import (
    HarnessCoreConfig,
    ModelTierConfig,
    TokenBudgetConfig,
    ConvergenceRules,
    ActorConfig,
    DEFAULT_HARNESS_CORE,
)
from harness.config.domain_config import DomainConfig, DEFAULT_DOMAIN
from harness.config.specialisation_config import (
    SpecialisationConfig,
    DEFAULT_SPECIALISATION,
)
from harness.config.engagement_config import (
    EngagementConfig,
    DEFAULT_ENGAGEMENT,
)
from harness.config.loader import HarnessConfig, load_config

__all__ = [
    "HarnessCoreConfig",
    "ModelTierConfig",
    "TokenBudgetConfig",
    "ConvergenceRules",
    "ActorConfig",
    "DomainConfig",
    "SpecialisationConfig",
    "EngagementConfig",
    "HarnessConfig",
    "DEFAULT_HARNESS_CORE",
    "DEFAULT_DOMAIN",
    "DEFAULT_SPECIALISATION",
    "DEFAULT_ENGAGEMENT",
    "load_config",
]
