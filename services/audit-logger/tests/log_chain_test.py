from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

from audit_logger.log_chain import AuditRecord, LogChain


def _valid_chain() -> tuple[LogChain, list[AuditRecord]]:
    chain = LogChain()
    first = chain.append("login succeeded for cust_test_001")
    second = chain.append("transfer queued for acct_test_0001")
    return chain, [first, second]


def test_first_record_links_to_genesis(frozen_clock):
    chain = LogChain()
    record = chain.append("login succeeded for cust_test_001")

    assert record.sequence == 1
    assert record.previous_hash == "GENESIS"
    assert record.hash != "GENESIS"


def test_subsequent_record_links_to_previous_hash(frozen_clock):
    chain, records = _valid_chain()

    assert records[1].sequence == 2
    assert records[1].previous_hash == records[0].hash
    assert chain.verify() is True


def test_empty_chain_verifies_true():
    assert LogChain().verify() is True


def test_verify_uses_internal_records_when_none_passed(frozen_clock):
    chain, _ = _valid_chain()

    assert chain.verify(None) is True
    assert chain.verify() is True


def test_verify_accepts_external_record_list_without_mutation(frozen_clock):
    chain, records = _valid_chain()
    internal_before = list(chain._records)

    external = list(records)
    assert chain.verify(external) is True
    assert chain._records == internal_before


def test_sequence_gap_fails_verification(frozen_clock):
    chain, records = _valid_chain()
    tampered = dataclasses.replace(records[1], sequence=99)

    assert chain.verify([records[0], tampered]) is False


def test_broken_previous_hash_link_fails_verification(frozen_clock):
    chain, records = _valid_chain()
    tampered = dataclasses.replace(records[1], previous_hash="GENESIS")

    assert chain.verify([records[0], tampered]) is False


def test_tampered_message_fails_verification(frozen_clock):
    chain, records = _valid_chain()
    tampered = dataclasses.replace(records[0], message="transfer approved")

    assert chain.verify([tampered, records[1]]) is False


def test_tampered_timestamp_fails_verification(frozen_clock):
    chain, records = _valid_chain()
    shifted = records[0].occurred_at.replace(year=2030)
    tampered = dataclasses.replace(records[0], occurred_at=shifted)

    assert chain.verify([tampered, records[1]]) is False


def test_tampered_stored_hash_fails_verification(frozen_clock):
    chain, records = _valid_chain()
    tampered = dataclasses.replace(records[0], hash="deadbeef")

    assert chain.verify([tampered, records[1]]) is False


def test_fixed_clock_produces_deterministic_hash():
    instant = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected = LogChain._hash(1, "GENESIS", "audit event", instant.isoformat())

    record = AuditRecord(1, "GENESIS", "audit event", instant, expected)
    assert LogChain().verify([record]) is True
