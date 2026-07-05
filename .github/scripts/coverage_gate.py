from __future__ import annotations

import argparse
import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CoverageTarget:
    path_family: str
    service: str
    report: Path
    report_type: str


@dataclass(frozen=True)
class CoverageGap:
    target: CoverageTarget
    coverage: float | None
    minimum: float

    @property
    def severity_key(self) -> tuple[int, float]:
        if self.coverage is None:
            return (0, 0.0)
        return (1, self.coverage)

    def output_coverage(self) -> str:
        return "undefined" if self.coverage is None else f"{self.coverage:.2f}"


TARGETS = {
    "transaction": CoverageTarget(
        "transaction",
        "payments-core",
        Path("services/payments-core/build/reports/jacoco/test/jacocoTestReport.xml"),
        "jacoco",
    ),
    "auth": CoverageTarget(
        "auth",
        "auth-gateway",
        Path("services/auth-gateway/coverage/coverage-summary.json"),
        "jest",
    ),
    "pii": CoverageTarget(
        "pii",
        "pii-vault",
        Path("services/pii-vault/build/reports/jacoco/test/jacocoTestReport.xml"),
        "jacoco",
    ),
    "audit": CoverageTarget(
        "audit",
        "audit-logger",
        Path("services/audit-logger/coverage.json"),
        "pytest",
    ),
}


def set_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def jacoco_branch_percent(path: Path) -> float | None:
    if not path.exists():
        return None
    root = ET.parse(path).getroot()
    missed = covered = 0
    for counter in root.iter("counter"):
        if counter.attrib.get("type") == "BRANCH":
            missed += int(counter.attrib.get("missed", "0"))
            covered += int(counter.attrib.get("covered", "0"))
    total = missed + covered
    return (covered / total) * 100 if total else 100.0


def jest_branch_percent(path: Path) -> float | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    branches = data.get("total", {}).get("branches", {})
    pct = branches.get("pct")
    return float(pct) if pct is not None else None


def pytest_branch_percent(path: Path) -> float | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    num_branches = totals.get("num_branches")
    covered_branches = totals.get("covered_branches")
    if not num_branches:
        return None
    return (covered_branches / num_branches) * 100


def coverage_for(target: CoverageTarget) -> float | None:
    if target.report_type == "jacoco":
        return jacoco_branch_percent(target.report)
    if target.report_type == "jest":
        return jest_branch_percent(target.report)
    if target.report_type == "pytest":
        return pytest_branch_percent(target.report)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", required=True, help="Comma-separated path families")
    parser.add_argument("--min", type=float, required=True, dest="minimum")
    args = parser.parse_args()

    requested = [path.strip() for path in args.paths.split(",") if path.strip()]
    gaps: list[CoverageGap] = []
    for path_family in requested:
        target = TARGETS[path_family]
        pct = coverage_for(target)
        if pct is None or pct < args.minimum:
            gaps.append(CoverageGap(target, pct, args.minimum))
            print(
                f"{target.path_family}: {target.service} below threshold "
                f"({pct if pct is not None else 'undefined'} < {args.minimum})"
            )

    if gaps:
        selected = sorted(gaps, key=lambda gap: gap.severity_key)[0]
        set_output("below_threshold", "true")
        set_output("service", selected.target.service)
        set_output("path_family", selected.target.path_family)
        set_output("coverage", selected.output_coverage())
        set_output(
            "gaps",
            json.dumps([
                {
                    "path": gap.target.path_family,
                    "service": gap.target.service,
                    "coverage": gap.output_coverage(),
                    "minimum": gap.minimum,
                }
                for gap in gaps
            ]),
        )
        print(
            "selected_gap="
            f"{selected.target.path_family}/{selected.target.service}/"
            f"{selected.output_coverage()}"
        )
        return 1

    set_output("below_threshold", "false")
    set_output("gaps", "[]")
    print("All compliance paths meet threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
