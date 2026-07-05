# Coverage Baseline

Synthetic baseline for Tellson's Bank. Run
`python3 scripts/coverage_baseline.py` to print the machine-readable version of
this baseline.

The goal is to mirror a common enterprise problem: broad repo coverage appears
near 30%, but compliance-critical branch coverage is materially lower in the
classes an examiner will care about.

| Family | Primary target | Baseline branch posture | Remediation expectation |
| --- | --- | --- | --- |
| Transaction | `payments-core/AmountValidator`, `TransferService` | Synthetic baseline: 22% targeted branch coverage; many validation and exception branches uncovered | Raise targeted class coverage toward 80-90% |
| Authentication | `auth-gateway/SessionTokenVerifier`, `LockoutCounter` | Synthetic baseline: 10% targeted branch coverage; verifier effectively uncovered | Add token and threshold edge cases |
| PII | `pii-vault/MaskingService`, `statements-api/StatementAssembler` | Synthetic baseline: 18% targeted branch coverage; canonical happy paths only | Add boundary and leakage tests |
| Audit | `audit-logger/LogChain`, `Redactor` | Undefined because no test harness exists | Bootstrap pytest, coverage, mocks, and CI |

## Why Targeted Coverage Matters

Repo-level coverage is the wrong metric for this compliance program. Support services can have
reasonable smoke coverage while the regulatory paths remain weak. PRs should
therefore report targeted branch coverage for the touched classes/modules and
avoid claiming whole-repo remediation.

## Evidence Requirements

Every finished PR should include:

- before/after branch coverage for targeted classes or modules
- commands run
- synthetic fixtures used
- CI link or coverage artifact
- explicit statement that no production-code files changed
- reviewer checklist
