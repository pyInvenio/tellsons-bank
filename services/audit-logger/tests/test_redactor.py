from __future__ import annotations

from audit_logger.redactor import Redactor


class TestRedactSSN:
    def test_single_ssn_is_redacted(self) -> None:
        r = Redactor()
        assert r.redact("ssn is 000-00-0000") == "ssn is ***-**-****"

    def test_multiple_ssns_are_redacted(self) -> None:
        r = Redactor()
        msg = "ssn1=123-45-0000 ssn2=987-65-0000"
        assert r.redact(msg) == "ssn1=***-**-**** ssn2=***-**-****"

    def test_ssn_at_start_of_string(self) -> None:
        r = Redactor()
        assert r.redact("000-00-0000 is the ssn") == "***-**-**** is the ssn"

    def test_ssn_at_end_of_string(self) -> None:
        r = Redactor()
        assert r.redact("ssn is 000-00-0000") == "ssn is ***-**-****"

    def test_ssn_alone(self) -> None:
        r = Redactor()
        assert r.redact("000-00-0000") == "***-**-****"


class TestRedactSSNNearMisses:
    def test_too_few_digits_first_group(self) -> None:
        r = Redactor()
        assert r.redact("00-00-0000") == "00-00-0000"

    def test_too_many_digits_first_group(self) -> None:
        r = Redactor()
        assert r.redact("0000-00-0000") == "0000-00-0000"

    def test_too_few_digits_last_group(self) -> None:
        r = Redactor()
        assert r.redact("000-00-000") == "000-00-000"

    def test_no_dashes(self) -> None:
        r = Redactor()
        assert r.redact("000000000") == "000000000"

    def test_ssn_with_letters(self) -> None:
        r = Redactor()
        assert r.redact("00a-00-0000") == "00a-00-0000"


class TestRedactAccountID:
    def test_single_account_id(self) -> None:
        r = Redactor()
        assert r.redact("account acct_test_source") == "account acct_***"

    def test_multiple_account_ids(self) -> None:
        r = Redactor()
        msg = "from acct_test_source to acct_test_dest"
        assert r.redact(msg) == "from acct_*** to acct_***"

    def test_account_id_with_punctuation(self) -> None:
        r = Redactor()
        assert r.redact("(acct_test_source)") == "(acct_***)"

    def test_account_id_at_line_boundary(self) -> None:
        r = Redactor()
        assert r.redact("acct_test_source") == "acct_***"

    def test_demo_account_id(self) -> None:
        r = Redactor()
        assert r.redact("acct_demo_001234") == "acct_***"


class TestRedactAccountIDNearMisses:
    def test_acct_prefix_too_short_suffix(self) -> None:
        r = Redactor()
        assert r.redact("acct_ab") == "acct_ab"

    def test_no_underscore_after_acct(self) -> None:
        r = Redactor()
        assert r.redact("accttest_source") == "accttest_source"

    def test_acct_exactly_six_chars_matches(self) -> None:
        r = Redactor()
        assert r.redact("acct_abcdef") == "acct_***"


class TestRedactCombined:
    def test_ssn_and_account_in_same_message(self) -> None:
        r = Redactor()
        msg = "cust 000-00-0000 accessed acct_test_source"
        result = r.redact(msg)
        assert "000-00-0000" not in result
        assert "acct_test_source" not in result
        assert "***-**-****" in result
        assert "acct_***" in result

    def test_empty_string(self) -> None:
        r = Redactor()
        assert r.redact("") == ""

    def test_no_pii_unchanged(self) -> None:
        r = Redactor()
        msg = "system healthcheck passed for cust_test_001"
        assert r.redact(msg) == msg

    def test_synthetic_customers_ssn(
        self, synthetic_customers: list[dict[str, str]]
    ) -> None:
        r = Redactor()
        for customer in synthetic_customers:
            ssn = customer["ssn"]
            result = r.redact(f"lookup {ssn}")
            assert ssn not in result

    def test_synthetic_accounts_redacted(
        self, synthetic_accounts: list[dict[str, str]]
    ) -> None:
        r = Redactor()
        for account in synthetic_accounts:
            acct_id = account["accountId"]
            result = r.redact(f"transfer from {acct_id}")
            assert acct_id not in result
