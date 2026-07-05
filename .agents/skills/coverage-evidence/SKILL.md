---
name: coverage-evidence
description: Use when generating, parsing, or explaining Tellson's Bank coverage evidence from JaCoCo, Jest, Python tests, or the compliance coverage ratchet.
---

# Coverage Evidence

Use targeted branch coverage as the primary compliance metric.

## Commands

Java:

```bash
gradle :services:payments-core:test :services:pii-vault:test :services:accounts-ledger:test :services:fraud-signals:test
```

TypeScript:

```bash
cd services/<service>
npm install
npm test
```

Python support:

```bash
cd services/<service>
python -m unittest discover -s tests -p '*_test.py'
```

Baseline summary:

```bash
python3 scripts/coverage_baseline.py
```

Ratchet:

```bash
python3 .github/scripts/coverage_gate.py --paths transaction,auth,pii,audit --min 80
```

## Reports

- JaCoCo XML: `services/<java-service>/build/reports/jacoco/test/jacocoTestReport.xml`
- JaCoCo HTML: `services/<java-service>/build/reports/jacoco/test/html/index.html`
- Jest summary: `services/<ts-service>/coverage/coverage-summary.json`
- Jest HTML: `services/<ts-service>/coverage/lcov-report/index.html`

If a report is missing for `audit-logger`, treat coverage as `undefined` and recommend bootstrapping pytest, coverage, mocks, and CI.
