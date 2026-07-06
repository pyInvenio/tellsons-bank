"""Compliance tests for DisputeWorkflow – audit path.

Covers: invalid case IDs, missing transaction IDs, open-case status,
approve/deny resolution paths, audit reason preservation, and
timestamp determinism (via injected clock).
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from dispute_resolution.workflow import DisputeCase, DisputeWorkflow

from .fixtures import (
    EMPTY_TXN_ID,
    FIXED_TIMESTAMP,
    FIXED_TIMESTAMP_ALT,
    INVALID_CASE_IDS,
    VALID_CASE_ID,
    VALID_CASE_ID_ALT,
    VALID_REASON,
    VALID_REASON_ALT,
    VALID_TXN_ID,
    VALID_TXN_ID_ALT,
)


# ---------------------------------------------------------------------------
# open_case – invalid case IDs
# ---------------------------------------------------------------------------

class TestOpenCaseInvalidCaseId:
    """Cases whose case_id does not start with 'case_test_' must be rejected."""

    @pytest.mark.parametrize("bad_id", INVALID_CASE_IDS)
    def test_rejects_non_synthetic_case_id(self, workflow: DisputeWorkflow, bad_id: str) -> None:
        with pytest.raises(ValueError, match="synthetic case id required"):
            workflow.open_case(bad_id, VALID_TXN_ID, VALID_REASON)


# ---------------------------------------------------------------------------
# open_case – missing transaction ID
# ---------------------------------------------------------------------------

class TestOpenCaseMissingTransactionId:
    """A blank transaction_id must raise."""

    def test_rejects_empty_transaction_id(self, workflow: DisputeWorkflow) -> None:
        with pytest.raises(ValueError, match="transaction id required"):
            workflow.open_case(VALID_CASE_ID, EMPTY_TXN_ID, VALID_REASON)


# ---------------------------------------------------------------------------
# open_case – happy path / OPEN status
# ---------------------------------------------------------------------------

class TestOpenCaseHappyPath:
    """A valid open_case call returns a DisputeCase with status OPEN."""

    def test_returns_dispute_case(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert isinstance(case, DisputeCase)

    def test_status_is_open(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.status == "OPEN"

    def test_preserves_case_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.case_id == VALID_CASE_ID

    def test_preserves_transaction_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.transaction_id == VALID_TXN_ID

    def test_preserves_audit_reason(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.audit_reason == VALID_REASON

    def test_updated_at_is_utc(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.updated_at.tzinfo == timezone.utc


# ---------------------------------------------------------------------------
# open_case – audit reason preservation for various inputs
# ---------------------------------------------------------------------------

class TestAuditReasonPreservation:
    """audit_reason must pass through unchanged for any string value."""

    def test_empty_reason_preserved(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, "")
        assert case.audit_reason == ""

    def test_long_reason_preserved(self, workflow: DisputeWorkflow) -> None:
        long_reason = "x" * 2000
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, long_reason)
        assert case.audit_reason == long_reason

    def test_unicode_reason_preserved(self, workflow: DisputeWorkflow) -> None:
        reason = "disputante: cust_demo_001 \u2013 charge r\u00e9clam\u00e9e"
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, reason)
        assert case.audit_reason == reason

    def test_alternate_reason_preserved(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON_ALT)
        assert case.audit_reason == VALID_REASON_ALT


# ---------------------------------------------------------------------------
# resolve – approve path (CUSTOMER_CREDITED)
# ---------------------------------------------------------------------------

class TestResolveApproved:
    """Approved resolution yields CUSTOMER_CREDITED status."""

    def test_approved_status(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert resolved.status == "CUSTOMER_CREDITED"

    def test_approved_preserves_case_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert resolved.case_id == VALID_CASE_ID

    def test_approved_preserves_transaction_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert resolved.transaction_id == VALID_TXN_ID

    def test_approved_preserves_audit_reason(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert resolved.audit_reason == VALID_REASON


# ---------------------------------------------------------------------------
# resolve – deny path (DENIED)
# ---------------------------------------------------------------------------

class TestResolveDenied:
    """Denied resolution yields DENIED status."""

    def test_denied_status(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=False)
        assert resolved.status == "DENIED"

    def test_denied_preserves_case_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=False)
        assert resolved.case_id == VALID_CASE_ID

    def test_denied_preserves_transaction_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=False)
        assert resolved.transaction_id == VALID_TXN_ID

    def test_denied_preserves_audit_reason(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=False)
        assert resolved.audit_reason == VALID_REASON


# ---------------------------------------------------------------------------
# resolve – output is a new immutable DisputeCase
# ---------------------------------------------------------------------------

class TestResolveImmutability:
    """resolve() returns a new DisputeCase; original is unchanged (frozen dataclass)."""

    def test_original_unchanged(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert case.status == "OPEN"
        assert resolved.status == "CUSTOMER_CREDITED"

    def test_resolved_is_different_object(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert case is not resolved


# ---------------------------------------------------------------------------
# Timestamp determinism via injected clock
# ---------------------------------------------------------------------------

class TestTimestampDeterminism:
    """Verify timestamps are deterministic when datetime.now is mocked."""

    def test_open_case_uses_fixed_clock(self, workflow: DisputeWorkflow, frozen_clock) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        assert case.updated_at == FIXED_TIMESTAMP

    def test_resolve_uses_fixed_clock(self, workflow: DisputeWorkflow, frozen_clock) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        resolved = workflow.resolve(case, approved=True)
        assert resolved.updated_at == FIXED_TIMESTAMP

    def test_clock_advances_between_steps(self, workflow: DisputeWorkflow) -> None:
        with patch("dispute_resolution.workflow.datetime") as mock_dt:
            mock_dt.now.return_value = FIXED_TIMESTAMP
            case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
            assert case.updated_at == FIXED_TIMESTAMP

            mock_dt.now.return_value = FIXED_TIMESTAMP_ALT
            resolved = workflow.resolve(case, approved=False)
            assert resolved.updated_at == FIXED_TIMESTAMP_ALT
            assert resolved.updated_at > case.updated_at


# ---------------------------------------------------------------------------
# Multiple cases – independent workflows
# ---------------------------------------------------------------------------

class TestMultipleCases:
    """Separate cases don't interfere with each other."""

    def test_two_independent_cases(self, workflow: DisputeWorkflow) -> None:
        case_a = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        case_b = workflow.open_case(VALID_CASE_ID_ALT, VALID_TXN_ID_ALT, VALID_REASON_ALT)
        assert case_a.case_id != case_b.case_id
        assert case_a.transaction_id != case_b.transaction_id

    def test_resolve_one_leaves_other_open(self, workflow: DisputeWorkflow) -> None:
        case_a = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        case_b = workflow.open_case(VALID_CASE_ID_ALT, VALID_TXN_ID_ALT, VALID_REASON_ALT)
        resolved_a = workflow.resolve(case_a, approved=True)
        assert resolved_a.status == "CUSTOMER_CREDITED"
        assert case_b.status == "OPEN"


# ---------------------------------------------------------------------------
# DisputeCase dataclass – frozen enforcement
# ---------------------------------------------------------------------------

class TestDisputeCaseFrozen:
    """DisputeCase is a frozen dataclass; mutation must raise."""

    def test_cannot_mutate_status(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        with pytest.raises(AttributeError):
            case.status = "DENIED"  # type: ignore[misc]

    def test_cannot_mutate_case_id(self, workflow: DisputeWorkflow) -> None:
        case = workflow.open_case(VALID_CASE_ID, VALID_TXN_ID, VALID_REASON)
        with pytest.raises(AttributeError):
            case.case_id = "case_test_hack"  # type: ignore[misc]
