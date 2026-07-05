from __future__ import annotations

import dataclasses

from audit_logger.log_chain import AuditRecord, LogChain

from conftest import BASE_TIME, make_record


def test_append_first_record_links_to_genesis(chain):
    record = chain.append("boot cust_test_001")

    assert record.sequence == 1
    assert record.previous_hash == "GENESIS"
    assert record.occurred_at == BASE_TIME
    assert record.hash == LogChain._hash(
        1, "GENESIS", "boot cust_test_001", BASE_TIME.isoformat()
    )


def test_append_chains_sequence_and_previous_hash(chain):
    first = chain.append("event one for acct_test_0001")
    second = chain.append("event two for acct_test_0002")

    assert second.sequence == 2
    assert second.previous_hash == first.hash
    assert chain.verify() is True


def test_verify_empty_chain_is_true():
    assert LogChain().verify() is True


def test_verify_valid_multi_record_chain(chain):
    for message in ("a", "b", "c"):
        chain.append(message)

    assert chain.verify() is True


def test_verify_detects_sequence_gap():
    record_one = make_record(1, "GENESIS", "first")
    # Sequence jumps to 3, so continuity check must fail.
    record_three = make_record(3, record_one.hash, "third")

    assert LogChain().verify([record_one, record_three]) is False


def test_verify_detects_broken_previous_hash_link():
    record_one = make_record(1, "GENESIS", "first")
    record_two = make_record(2, "not-the-previous-hash", "second")

    assert LogChain().verify([record_one, record_two]) is False


def test_verify_detects_tampered_message():
    record = make_record(1, "GENESIS", "original")
    tampered = dataclasses.replace(record, message="rewritten")

    assert LogChain().verify([tampered]) is False


def test_verify_detects_tampered_timestamp():
    record = make_record(1, "GENESIS", "original")
    shifted = dataclasses.replace(
        record, occurred_at=BASE_TIME.replace(year=2030)
    )

    assert LogChain().verify([shifted]) is False


def test_verify_detects_tampered_hash():
    record = make_record(1, "GENESIS", "original")
    forged = dataclasses.replace(record, hash="deadbeef")

    assert LogChain().verify([forged]) is False


def test_verify_external_list_does_not_mutate_internal_state(chain):
    chain.append("internal only")
    external = [make_record(1, "GENESIS", "external record")]

    assert chain.verify(external) is True
    # Internal chain is untouched and still self-consistent.
    assert chain.verify() is True
    assert len(chain._records) == 1
    assert chain._records[0].message == "internal only"


def test_records_are_immutable(chain):
    record = chain.append("frozen")

    with_error = False
    try:
        record.message = "mutated"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        with_error = True

    assert with_error is True
