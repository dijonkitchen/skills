"""
Prompt Injection Prevention Skill

A defense framework for LLM-based agents inspired by the CaMeL
(CApability-based Machine Learning) paper. Implements data-control
separation, taint tracking, capability-based security, and policy
enforcement to protect against prompt injection attacks.

Key concepts from CaMeL:
- **Data-Control Separation**: Distinguishes trusted instructions (user)
  from untrusted data (tools, web, files).
- **Taint Tracking**: Tracks data provenance so untrusted content cannot
  influence control-flow decisions.
- **Capability-Based Security**: Each tool/action requires an explicit
  capability grant before execution.
- **Policy Enforcement**: Configurable policies define what actions are
  permitted given the taint status of their inputs.
- **Dual LLM Architecture**: Optionally routes trusted and untrusted
  content through separate processing paths.
"""

from prompt_injection_prevention.taint_tracker import (
    TaintedData,
    TaintLabel,
    TaintTracker,
)
from prompt_injection_prevention.capability_manager import (
    Capability,
    CapabilityManager,
)
from prompt_injection_prevention.input_sanitizer import (
    InputSanitizer,
    SanitizationResult,
    ThreatLevel,
)
from prompt_injection_prevention.policy_engine import (
    Action,
    PolicyDecision,
    PolicyEngine,
    PolicyRule,
)
from prompt_injection_prevention.dual_llm import DualLLMOrchestrator, LLMRole
from prompt_injection_prevention.camel_defense import CamelDefense, DefenseResult

__all__ = [
    "Action",
    "CamelDefense",
    "Capability",
    "CapabilityManager",
    "DefenseResult",
    "DualLLMOrchestrator",
    "InputSanitizer",
    "LLMRole",
    "PolicyDecision",
    "PolicyEngine",
    "PolicyRule",
    "SanitizationResult",
    "TaintedData",
    "TaintLabel",
    "TaintTracker",
    "ThreatLevel",
]

__version__ = "0.1.0"
