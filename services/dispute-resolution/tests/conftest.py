"""Shared pytest fixtures for dispute-resolution tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from dispute_resolution.workflow import DisputeWorkflow

from .fixtures import FIXED_TIMESTAMP


@pytest.fixture()
def workflow() -> DisputeWorkflow:
    return DisputeWorkflow()


@pytest.fixture()
def frozen_clock():
    """Patch datetime.now inside the workflow module to return a fixed timestamp."""
    with patch(
        "dispute_resolution.workflow.datetime"
    ) as mock_dt:
        mock_dt.now.return_value = FIXED_TIMESTAMP
        mock_dt.side_effect = lambda *a, **kw: __import__("datetime").datetime(*a, **kw)
        yield mock_dt
