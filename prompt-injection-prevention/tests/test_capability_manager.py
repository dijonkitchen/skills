"""Tests for CapabilityManager."""

import pytest

from prompt_injection_prevention.capability_manager import (
    Capability,
    CapabilityManager,
)


class TestCapabilityManager:
    def test_grant_and_check(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ)
        decision = mgr.check(Capability.FILE_READ, resource="/any/file")
        assert decision.allowed

    def test_check_without_grant_denies(self):
        mgr = CapabilityManager()
        decision = mgr.check(Capability.FILE_READ)
        assert not decision.allowed

    def test_scoped_grant(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ, resource_pattern="/safe/*")
        assert mgr.check(Capability.FILE_READ, resource="/safe/data.txt").allowed
        assert not mgr.check(Capability.FILE_READ, resource="/etc/passwd").allowed

    def test_revoke(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ)
        removed = mgr.revoke(Capability.FILE_READ)
        assert removed == 1
        assert not mgr.check(Capability.FILE_READ).allowed

    def test_revoke_all(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ)
        mgr.grant(Capability.WEB_FETCH)
        mgr.revoke_all()
        assert not mgr.has_capability(Capability.FILE_READ)
        assert not mgr.has_capability(Capability.WEB_FETCH)

    def test_require_raises_on_denial(self):
        mgr = CapabilityManager()
        with pytest.raises(PermissionError, match="denied"):
            mgr.require(Capability.SHELL_EXECUTE)

    def test_require_succeeds_when_granted(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.SHELL_EXECUTE)
        decision = mgr.require(Capability.SHELL_EXECUTE)
        assert decision.allowed

    def test_list_grants(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ, reason="test")
        grants = mgr.list_grants()
        assert len(grants) == 1
        assert grants[0].capability == Capability.FILE_READ

    def test_has_capability(self):
        mgr = CapabilityManager()
        assert not mgr.has_capability(Capability.FILE_READ)
        mgr.grant(Capability.FILE_READ)
        assert mgr.has_capability(Capability.FILE_READ)

    def test_multiple_grants_same_capability_different_scope(self):
        mgr = CapabilityManager()
        mgr.grant(Capability.FILE_READ, resource_pattern="/safe/*")
        mgr.grant(Capability.FILE_READ, resource_pattern="/tmp/*")
        assert mgr.check(Capability.FILE_READ, resource="/safe/a.txt").allowed
        assert mgr.check(Capability.FILE_READ, resource="/tmp/b.txt").allowed
        assert not mgr.check(Capability.FILE_READ, resource="/etc/passwd").allowed
