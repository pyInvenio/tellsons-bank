from __future__ import annotations

from datetime import datetime, timezone

from audit_logger.log_chain import AuditRecord, LogChain


class TestLogChainAppend:
    def test_first_record_links_to_genesis(self) -> None:
        chain = LogChain()
        record = chain.append("cust_test_001 logged in")
        assert record.sequence == 1
        assert record.previous_hash == "GENESIS"
        assert isinstance(record.hash, str) and len(record.hash) == 64

    def test_second_record_links_to_first(self) -> None:
        chain = LogChain()
        first = chain.append("cust_test_001 logged in")
        second = chain.append("cust_test_002 transfer initiated")
        assert second.sequence == 2
        assert second.previous_hash == first.hash

    def test_append_records_utc_timestamp(self) -> None:
        chain = LogChain()
        record = chain.append("acct_test_source deposit")
        assert record.occurred_at.tzinfo == timezone.utc

    def test_hash_is_deterministic_for_same_inputs(self) -> None:
        h1 = LogChain._hash(1, "GENESIS", "msg", "2025-01-01T00:00:00+00:00")
        h2 = LogChain._hash(1, "GENESIS", "msg", "2025-01-01T00:00:00+00:00")
        assert h1 == h2

    def test_hash_changes_with_different_message(self) -> None:
        h1 = LogChain._hash(1, "GENESIS", "msg_a", "2025-01-01T00:00:00+00:00")
        h2 = LogChain._hash(1, "GENESIS", "msg_b", "2025-01-01T00:00:00+00:00")
        assert h1 != h2


class TestLogChainVerify:
    def test_empty_chain_verifies(self) -> None:
        chain = LogChain()
        assert chain.verify() is True

    def test_valid_single_record_verifies(self) -> None:
        chain = LogChain()
        chain.append("cust_test_001 logged in")
        assert chain.verify() is True

    def test_valid_multi_record_chain_verifies(self) -> None:
        chain = LogChain()
        chain.append("cust_test_001 logged in")
        chain.append("txn_test_001 transfer")
        chain.append("cust_test_002 logged out")
        assert chain.verify() is True

    def test_sequence_gap_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        h = LogChain._hash(1, "GENESIS", "m", ts.isoformat())
        bad_records = [
            AuditRecord(sequence=2, previous_hash="GENESIS", message="m", occurred_at=ts, hash=h),
        ]
        assert chain.verify(bad_records) is False

    def test_wrong_previous_hash_fails_verification(self) -> None:
        chain = LogChain()
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        h = LogChain._hash(1, "WRONG", "m", ts.isoformat())
        bad_records = [
            AuditRecord(sequence=1, previous_hash="WRONG", message="m", occurred_at=ts, hash=h),
        ]
        assert chain.verify(bad_records) is False

    def test_tampered_message_fails_verification(self) -> None:
        chain = LogChain()
        record = chain.append("original message")
        tampered = AuditRecord(
            sequence=record.sequence,
            previous_hash=record.previous_hash,
            message="tampered message",
            occurred_at=record.occurred_at,
            hash=record.hash,
        )
        assert chain.verify([tampered]) is False

    def test_tampered_timestamp_fails_verification(self) -> None:
        chain = LogChain()
        record = chain.append("cust_test_001 event")
        fake_ts = datetime(1999, 1, 1, tzinfo=timezone.utc)
        tampered = AuditRecord(
            sequence=record.sequence,
            previous_hash=record.previous_hash,
            message=record.message,
            occurred_at=fake_ts,
            hash=record.hash,
        )
        assert chain.verify([tampered]) is False

    def test_tampered_hash_fails_verification(self) -> None:
        chain = LogChain()
        record = chain.append("cust_test_001 event")
        tampered = AuditRecord(
            sequence=record.sequence,
            previous_hash=record.previous_hash,
            message=record.message,
            occurred_at=record.occurred_at,
            hash="0" * 64,
        )
        assert chain.verify([tampered]) is False

    def test_external_list_does_not_mutate_internal_state(self) -> None:
        chain = LogChain()
        chain.append("cust_test_001 internal event")
        ts = datetime(2025, 6, 1, tzinfo=timezone.utc)
        h = LogChain._hash(1, "GENESIS", "external", ts.isoformat())
        external = [
            AuditRecord(sequence=1, previous_hash="GENESIS", message="external", occurred_at=ts, hash=h),
        ]
        assert chain.verify(external) is True
        assert chain.verify() is True
        assert chain._records[0].message == "cust_test_001 internal event"

    def test_broken_link_mid_chain_fails(self) -> None:
        chain = LogChain()
        r1 = chain.append("cust_test_001 event1")
        r2 = chain.append("cust_test_002 event2")
        broken_r2 = AuditRecord(
            sequence=r2.sequence,
            previous_hash="GENESIS",
            message=r2.message,
            occurred_at=r2.occurred_at,
            hash=r2.hash,
        )
        assert chain.verify([r1, broken_r2]) is False
