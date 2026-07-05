from __future__ import annotations

import pytest


def test_redacts_single_ssn(redactor):
    assert redactor.redact("ssn 000-00-0000 recorded") == "ssn ***-**-**** recorded"


def test_redacts_multiple_ssns_in_one_line(redactor):
    message = "primary 000-00-0000 and secondary 123-45-6789"
    assert redactor.redact(message) == "primary ***-**-**** and secondary ***-**-****"


def test_redacts_account_id(redactor):
    assert redactor.redact("debit acct_test_0001 today") == "debit acct_*** today"


def test_redacts_account_id_surrounded_by_punctuation(redactor):
    assert redactor.redact("(acct_test_0001).") == "(acct_***)."


def test_redacts_both_ssn_and_account(redactor):
    message = "cust 000-00-0000 owns acct_test_0002"
    assert redactor.redact(message) == "cust ***-**-**** owns acct_***"


@pytest.mark.parametrize(
    "message",
    [
        "acct_short",            # fewer than 6 trailing chars -> not matched
        "0000-00-0000",          # malformed SSN grouping
        "00-00-0000",            # wrong leading group length
        "plain audit event",     # no PII at all
    ],
)
def test_leaves_near_misses_and_clean_text_unchanged(redactor, message):
    assert redactor.redact(message) == message


def test_empty_string_is_unchanged(redactor):
    assert redactor.redact("") == ""
