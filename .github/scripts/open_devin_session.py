from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


API_BASE = "https://api.devin.ai/v3"


def post_github_comment(session: dict) -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repository = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not event_path or not repository or not token:
        return

    event = json.loads(open(event_path, encoding="utf-8").read())
    issue_number = event.get("pull_request", {}).get("number") or event.get("issue", {}).get("number")
    if not issue_number:
        return

    comment = (
        "Opened a Devin session for this coverage workflow:\n\n"
        f"- Session: {session.get('url', session.get('session_id', 'unknown'))}\n"
        f"- Tags: {', '.join(session.get('tags', []))}"
    )
    trigger_summary = read_trigger_summary()
    if trigger_summary:
        comment = f"{comment}\n\n{trigger_summary}"
    body = {"body": comment}
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/issues/{issue_number}/comments",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30):
        pass


def read_trigger_summary() -> str:
    summary_file = os.environ.get("DEVIN_TRIGGER_SUMMARY_FILE")
    if not summary_file:
        return ""
    path = Path(summary_file)
    if not path.exists():
        return ""
    contents = path.read_text(encoding="utf-8").strip()
    if not contents:
        return ""
    max_chars = 12000
    if len(contents) > max_chars:
        return contents[:max_chars] + "\n\n_Trimmed; see the workflow artifact for full evidence._"
    return contents


def append_step_summary(session: dict) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("## Devin session\n\n")
        handle.write(f"- Session: {session.get('url', session.get('session_id', 'unknown'))}\n")
        handle.write(f"- Tags: {', '.join(session.get('tags', []))}\n")


def parse_knowledge_ids(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [normalize_resource_id(item, "knowledge_") for item in raw.split(",") if item.strip()]


def normalize_resource_id(value: str, expected_prefix: str) -> str:
    trimmed = value.strip().strip("'\"")
    without_query = trimmed.split("?", 1)[0].split("#", 1)[0]
    resource_id = next(reversed([part for part in without_query.split("/") if part]), trimmed)
    if resource_id.startswith(expected_prefix):
        return resource_id
    return f"{expected_prefix}{resource_id}"


def get_playbook_id() -> str | None:
    raw = os.environ.get("DEVIN_PLAYBOOK_ID") or os.environ.get(
        "DEVIN_PLAYBOOK_ID_COMPLIANCE_TESTS"
    )
    return normalize_resource_id(raw, "playbook_") if raw else None


def get_knowledge_ids() -> list[str]:
    explicit = parse_knowledge_ids(os.environ.get("DEVIN_KNOWLEDGE_IDS"))
    if explicit:
        return explicit
    keys = [
        "DEVIN_KNOWLEDGE_ID_TELLSONS_DEMO_CONTEXT",
        "DEVIN_KNOWLEDGE_ID_TELLSONS_COMPLIANCE_PATHS",
        "DEVIN_KNOWLEDGE_ID_TELLSONS_DEVIN_API_NOTES",
    ]
    return [
        normalize_resource_id(os.environ[key], "knowledge_")
        for key in keys
        if os.environ.get(key)
    ]


def open_session(args: argparse.Namespace) -> dict:
    api_key = os.environ["DEVIN_API_KEY"]
    org_id = os.environ["DEVIN_ORG_ID"]
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = (
            f"!compliance-tests {args.service} {args.path}\n\n"
            "Use synthetic fixtures only. Add tests and CI evidence, but do not modify "
            "production code unless a human explicitly changes the scope."
        )
    payload: dict[str, object] = {
        "title": args.title,
        "prompt": prompt,
        "tags": args.tag,
        "max_acu_limit": args.max_acu_limit,
        "repos": [args.repo] if args.repo else [],
    }
    playbook_id = get_playbook_id()
    if playbook_id:
        payload["playbook_id"] = playbook_id
    knowledge_ids = get_knowledge_ids()
    if knowledge_ids:
        payload["knowledge_ids"] = knowledge_ids
    if args.devin_mode:
        payload["devin_mode"] = args.devin_mode

    return post_session(org_id, api_key, payload)


def post_session(org_id: str, api_key: str, payload: dict[str, object]) -> dict:
    request = urllib.request.Request(
        f"{API_BASE}/organizations/{org_id}/sessions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        if should_retry_without_workspace_assets(exc, body, payload):
            sys.stderr.write(
                "Devin rejected the configured playbook/knowledge IDs. "
                "Retrying as a prompt-only session. Update DEVIN_PLAYBOOK_ID "
                "and DEVIN_KNOWLEDGE_IDS to re-enable attached workspace assets.\n"
            )
            prompt_only_payload = dict(payload)
            prompt_only_payload.pop("playbook_id", None)
            prompt_only_payload.pop("knowledge_ids", None)
            prompt_only_payload["prompt"] = append_local_guidance(
                str(prompt_only_payload["prompt"])
            )
            return post_session(org_id, api_key, prompt_only_payload)
        sys.stderr.write(body)
        raise


def should_retry_without_workspace_assets(
    exc: urllib.error.HTTPError, body: str, payload: dict[str, object]
) -> bool:
    if os.environ.get("DEVIN_STRICT_WORKSPACE_ASSETS", "").lower() in {"1", "true", "yes"}:
        return False
    if exc.code != 400:
        return False
    if "playbook_id" not in payload and "knowledge_ids" not in payload:
        return False
    normalized = body.lower()
    return "playbook" in normalized or "knowledge" in normalized


def append_local_guidance(prompt: str) -> str:
    skill_paths = [
        Path(".agents/skills/compliance-tests/SKILL.md"),
        Path(".agents/skills/coverage-evidence/SKILL.md"),
        Path(".agents/skills/no-prod-code-test-pr/SKILL.md"),
    ]
    sections = [
        f"## Local Guidance: {path.parent.name}\n\n{path.read_text(encoding='utf-8').strip()}"
        for path in skill_paths
        if path.exists()
    ]
    if not sections:
        return prompt
    return (
        f"{prompt}\n\n---\n\nLOCAL DEVIN RESOURCES\n"
        "These committed repo-local resources mirror the Devin workspace playbook "
        "and knowledge. Treat them as trusted operating guidance for this session.\n\n"
        + "\n\n".join(sections)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--path", required=True, choices=["transaction", "auth", "pii", "audit"])
    parser.add_argument("--title", required=True)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--max-acu-limit", type=int, default=10)
    parser.add_argument("--repo", default=os.environ.get("DEVIN_REPO", ""))
    parser.add_argument("--devin-mode", choices=["normal", "fast", "lite", "ultra", "fusion"])
    parser.add_argument("--comment-on-pr", action="store_true")
    parser.add_argument("--comment-on-github", action="store_true")
    args = parser.parse_args()
    result = open_session(args)
    print(json.dumps(result, indent=2))
    if "url" in result:
        print(f"Devin session: {result['url']}")
    append_step_summary(result)
    if args.comment_on_pr or args.comment_on_github:
        post_github_comment(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
