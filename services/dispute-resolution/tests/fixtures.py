"""Synthetic fixtures for dispute-resolution compliance tests.

All identifiers use test_/demo_ prefixes per Tellson's synthetic data policy.
"""

from __future__ import annotations

from datetime import datetime, timezone

VALID_CASE_ID = "case_test_0001"
VALID_CASE_ID_ALT = "case_test_0002"
VALID_TXN_ID = "txn_test_9001"
VALID_TXN_ID_ALT = "txn_test_9002"
VALID_REASON = "unauthorized charge on acct_test_source"
VALID_REASON_ALT = "duplicate debit for txn_test_9001"

INVALID_CASE_IDS = [
    "CASE_0001",
    "dispute_0001",
    "",
    "case_prod_0001",
    "random_string",
]

EMPTY_TXN_ID = ""

FIXED_TIMESTAMP = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
FIXED_TIMESTAMP_ALT = datetime(2025, 6, 15, 12, 5, 0, tzinfo=timezone.utc)
