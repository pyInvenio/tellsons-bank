from __future__ import annotations

import json
import os
import re
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


def labels_for(event: dict) -> list[str]:
    issue = event.get("issue") or {}
    return [label.get("name", "") for label in issue.get("labels", [])]


def infer_from_text(text: str) -> tuple[str, str]:
    lowered = text.lower()
    for service, path in SERVICES.items():
        if service in lowered:
            return service, path
    if re.search(r"\b(jwt|token|login|auth|lockout)\b", lowered):
        return "auth-gateway", "auth"
    if re.search(r"\b(pii|ssn|mask|statement|profile|redact)\b", lowered):
        return "pii-vault", "pii"
    if re.search(r"\b(audit|hash|log|dispute)\b", lowered):
        return "audit-logger", "audit"
    return "payments-core", "transaction"


def resolve(event: dict) -> tuple[str, str]:
    labels = labels_for(event)
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

    issue = event.get("issue") or {}
    text = f"{issue.get('title', '')}\n{issue.get('body', '')}"
    return infer_from_text(text)


def main() -> int:
    event_path = os.environ["GITHUB_EVENT_PATH"]
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    service, path = resolve(event)
    issue = event.get("issue") or {}
    issue_title = issue.get("title", "test gap")
    title = f"Issue trigger: {path} coverage for {service}"
    prompt = (
        f"!compliance-tests {service} {path}\n\n"
        f"Triggered by GitHub issue #{issue.get('number')}: {issue_title}\n\n"
        "Use synthetic fixtures only. Add tests, fixtures, mocks, CI wiring, and evidence notes. "
        "Do not change production code. If product behavior appears defective, write a finding "
        "with reproduction steps and stop before remediation.\n\n"
        f"Issue body:\n{issue.get('body', '')}"
    )
    prompt_file = Path(os.environ.get("RUNNER_TEMP", ".")) / "devin_issue_prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    set_output("service", service)
    set_output("path_family", path)
    set_output("title", title)
    set_output("prompt_file", str(prompt_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
