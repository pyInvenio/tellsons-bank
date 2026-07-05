from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request


API_BASE = "https://api.devin.ai/v3"
SCOPES = {
    "core-four": [
        ("payments-core", "transaction"),
        ("auth-gateway", "auth"),
        ("pii-vault", "pii"),
        ("audit-logger", "audit"),
    ],
    "no-infra-python": [
        ("audit-logger", "audit"),
        ("dispute-resolution", "audit"),
    ],
    "all-services": [
        ("payments-core", "transaction"),
        ("accounts-ledger", "transaction"),
        ("fraud-signals", "transaction"),
        ("risk-scoring", "transaction"),
        ("notification-dispatch", "transaction"),
        ("auth-gateway", "auth"),
        ("loan-origination", "auth"),
        ("pii-vault", "pii"),
        ("statements-api", "pii"),
        ("customer-profile", "pii"),
        ("audit-logger", "audit"),
        ("dispute-resolution", "audit"),
    ],
}


def parse_knowledge_ids(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def post_session(payload: dict[str, object]) -> dict:
    request = urllib.request.Request(
        f"{API_BASE}/organizations/{os.environ['DEVIN_ORG_ID']}/sessions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['DEVIN_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def append_summary(results: list[dict]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("## Devin coverage swarm\n\n")
        for result in results:
            session = result["session"]
            handle.write(
                f"- {result['service']} / {result['path']}: "
                f"{session.get('url', session.get('session_id', 'unknown'))}\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=sorted(SCOPES), default="core-four")
    parser.add_argument("--max-sessions", type=int, default=4)
    parser.add_argument("--max-acu-limit", type=int, default=10)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--repo", default=os.environ.get("DEVIN_REPO", ""))
    parser.add_argument("--devin-mode", choices=["normal", "fast", "lite", "ultra", "fusion"])
    args = parser.parse_args()

    playbook_id = os.environ.get("DEVIN_PLAYBOOK_ID")
    knowledge_ids = parse_knowledge_ids(os.environ.get("DEVIN_KNOWLEDGE_IDS"))
    tasks = SCOPES[args.scope][: args.max_sessions]
    results: list[dict] = []
    for service, path_family in tasks:
        payload: dict[str, object] = {
            "title": f"Swarm triage: {path_family} coverage for {service}",
            "prompt": (
                f"!compliance-tests {service} {path_family}\n\n"
                "You are one session in a bounded Tellson's Bank coverage swarm. "
                "Aggressively improve targeted branch coverage for this service/path using tests, "
                "fixtures, mocks, CI wiring, and evidence notes only. Use synthetic fixtures only. "
                "Do not change production code. If behavior appears defective, write a finding with "
                "reproduction steps and stop before remediation. Coordinate through clear PR titles, "
                "coverage delta tables, and reviewer checklists."
            ),
            "tags": ["tellsons-occ", "swarm", path_family, service],
            "max_acu_limit": args.max_acu_limit,
            "repos": [args.repo] if args.repo else [],
        }
        if playbook_id:
            payload["playbook_id"] = playbook_id
        if knowledge_ids:
            payload["knowledge_ids"] = knowledge_ids
        if args.devin_mode:
            payload["devin_mode"] = args.devin_mode
        session = post_session(payload)
        result = {"service": service, "path": path_family, "session": session}
        results.append(result)
        print(json.dumps(result, indent=2))
        time.sleep(args.sleep)
    append_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
