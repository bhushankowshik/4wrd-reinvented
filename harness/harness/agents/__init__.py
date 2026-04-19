"""Claude Agent SDK subagents — Research + Producing + Adversarial."""
from harness.agents.adversarial_agent import (
    AdversarialAgent,
    AdversarialOutput,
    Challenge,
)
from harness.agents.producing_agent import ProducingAgent, ProducingOutput
from harness.agents.research_agent import (
    EMPTY_RESEARCH,
    ResearchAgent,
    ResearchOutput,
    should_invoke as should_invoke_research,
)

__all__ = [
    "AdversarialAgent",
    "AdversarialOutput",
    "Challenge",
    "ProducingAgent",
    "ProducingOutput",
    "ResearchAgent",
    "ResearchOutput",
    "EMPTY_RESEARCH",
    "should_invoke_research",
]
