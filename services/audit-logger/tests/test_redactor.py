from __future__ import annotations

import pytest

from audit_logger.redactor import Redactor


@pytest.fixture()
def redactor() -> Redactor:
    return Redactor()


class TestRedactorSSN:
    def test_single_ssn_redacted(self, redactor: Redactor) -> None:
        assert redactor.redact("SSN is 000-00-0000") == "SSN is ***-**-****"

    def test_multiple_ssns_redacted(self, redactor: Redactor) -> None:
        msg = "primary 000-00-0000 secondary 111-22-3333"
        result = redactor.redact(msg)
        assert result == "primary ***-**-**** secondary ***-**-****"

    def test_ssn_at_start_of_line(self, redactor: Redactor) -> None:
        assert redactor.redact("000-00-0000 is the SSN") == "***-**-**** is the SSN"

    def test_ssn_at_end_of_line(self, redactor: Redactor) -> None:
        assert redactor.redact("SSN: 000-00-0000") == "SSN: ***-**-****"

    def test_near_miss_too_few_digits(self, redactor: Redactor) -> None:
        assert redactor.redact("00-00-0000 partial") == "00-00-0000 partial"

    def test_near_miss_no_dashes(self, redactor: Redactor) -> None:
        assert redactor.redact("000000000 no dashes") == "000000000 no dashes"

    def test_near_miss_extra_digits(self, redactor: Redactor) -> None:
        assert redactor.redact("0000-00-0000 extra") == "0000-00-0000 extra"


class TestRedactorAccount:
    def test_account_id_redacted(self, redactor: Redactor) -> None:
        assert redactor.redact("account acct_test_source_01") == "account acct_***"

    def test_account_id_with_punctuation(self, redactor: Redactor) -> None:
        assert redactor.redact("(acct_test_source)") == "(acct_***)"

    def test_account_id_at_word_boundary(self, redactor: Redactor) -> None:
        assert redactor.redact("from acct_demo_001 to acct_demo_002") == "from acct_*** to acct_***"

    def test_short_account_id_not_redacted(self, redactor: Redactor) -> None:
        assert redactor.redact("acct_ab not long enough") == "acct_ab not long enough"

    def test_account_id_exactly_six_chars_redacted(self, redactor: Redactor) -> None:
        assert redactor.redact("acct_abcdef match") == "acct_*** match"


class TestRedactorCombined:
    def test_ssn_and_account_both_redacted(self, redactor: Redactor) -> None:
        msg = "cust 000-00-0000 acct acct_test_source"
        result = redactor.redact(msg)
        assert result == "cust ***-**-**** acct acct_***"

    def test_empty_string_unchanged(self, redactor: Redactor) -> None:
        assert redactor.redact("") == ""

    def test_no_pii_unchanged(self, redactor: Redactor) -> None:
        msg = "cust_test_001 logged in from 203.0.113.10"
        assert redactor.redact(msg) == msg
