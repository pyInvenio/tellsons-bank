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

    body = {
        "body": (
            "Opened a Devin session for this coverage workflow:\n\n"
            f"- Session: {session.get('url', session.get('session_id', 'unknown'))}\n"
            f"- Tags: {', '.join(session.get('tags', []))}"
        )
    }
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
    return [item.strip() for item in raw.split(",") if item.strip()]


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
    playbook_id = os.environ.get("DEVIN_PLAYBOOK_ID")
    if playbook_id:
        payload["playbook_id"] = playbook_id
    knowledge_ids = parse_knowledge_ids(os.environ.get("DEVIN_KNOWLEDGE_IDS"))
    if knowledge_ids:
        payload["knowledge_ids"] = knowledge_ids
    if args.devin_mode:
        payload["devin_mode"] = args.devin_mode

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
        sys.stderr.write(exc.read().decode("utf-8"))
        raise


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
