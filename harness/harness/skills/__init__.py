"""Skill registry — one per 4WRD reference skill (INPUT-001 §6).

Solutioning (6): S1 Problem Crystallisation, S2 Context and
Constraint Mapping, S3 Option Generation, S4 Option Evaluation,
S5 Solution Selection, S6 Solution Brief.

SDLC Execution (10): E1 Problem Definition, E2 Requirements, E3
Architecture, E4 Security and Compliance, E5 Data, E6 Build, E7
Test, E8 Deployment, E9 Operations, E10 Feedback and Learning.
"""
from harness.skills.s1_problem_crystallisation import S1_SKILL, Skill
from harness.skills.s2_context_constraint_mapping import S2_SKILL
from harness.skills.s3_option_generation import S3_SKILL
from harness.skills.s4_option_evaluation import S4_SKILL
from harness.skills.s5_solution_selection import S5_SKILL
from harness.skills.s6_solution_brief import S6_SKILL
from harness.skills.e1_problem_definition import E1_SKILL
from harness.skills.e2_requirements import E2_SKILL
from harness.skills.e3_architecture import E3_SKILL
from harness.skills.e4_security_compliance import E4_SKILL
from harness.skills.e5_data import E5_SKILL
from harness.skills.e6_build import E6_SKILL
from harness.skills.e7_test import E7_SKILL
from harness.skills.e8_deployment import E8_SKILL
from harness.skills.e9_operations import E9_SKILL
from harness.skills.e10_feedback_learning import E10_SKILL

SKILLS: dict[str, Skill] = {
    "S1": S1_SKILL,
    "S2": S2_SKILL,
    "S3": S3_SKILL,
    "S4": S4_SKILL,
    "S5": S5_SKILL,
    "S6": S6_SKILL,
    "E1": E1_SKILL,
    "E2": E2_SKILL,
    "E3": E3_SKILL,
    "E4": E4_SKILL,
    "E5": E5_SKILL,
    "E6": E6_SKILL,
    "E7": E7_SKILL,
    "E8": E8_SKILL,
    "E9": E9_SKILL,
    "E10": E10_SKILL,
}

__all__ = [
    "Skill",
    "SKILLS",
    "S1_SKILL", "S2_SKILL", "S3_SKILL", "S4_SKILL", "S5_SKILL", "S6_SKILL",
    "E1_SKILL", "E2_SKILL", "E3_SKILL", "E4_SKILL", "E5_SKILL",
    "E6_SKILL", "E7_SKILL", "E8_SKILL", "E9_SKILL", "E10_SKILL",
]
