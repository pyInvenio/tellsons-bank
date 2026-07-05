from __future__ import annotations

import pytest

from audit_logger.redactor import Redactor


@pytest.fixture
def redactor() -> Redactor:
    return Redactor()


def _all_cases(fixtures: dict) -> list[dict]:
    return (
        fixtures["ssn_cases"]
        + fixtures["account_cases"]
        + fixtures["combined_cases"]
        + fixtures["near_miss_cases"]
    )


def test_fixture_driven_redaction(redactor, redaction_fixtures):
    for case in _all_cases(redaction_fixtures):
        assert redactor.redact(case["input"]) == case["expected"], case["name"]


def test_single_ssn_is_masked(redactor):
    assert redactor.redact("ssn 000-00-0000 seen") == "ssn ***-**-**** seen"


def test_multiple_ssns_are_all_masked(redactor):
    assert redactor.redact("000-00-0000 000-00-0000") == "***-**-**** ***-**-****"


def test_account_id_is_masked(redactor):
    assert redactor.redact("acct_test_0001 closed") == "acct_*** closed"


def test_ssn_and_account_masked_together(redactor):
    result = redactor.redact("000-00-0000 owns acct_test_777001")
    assert result == "***-**-**** owns acct_***"


def test_short_account_suffix_is_not_masked(redactor):
    assert redactor.redact("acct_12 short") == "acct_12 short"


def test_partial_ssn_is_not_masked(redactor):
    assert redactor.redact("00-00-0000 not ssn") == "00-00-0000 not ssn"


def test_message_without_pii_is_unchanged(redactor):
    assert redactor.redact("login for cust_test_001") == "login for cust_test_001"


def test_empty_message_is_unchanged(redactor):
    assert redactor.redact("") == ""
