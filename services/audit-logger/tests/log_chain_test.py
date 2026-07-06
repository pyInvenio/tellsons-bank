from __future__ import annotations

from dataclasses import replace

from audit_logger.log_chain import LogChain


def test_append_to_empty_chain_uses_genesis_and_sequence_one_and_verifies() -> None:
    chain = LogChain()

    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")

    assert first.sequence == 1
    assert first.previous_hash == "GENESIS"
    assert second.sequence == 2
    assert second.previous_hash == first.hash
    assert chain.verify() is True


def test_verify_empty_chain_returns_true() -> None:
    chain = LogChain()

    assert chain.verify() is True


def test_verify_explicit_valid_records_returns_true() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")

    assert chain.verify([first, second]) is True


def test_verify_rejects_sequence_gap() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")
    tampered = [first, replace(second, sequence=3)]

    assert chain.verify(tampered) is False


def test_verify_rejects_broken_linkage() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")
    tampered = [first, replace(second, previous_hash="BROKEN")]

    assert chain.verify(tampered) is False


def test_verify_rejects_tampered_message() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")
    tampered = [first, replace(second, message="tampered event")]

    assert chain.verify(tampered) is False


def test_verify_rejects_tampered_timestamp() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")
    tampered = [first, replace(second, occurred_at=second.occurred_at.replace(minute=59))]

    assert chain.verify(tampered) is False


def test_verify_external_tampered_list_does_not_mutate_internal_state() -> None:
    chain = LogChain()
    first = chain.append("synthetic audit event one")
    second = chain.append("synthetic audit event two")
    tampered = [first, replace(second, message="tampered event")]

    assert chain.verify(tampered) is False
    assert chain.verify() is True
