"""Tests for PolicyEngine."""

from prompt_injection_prevention.capability_manager import Capability
from prompt_injection_prevention.input_sanitizer import ThreatLevel
from prompt_injection_prevention.policy_engine import (
    Action,
    PolicyDecision,
    PolicyEngine,
    PolicyRule,
)
from prompt_injection_prevention.taint_tracker import TaintLabel


class TestPolicyEngine:
    def test_default_deny(self):
        engine = PolicyEngine(default_decision=PolicyDecision.DENY)
        action = Action(
            name="test",
            capability=Capability.FILE_READ,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.DENY

    def test_default_rules_block_critical(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="read",
            capability=Capability.FILE_READ,
            threat_level=ThreatLevel.CRITICAL,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.DENY

    def test_default_rules_quarantine_high(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="read",
            capability=Capability.FILE_READ,
            threat_level=ThreatLevel.HIGH,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.QUARANTINE

    def test_default_rules_allow_trusted(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="read",
            capability=Capability.FILE_READ,
            input_taint=TaintLabel.USER_INPUT,
            threat_level=ThreatLevel.NONE,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.ALLOW

    def test_default_rules_block_tainted_code_exec(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="exec",
            capability=Capability.CODE_EXECUTE,
            input_taint=TaintLabel.TOOL_OUTPUT,
            threat_level=ThreatLevel.NONE,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.DENY

    def test_default_rules_block_tainted_write(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="write",
            capability=Capability.FILE_WRITE,
            input_taint=TaintLabel.WEB_CONTENT,
            threat_level=ThreatLevel.NONE,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.DENY

    def test_default_rules_quarantine_tainted_email(self):
        engine = PolicyEngine()
        engine.add_default_rules()
        action = Action(
            name="send",
            capability=Capability.SEND_EMAIL,
            input_taint=TaintLabel.TOOL_OUTPUT,
            threat_level=ThreatLevel.NONE,
        )
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.QUARANTINE

    def test_custom_rule(self):
        engine = PolicyEngine()
        engine.add_rule(
            PolicyRule(
                name="allow_all",
                priority=0,
                decision=PolicyDecision.ALLOW,
                condition=lambda _: True,
                reason="Custom allow-all rule",
            )
        )
        action = Action(name="anything", capability=Capability.SHELL_EXECUTE)
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.ALLOW

    def test_priority_ordering(self):
        engine = PolicyEngine()
        engine.add_rule(
            PolicyRule(
                name="low_priority_allow",
                priority=100,
                decision=PolicyDecision.ALLOW,
            )
        )
        engine.add_rule(
            PolicyRule(
                name="high_priority_deny",
                priority=1,
                decision=PolicyDecision.DENY,
            )
        )
        action = Action(name="test", capability=Capability.FILE_READ)
        result = engine.evaluate(action)
        assert result.decision == PolicyDecision.DENY
        assert result.matching_rule is not None
        assert result.matching_rule.name == "high_priority_deny"

    def test_remove_rule(self):
        engine = PolicyEngine()
        engine.add_rule(
            PolicyRule(name="my_rule", priority=0, decision=PolicyDecision.ALLOW)
        )
        assert engine.remove_rule("my_rule")
        assert not engine.remove_rule("nonexistent")
