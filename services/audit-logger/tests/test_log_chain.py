from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from audit_logger.log_chain import AuditRecord, LogChain


class TestLogChainAppend:
    def test_first_record_links_to_genesis(self) -> None:
        chain = LogChain()
        record = chain.append("login failed for cust_test_001")
        assert record.sequence == 1
        assert record.previous_hash == "GENESIS"

    def test_second_record_links_to_first_hash(self) -> None:
        chain = LogChain()
        first = chain.append("login failed for cust_test_001")
        second = chain.append("transfer denied for acct_test_source")
        assert second.sequence == 2
        assert second.previous_hash == first.hash

    def test_hash_is_deterministic_for_same_inputs(self) -> None:
        fixed_ts = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
        with patch("audit_logger.log_chain.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_ts
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            chain1 = LogChain()
            r1 = chain1.append("transfer denied for acct_test_source")
            chain2 = LogChain()
            r2 = chain2.append("transfer denied for acct_test_source")
        assert r1.hash == r2.hash

    def test_append_uses_utc_timestamp(self) -> None:
        chain = LogChain()
        record = chain.append("login failed for cust_test_001")
        assert record.occurred_at.tzinfo == timezone.utc

    def test_append_preserves_message(self) -> None:
        chain = LogChain()
        msg = "transfer denied for acct_test_source"
        record = chain.append(msg)
        assert record.message == msg

    def test_empty_message(self) -> None:
        chain = LogChain()
        record = chain.append("")
        assert record.sequence == 1
        assert record.message == ""
        assert record.hash

    def test_unicode_message(self) -> None:
        chain = LogChain()
        record = chain.append("withdrawal for cust_test_002 \u00e9\u00e0\u00fc\u00f1")
        assert record.message == "withdrawal for cust_test_002 \u00e9\u00e0\u00fc\u00f1"
        assert record.hash

    def test_long_chain_sequence_numbers(self) -> None:
        chain = LogChain()
        records = [chain.append(f"event {i} for cust_test_001") for i in range(10)]
        for i, record in enumerate(records, start=1):
            assert record.sequence == i

    def test_chain_linkage_across_many_records(self) -> None:
        chain = LogChain()
        prev_hash = "GENESIS"
        for i in range(5):
            record = chain.append(f"event {i} for acct_test_source")
            assert record.previous_hash == prev_hash
            prev_hash = record.hash


class TestLogChainVerify:
    def test_empty_chain_verifies(self) -> None:
        chain = LogChain()
        assert chain.verify() is True

    def test_single_record_chain_verifies(self) -> None:
        chain = LogChain()
        chain.append("login failed for cust_test_001")
        assert chain.verify() is True

    def test_multi_record_chain_verifies(self) -> None:
        chain = LogChain()
        chain.append("login failed for cust_test_001")
        chain.append("transfer denied for acct_test_source")
        chain.append("account locked for cust_test_002")
        assert chain.verify() is True

    def test_sequence_gap_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        bad_records = [
            AuditRecord(
                sequence=1,
                previous_hash="GENESIS",
                message="login failed for cust_test_001",
                occurred_at=ts,
                hash=chain._hash(1, "GENESIS", "login failed for cust_test_001", ts.isoformat()),
            ),
            AuditRecord(
                sequence=3,
                previous_hash="some_hash",
                message="skipped seq 2",
                occurred_at=ts,
                hash="irrelevant",
            ),
        ]
        assert chain.verify(bad_records) is False

    def test_wrong_previous_hash_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        first_hash = chain._hash(1, "GENESIS", "login failed for cust_test_001", ts.isoformat())
        bad_records = [
            AuditRecord(
                sequence=1,
                previous_hash="GENESIS",
                message="login failed for cust_test_001",
                occurred_at=ts,
                hash=first_hash,
            ),
            AuditRecord(
                sequence=2,
                previous_hash="WRONG_HASH",
                message="transfer denied for acct_test_source",
                occurred_at=ts,
                hash=chain._hash(2, "WRONG_HASH", "transfer denied for acct_test_source", ts.isoformat()),
            ),
        ]
        assert chain.verify(bad_records) is False

    def test_tampered_message_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        original_hash = chain._hash(1, "GENESIS", "login failed for cust_test_001", ts.isoformat())
        tampered = [
            AuditRecord(
                sequence=1,
                previous_hash="GENESIS",
                message="login SUCCEEDED for cust_test_001",
                occurred_at=ts,
                hash=original_hash,
            ),
        ]
        assert chain.verify(tampered) is False

    def test_tampered_timestamp_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        original_hash = chain._hash(1, "GENESIS", "login failed for cust_test_001", ts.isoformat())
        tampered_ts = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
        tampered = [
            AuditRecord(
                sequence=1,
                previous_hash="GENESIS",
                message="login failed for cust_test_001",
                occurred_at=tampered_ts,
                hash=original_hash,
            ),
        ]
        assert chain.verify(tampered) is False

    def test_tampered_hash_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        tampered = [
            AuditRecord(
                sequence=1,
                previous_hash="GENESIS",
                message="login failed for cust_test_001",
                occurred_at=ts,
                hash="0000000000000000000000000000000000000000000000000000000000000000",
            ),
        ]
        assert chain.verify(tampered) is False

    def test_verify_with_explicit_valid_list(self) -> None:
        chain = LogChain()
        chain.append("login failed for cust_test_001")
        chain.append("transfer denied for acct_test_source")
        valid_list = list(chain._records)
        new_chain = LogChain()
        assert new_chain.verify(valid_list) is True

    def test_verify_external_list_does_not_mutate_internal(self) -> None:
        chain = LogChain()
        chain.append("login failed for cust_test_001")
        external: list[AuditRecord] = []
        chain.verify(external)
        assert len(chain._records) == 1

    def test_verify_none_uses_internal_records(self) -> None:
        chain = LogChain()
        chain.append("login failed for cust_test_001")
        assert chain.verify(None) is True

    def test_single_record_wrong_sequence_fails(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        bad = [
            AuditRecord(
                sequence=5,
                previous_hash="GENESIS",
                message="login failed for cust_test_001",
                occurred_at=ts,
                hash=chain._hash(5, "GENESIS", "login failed for cust_test_001", ts.isoformat()),
            ),
        ]
        assert chain.verify(bad) is False


class TestLogChainHash:
    def test_hash_is_sha256_hex(self) -> None:
        h = LogChain._hash(1, "GENESIS", "test", "2025-01-01T00:00:00+00:00")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_sequences_produce_different_hashes(self) -> None:
        ts = "2025-01-01T00:00:00+00:00"
        h1 = LogChain._hash(1, "GENESIS", "msg", ts)
        h2 = LogChain._hash(2, "GENESIS", "msg", ts)
        assert h1 != h2

    def test_different_messages_produce_different_hashes(self) -> None:
        ts = "2025-01-01T00:00:00+00:00"
        h1 = LogChain._hash(1, "GENESIS", "msg_a", ts)
        h2 = LogChain._hash(1, "GENESIS", "msg_b", ts)
        assert h1 != h2

    def test_different_timestamps_produce_different_hashes(self) -> None:
        h1 = LogChain._hash(1, "GENESIS", "msg", "2025-01-01T00:00:00+00:00")
        h2 = LogChain._hash(1, "GENESIS", "msg", "2025-06-01T00:00:00+00:00")
        assert h1 != h2


class TestLogChainWithFixtures:
    def test_append_synthetic_audit_lines(
        self, synthetic_audit_lines: list[dict[str, str]]
    ) -> None:
        chain = LogChain()
        for line in synthetic_audit_lines:
            record = chain.append(line["message"])
            assert record.hash
        assert chain.verify() is True
