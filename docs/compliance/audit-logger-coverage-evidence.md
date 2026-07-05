# Audit Path Coverage Evidence — `audit-logger`

Compliance path: **audit**. Primary targets: `LogChain` and `Redactor`
(with supporting coverage for `FileAuditSink`, `AuditFormatter`, and
`AuditLoggerService`).

This PR bootstraps the previously-missing test infrastructure for
`services/audit-logger` and raises targeted branch coverage from **undefined**
(no pytest, no coverage config, no CI job, no mocks) to **100%**. No production
code was changed.

## Commands Run

```bash
# from services/audit-logger
pip install -r requirements-dev.txt

# narrow target suite (primary targets)
python -m pytest tests/log_chain_test.py tests/redactor_test.py -q

# service-level suite with branch coverage
python -m coverage run -m pytest
python -m coverage report -m
python -m coverage json -o coverage.json
python -m coverage html -d coverage_html

# ratchet gate (audit path)
python3 ../../.github/scripts/coverage_gate.py --paths audit --min 80
```

## Branch Coverage Before / After

| Module | Before | After (branch) |
| --- | --- | --- |
| `audit_logger/log_chain.py` (`LogChain`) | undefined (no harness) | 100% (8/8 branches) |
| `audit_logger/redactor.py` (`Redactor`) | undefined | 100% |
| `audit_logger/sink.py` (`FileAuditSink`) | undefined | 100% |
| `audit_logger/formatter.py` (`AuditFormatter`) | undefined | 100% |
| `audit_logger/service.py` (`AuditLoggerService`) | undefined | 100% |
| **Service total** | **undefined** | **100% (8/8 branches, 78/78 stmts)** |

Ratchet gate for the audit path: `below_threshold=false` after the change
(was `undefined < 80` before).

## Edge Cases Covered

- **Hash chain (`LogChain`)**: empty chain, first record links to `GENESIS`,
  subsequent record links to previous hash, default vs. explicit record list,
  sequence gap, broken previous-hash link, tampered message, tampered
  timestamp, tampered stored hash, external list does not mutate internal state,
  deterministic hash under a fixed clock.
- **Redaction (`Redactor`)**: single SSN, multiple SSNs, account IDs with
  surrounding punctuation, combined SSN + account, near-miss short SSN,
  too-short account suffix, message with no PII, empty string.
- **Sink (`FileAuditSink`)**: parent directory creation, append across writes,
  newline termination, exception on unwritable path.
- **Formatter (`AuditFormatter`)**: field order and pipe separators.
- **Service (`AuditLoggerService`)**: PII redacted before write, returned hash
  matches chain and formatted line, one line written per event.

## Synthetic Fixtures Used

- `services/audit-logger/tests/fixtures/synthetic_redaction_cases.json`
  (synthetic IDs only: `000-00-0000`, `acct_test_*`, `acct_demo_*`,
  `cust_test_*`).
- Downstream file sink is replaced by `tmp_path` and an in-memory
  `RecordingSink` test double. No real network calls.

## Flaky-Risk Notes

- The clock inside `LogChain.append` is patched to a fixed sequence via the
  `frozen_clock` fixture (`tests/conftest.py`), so hashes are deterministic.
- No `sleep`, no wall-clock assertions, no shared filesystem paths — all file
  writes go through `tmp_path`.
- No external services or network access.

## Reviewer Checklist

- [x] Tests cover error handling and data validation for the audit path.
- [x] Fixtures are synthetic and contain no realistic customer data.
- [x] No real network calls are made.
- [x] No production files changed.
- [x] Coverage report / CI evidence is linked.
