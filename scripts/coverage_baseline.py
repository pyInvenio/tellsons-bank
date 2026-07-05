from __future__ import annotations

import json


BASELINE = [
    {
        "family": "transaction",
        "primary": "payments-core",
        "supporting": ["accounts-ledger", "fraud-signals", "risk-scoring"],
        "targeted_branch_percent": 22,
        "posture": "JUnit/Jacoco exists, but critical validation branches are sparse.",
    },
    {
        "family": "auth",
        "primary": "auth-gateway",
        "supporting": ["loan-origination"],
        "targeted_branch_percent": 10,
        "posture": "Jest exists, but SessionTokenVerifier is effectively uncovered.",
    },
    {
        "family": "pii",
        "primary": "pii-vault",
        "supporting": ["statements-api", "customer-profile"],
        "targeted_branch_percent": 18,
        "posture": "Masking has a canonical happy path; leakage and unicode boundaries are thin.",
    },
    {
        "family": "audit",
        "primary": "audit-logger",
        "supporting": ["dispute-resolution"],
        "targeted_branch_percent": None,
        "posture": "Undefined: no pytest, no coverage config, no CI job, no mocks.",
    },
]


def main() -> int:
    measured = [item["targeted_branch_percent"] for item in BASELINE if item["targeted_branch_percent"] is not None]
    critical_average = sum(measured) / len(measured)
    synthetic_repo_average = 31.4
    payload = {
        "repo_overall_branch_percent": synthetic_repo_average,
        "critical_path_measured_average": round(critical_average, 2),
        "audit_coverage": "undefined",
        "baseline": BASELINE,
        "note": (
            "Overall repo coverage is a synthetic baseline used for compliance planning. "
            "The ratchet uses generated JaCoCo/Jest reports when available and treats "
            "missing audit infrastructure as undefined."
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
