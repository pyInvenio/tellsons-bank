from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from coverage_gate import TARGETS, coverage_for


SERVICES = {
    "payments-core": "transaction",
    "auth-gateway": "auth",
    "pii-vault": "pii",
    "audit-logger": "audit",
}


def changed_files() -> list[str]:
    base = os.environ.get("BASE_SHA")
    head = os.environ.get("HEAD_SHA")
    if not base or not head:
        base = os.environ.get("GITHUB_BASE_REF")
        head = os.environ.get("GITHUB_SHA")
    if not base or not head:
        return []
    result = subprocess.run(
        ["git", "diff", "--name-only", base, head],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_production_file(path: str) -> bool:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "services":
        return False
    service = parts[1]
    if service not in SERVICES:
        return False
    if "/tests/" in f"/{path}" or "/src/test/" in f"/{path}":
        return False
    if path.endswith((".md", ".json")):
        return False
    return (
        path.startswith(f"services/{service}/src/")
        or path.startswith(f"services/{service}/audit_logger/")
    )


def append_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, required=True, dest="minimum")
    args = parser.parse_args()

    files = changed_files()
    touched_services = sorted(
        {
            Path(path).parts[1]
            for path in files
            if is_production_file(path)
        }
    )
    if not touched_services:
        append_summary(
            [
                "## Changed Production Path Coverage",
                "",
                "No compliance production files changed; no changed-path coverage gate needed.",
                "",
            ]
        )
        print("No compliance production files changed")
        return 0

    failures: list[tuple[str, str, str]] = []
    lines = [
        "## Changed Production Path Coverage",
        "",
        "This PR changes compliance-path production code, so the touched path must have "
        f"at least {args.minimum:.2f}% branch coverage.",
        "",
        "| Service | Path | Branch Coverage | Minimum | Status |",
        "|---|---|---:|---:|---|",
    ]
    for service in touched_services:
        path_family = SERVICES[service]
        target = TARGETS[path_family]
        coverage = coverage_for(target)
        coverage_text = "undefined" if coverage is None else f"{coverage:.2f}"
        passed = coverage is not None and coverage >= args.minimum
        status = "pass" if passed else "fail"
        lines.append(
            f"| {service} | {path_family} | {coverage_text} | {args.minimum:.2f} | {status} |"
        )
        if not passed:
            failures.append((service, path_family, coverage_text))

    lines.append("")
    if failures:
        lines.append(
            "Coverage gate failed because production code changed without enough targeted "
            "branch coverage. Add tests or route the PR through Devin QA/remediation."
        )
    else:
        lines.append("Changed production paths meet the coverage threshold.")
    lines.append("")
    append_summary(lines)

    if failures:
        for service, path_family, coverage_text in failures:
            print(
                f"{service}/{path_family} changed production coverage below threshold: "
                f"{coverage_text} < {args.minimum:.2f}"
            )
        return 1

    print("Changed production paths meet threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
