"""Tests for TaintTracker."""

import pytest

from prompt_injection_prevention.taint_tracker import (
    TaintedData,
    TaintLabel,
    TaintTracker,
)


class TestTaintLabel:
    def test_user_input_is_trusted(self):
        assert TaintLabel.USER_INPUT.is_trusted

    def test_none_is_trusted(self):
        assert TaintLabel.NONE.is_trusted

    def test_tool_output_is_untrusted(self):
        assert TaintLabel.TOOL_OUTPUT.is_untrusted

    def test_web_content_is_untrusted(self):
        assert TaintLabel.WEB_CONTENT.is_untrusted

    def test_combined_untrusted_labels(self):
        combined = TaintLabel.TOOL_OUTPUT | TaintLabel.WEB_CONTENT
        assert combined.is_untrusted

    def test_user_input_combined_with_tool_output_is_untrusted(self):
        combined = TaintLabel.USER_INPUT | TaintLabel.TOOL_OUTPUT
        assert combined.is_untrusted


class TestTaintedData:
    def test_trusted_data(self):
        td = TaintedData(value="hello", labels=TaintLabel.USER_INPUT)
        assert td.is_trusted
        assert not td.is_tainted

    def test_tainted_data(self):
        td = TaintedData(value="hello", labels=TaintLabel.TOOL_OUTPUT)
        assert td.is_tainted
        assert not td.is_trusted

    def test_with_additional_label(self):
        td = TaintedData(value="hello", labels=TaintLabel.TOOL_OUTPUT)
        td2 = td.with_additional_label(TaintLabel.WEB_CONTENT)
        assert TaintLabel.TOOL_OUTPUT in td2.labels
        assert TaintLabel.WEB_CONTENT in td2.labels
        # Original unchanged
        assert TaintLabel.WEB_CONTENT not in td.labels

    def test_data_id_is_generated(self):
        td1 = TaintedData(value="a")
        td2 = TaintedData(value="b")
        assert td1.data_id != td2.data_id


class TestTaintTracker:
    def test_create_trusted(self):
        tracker = TaintTracker()
        td = tracker.create_trusted("user command")
        assert td.is_trusted
        assert tracker.lookup(td.data_id) is td

    def test_create_tainted(self):
        tracker = TaintTracker()
        td = tracker.create_tainted(
            "tool output", TaintLabel.TOOL_OUTPUT, description="api result"
        )
        assert td.is_tainted
        assert tracker.is_tainted(td.data_id)

    def test_create_tainted_rejects_trusted_labels(self):
        tracker = TaintTracker()
        with pytest.raises(ValueError):
            tracker.create_tainted("x", TaintLabel.NONE)
        with pytest.raises(ValueError):
            tracker.create_tainted("x", TaintLabel.USER_INPUT)

    def test_propagate_combines_labels(self):
        tracker = TaintTracker()
        a = tracker.create_trusted("user part")
        b = tracker.create_tainted("web part", TaintLabel.WEB_CONTENT)
        combined = tracker.propagate(a, b, result_value="merged")
        assert combined.is_tainted
        assert TaintLabel.USER_INPUT in combined.labels
        assert TaintLabel.WEB_CONTENT in combined.labels

    def test_unknown_id_is_tainted_by_default(self):
        tracker = TaintTracker()
        assert tracker.is_tainted("nonexistent")

    def test_get_all_tainted_and_trusted(self):
        tracker = TaintTracker()
        tracker.create_trusted("a")
        tracker.create_tainted("b", TaintLabel.FILE_CONTENT)
        tracker.create_trusted("c")
        assert len(tracker.get_all_trusted()) == 2
        assert len(tracker.get_all_tainted()) == 1

    def test_clear(self):
        tracker = TaintTracker()
        tracker.create_trusted("a")
        tracker.clear()
        assert tracker.get_all_trusted() == []
