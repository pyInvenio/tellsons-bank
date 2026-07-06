# Dispute-Resolution Audit Path – Evidence Notes

## Baseline

- **Before**: No test harness, no CI job, no coverage config. Branch coverage: **undefined** (0%).
- **After**: pytest + pytest-cov bootstrapped, 33 tests, branch coverage: **100%** on `dispute_resolution/workflow.py`.

## Targeted Module

`dispute_resolution.workflow` — `DisputeWorkflow` class and `DisputeCase` dataclass.

## Branch Coverage Delta

| File | Stmts | Branch | Before | After |
|------|-------|--------|--------|-------|
| `dispute_resolution/__init__.py` | 2 | 0 | undefined | 100% |
| `dispute_resolution/workflow.py` | 20 | 4 | undefined | 100% |

## Edge Cases Covered

1. **Invalid case IDs** — 5 parametrized inputs that do not start with `case_test_` (empty, wrong prefix, prod-like).
2. **Missing transaction ID** — empty string triggers `ValueError`.
3. **OPEN status** — `open_case` returns `DisputeCase` with status `OPEN`.
4. **Approve resolution** — `resolve(approved=True)` yields `CUSTOMER_CREDITED`.
5. **Deny resolution** — `resolve(approved=False)` yields `DENIED`.
6. **Audit reason preservation** — empty, long (2000 chars), unicode, alternate reasons are all preserved verbatim.
7. **Timestamp determinism** — `datetime.now` is mocked via `unittest.mock.patch`; fixed clock injected for deterministic assertions.
8. **Clock advance between steps** — mock clock advances between `open_case` and `resolve`, verifying ordering.
9. **Immutability** — frozen dataclass prevents mutation of `status` and `case_id`.
10. **Multiple independent cases** — resolving one case does not affect another.

## Synthetic Fixtures Used

- `case_test_0001`, `case_test_0002` (case IDs)
- `txn_test_9001`, `txn_test_9002` (transaction IDs)
- `acct_test_source` (referenced in reason text)
- `cust_demo_001` (referenced in unicode reason)
- Fixed timestamps: `2025-06-15T12:00:00Z`, `2025-06-15T12:05:00Z`

## Commands Run

```bash
cd services/dispute-resolution
pip install pytest pytest-cov
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=dispute_resolution --cov-branch --cov-report=term-missing --cov-report=html:htmlcov
```

## Flaky-Risk Notes

- **No sleeps or wall-clock dependence.** All timestamps use injected mocks.
- **No network calls.** All tests are purely in-memory.
- **No filesystem I/O.** DisputeWorkflow is stateless.
- **Parametrized invalid IDs** are deterministic string literals.
- **Risk: None identified.** All tests are deterministic.

## Findings

No production-code defects observed. All branches behave as documented.
