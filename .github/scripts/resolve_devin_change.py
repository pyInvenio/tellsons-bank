from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


PATHS = {"transaction", "auth", "pii", "audit"}
DEFAULTS = {
    "transaction": "payments-core",
    "auth": "auth-gateway",
    "pii": "pii-vault",
    "audit": "audit-logger",
}
SERVICES = {
    "payments-core": "transaction",
    "accounts-ledger": "transaction",
    "fraud-signals": "transaction",
    "risk-scoring": "transaction",
    "notification-dispatch": "transaction",
    "auth-gateway": "auth",
    "loan-origination": "auth",
    "pii-vault": "pii",
    "statements-api": "pii",
    "customer-profile": "pii",
    "audit-logger": "audit",
    "dispute-resolution": "audit",
}


def set_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def event() -> dict:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def labels_for(data: dict) -> list[str]:
    issue = data.get("issue") or data.get("pull_request") or {}
    return [label.get("name", "") for label in issue.get("labels", [])]


def explicit_target(data: dict) -> tuple[str, str] | None:
    labels = labels_for(data)
    path = ""
    service = ""
    for label in labels:
        if label.startswith("path:") and label.split(":", 1)[1] in PATHS:
            path = label.split(":", 1)[1]
        if label.startswith("service:"):
            candidate = label.split(":", 1)[1]
            if candidate in SERVICES:
                service = candidate
    if service and not path:
        path = SERVICES[service]
    if path and not service:
        service = DEFAULTS[path]
    if service and path:
        return service, path
    return None


def changed_files_from_git(data: dict) -> list[str]:
    before = os.environ.get("BASE_SHA")
    after = os.environ.get("HEAD_SHA")
    if not before or not after:
        if data.get("pull_request"):
            before = data["pull_request"]["base"]["sha"]
            after = data["pull_request"]["head"]["sha"]
        elif data.get("before") and data.get("after"):
            before = data["before"]
            after = data["after"]
    if not before or not after:
        return []
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", before, after],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def infer_from_files(files: list[str]) -> tuple[str, str] | None:
    counts: dict[str, int] = {}
    for file_name in files:
        parts = Path(file_name).parts
        if len(parts) >= 2 and parts[0] == "services" and parts[1] in SERVICES:
            counts[parts[1]] = counts.get(parts[1], 0) + 1
    if not counts:
        return None
    service = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return service, SERVICES[service]


def infer_from_text(data: dict) -> tuple[str, str]:
    issue = data.get("issue") or {}
    pull_request = data.get("pull_request") or {}
    text = "\n".join(
        [
            issue.get("title", ""),
            issue.get("body", ""),
            pull_request.get("title", ""),
            pull_request.get("body", ""),
        ]
    ).lower()
    for service, path in SERVICES.items():
        if service in text:
            return service, path
    if re.search(r"\b(jwt|token|login|auth|lockout)\b", text):
        return "auth-gateway", "auth"
    if re.search(r"\b(pii|ssn|mask|statement|profile|redact)\b", text):
        return "pii-vault", "pii"
    if re.search(r"\b(audit|hash|log|dispute)\b", text):
        return "audit-logger", "audit"
    return "payments-core", "transaction"


def event_reference(data: dict) -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "pyInvenio/tellsons-bank")
    if data.get("pull_request"):
        number = data["pull_request"]["number"]
        return f"https://github.com/{repository}/pull/{number}"
    if data.get("issue"):
        number = data["issue"]["number"]
        return f"https://github.com/{repository}/issues/{number}"
    sha = os.environ.get("GITHUB_SHA", "")
    if sha:
        return f"https://github.com/{repository}/commit/{sha}"
    return f"https://github.com/{repository}"


def write_prompt(
    kind: str,
    service: str,
    path_family: str,
    files: list[str],
    data: dict,
) -> Path:
    prompt_file = Path(os.environ.get("RUNNER_TEMP", ".")) / f"devin_{kind}_prompt.txt"
    changed = "\n".join(f"- {file_name}" for file_name in files[:80]) or "- No changed files detected"
    reference = event_reference(data)
    if kind == "qa":
        prompt = f"""QA review this Tellson's Bank change.

Reference: {reference}
Primary inferred path: {path_family}
Primary inferred service: {service}

Changed files:
{changed}

Review only unless explicitly asked to patch. Verify:
- tests run and failures are explained
- coverage evidence is present for touched compliance paths
- no production-code changes appear in a test-only PR unless the human requested them
- fixtures are synthetic and no real downstream calls are introduced
- PR description includes commands, coverage delta, edge cases, flaky-risk notes, and reviewer checklist

Return a concise QA report with pass/fail status, blocking issues, nonblocking risks,
commands that should be run, and recommended next action. If a code change is truly needed,
ask before editing.
"""
    else:
        prompt = f"""!compliance-tests {service} {path_family}

Triggered from a Tellson's Bank change event.

Reference: {reference}
Changed files:
{changed}

Aggressively improve test coverage for the inferred compliance path while staying inside
the test-coverage scope. Add tests, fixtures, mocks, CI wiring, and evidence notes. Use
synthetic fixtures only. Do not change production code. If production behavior appears
defective, write a finding with reproduction steps and stop before remediation.
"""
    prompt_file.write_text(prompt, encoding="utf-8")
    return prompt_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["coverage", "qa"], required=True)
    parser.add_argument("--service")
    parser.add_argument("--path", choices=sorted(PATHS))
    args = parser.parse_args()

    data = event()
    files = changed_files_from_git(data)
    if args.service and args.path:
        service, path_family = args.service, args.path
    else:
        target = explicit_target(data) or infer_from_files(files) or infer_from_text(data)
        service, path_family = target

    title_prefix = "QA review" if args.kind == "qa" else "Change trigger"
    title = f"{title_prefix}: {path_family} coverage for {service}"
    prompt_file = write_prompt(args.kind, service, path_family, files, data)
    set_output("service", service)
    set_output("path_family", path_family)
    set_output("title", title)
    set_output("prompt_file", str(prompt_file))
    set_output("changed_files", json.dumps(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
