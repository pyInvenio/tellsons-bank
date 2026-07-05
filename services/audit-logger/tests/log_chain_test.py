"""Branch coverage for LogChain append/verify tamper and gap paths."""
from __future__ import annotations

import dataclasses
from datetime import timedelta

from audit_logger.log_chain import LogChain


def test_append_first_record_links_to_genesis():
    chain = LogChain()

    record = chain.append("login ok for cust_test_001")

    assert record.sequence == 1
    assert record.previous_hash == "GENESIS"
    assert record.hash != "GENESIS"


def test_append_links_each_record_to_previous_hash():
    chain = LogChain()

    first = chain.append("first for cust_test_001")
    second = chain.append("second for cust_test_001")

    assert second.sequence == 2
    assert second.previous_hash == first.hash
    assert chain.verify() is True


def test_empty_chain_verifies_true():
    assert LogChain().verify() is True


def test_verify_valid_external_records(valid_records):
    assert LogChain().verify(valid_records) is True


def test_verify_fails_on_sequence_gap(valid_records):
    # Drop the middle record so sequence continuity breaks (hash-chain gap).
    gapped = [valid_records[0], valid_records[2]]

    assert LogChain().verify(gapped) is False


def test_verify_fails_on_out_of_order_sequence(valid_records):
    tampered = dataclasses.replace(valid_records[0], sequence=5)

    assert LogChain().verify([tampered, *valid_records[1:]]) is False


def test_verify_fails_on_broken_previous_hash_linkage(valid_records):
    tampered = dataclasses.replace(valid_records[1], previous_hash="GENESIS")

    assert LogChain().verify([valid_records[0], tampered, valid_records[2]]) is False


def test_verify_fails_on_tampered_message(valid_records):
    tampered = dataclasses.replace(valid_records[1], message="edited after the fact")

    assert LogChain().verify([valid_records[0], tampered, valid_records[2]]) is False


def test_verify_fails_on_tampered_timestamp(valid_records):
    tampered = dataclasses.replace(
        valid_records[1], occurred_at=valid_records[1].occurred_at + timedelta(hours=1)
    )

    assert LogChain().verify([valid_records[0], tampered, valid_records[2]]) is False


def test_verify_with_external_list_does_not_mutate_internal_state(valid_records):
    chain = LogChain()
    chain.append("internal only for cust_test_001")

    # Verifying a foreign list must not disturb the internal chain.
    assert chain.verify(valid_records) is True
    assert chain.verify() is True
    assert chain.verify([]) is True


def test_single_record_list_with_wrong_genesis_fails(make_records):
    (record,) = make_records(["only for cust_test_001"])
    tampered = dataclasses.replace(record, previous_hash="NOT_GENESIS")

    assert LogChain().verify([tampered]) is False
