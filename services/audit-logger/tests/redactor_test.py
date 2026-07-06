from __future__ import annotations

import pytest

from audit_logger.redactor import Redactor


@pytest.fixture
def redactor() -> Redactor:
    return Redactor()


@pytest.fixture(params=[0, 1, 2, 3], ids=lambda index: f"fixture_case_{index}")
def redaction_case(request: pytest.FixtureRequest, redaction_fixtures: list[dict[str, str]]) -> dict[str, str]:
    return redaction_fixtures[request.param]


def test_redactor_replaces_single_ssn(redactor: Redactor) -> None:
    assert redactor.redact("cust_test_0001 used 000-00-0000 for verification") == (
        "cust_test_0001 used ***-**-**** for verification"
    )


def test_redactor_replaces_multiple_ssns(redactor: Redactor) -> None:
    assert redactor.redact("000-00-0000 and 111-22-3333 were both observed") == (
        "***-**-**** and ***-**-**** were both observed"
    )


def test_redactor_replaces_account_surrounded_by_punctuation(redactor: Redactor) -> None:
    assert redactor.redact("alerts:(acct_test_0001),reviewed") == "alerts:(acct_***),reviewed"


def test_redactor_replaces_both_ssn_and_account(redactor: Redactor) -> None:
    assert redactor.redact("acct_test_0001 saw 000-00-0000 in a note") == (
        "acct_*** saw ***-**-**** in a note"
    )


def test_redactor_leaves_near_misses_unchanged(redactor: Redactor) -> None:
    message = "acct_12 and 00-00-0000 remain untouched"

    assert redactor.redact(message) == message


def test_redactor_handles_empty_string(redactor: Redactor) -> None:
    assert redactor.redact("") == ""


def test_redactor_leaves_non_pii_message_unchanged(redactor: Redactor) -> None:
    message = "cust_test_0001 opened a synthetic audit session"

    assert redactor.redact(message) == message


def test_redactor_uses_json_fixture_case(redactor: Redactor, redaction_case: dict[str, str]) -> None:
    assert redactor.redact(redaction_case["message"]) == redaction_case["expected"]
