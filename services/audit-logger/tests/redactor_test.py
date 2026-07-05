"""Branch coverage for Redactor PII suppression and redaction boundaries.

All SSN-like values use the reserved ``000-00-0000`` documentation pattern and
account IDs use synthetic ``acct_test_*`` / ``acct_demo_*`` identifiers.
"""
from __future__ import annotations

import pytest

from audit_logger.redactor import Redactor


@pytest.fixture
def redactor() -> Redactor:
    return Redactor()


def test_redacts_single_ssn(redactor):
    assert redactor.redact("ssn 000-00-0000 on file") == "ssn ***-**-**** on file"


def test_redacts_multiple_ssns_in_one_line(redactor):
    result = redactor.redact("primary 000-00-0000 secondary 111-22-3333")

    assert result == "primary ***-**-**** secondary ***-**-****"


def test_redacts_account_id(redactor):
    assert redactor.redact("charge acct_test_0001 now") == "charge acct_*** now"


def test_redacts_account_id_surrounded_by_punctuation(redactor):
    assert redactor.redact("(acct_demo_999).") == "(acct_***)."


def test_redacts_both_ssn_and_account(redactor):
    result = redactor.redact("cust 000-00-0000 owns acct_test_source")

    assert result == "cust ***-**-**** owns acct_***"


@pytest.mark.parametrize(
    "message",
    [
        "audit trail intact",
        "",
        "cust_test_001 logged in",
        "amount 4111",
    ],
)
def test_leaves_messages_without_pii_unchanged(redactor, message):
    assert redactor.redact(message) == message


@pytest.mark.parametrize(
    "near_miss",
    [
        "0000-00-0000",       # too many leading digits, no word boundary match
        "00-00-0000",         # too few leading digits
        "000-0-0000",         # too few middle digits
        "acct_short",         # fewer than 6 trailing chars
        "acctx_test_000001",  # missing required underscore after acct
    ],
)
def test_near_misses_are_not_redacted(redactor, near_miss):
    assert redactor.redact(near_miss) == near_miss
