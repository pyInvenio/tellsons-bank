from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request


def set_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def github_get(path: str) -> object:
    token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def matches(pr: dict, service: str, path_family: str) -> bool:
    title = str(pr.get("title", "")).lower()
    branch = str(pr.get("head", {}).get("ref", "")).lower()
    service_token = service.lower()
    path_token = path_family.lower()
    return (
        (service_token in title or service_token in branch)
        and (path_token in title or path_token in branch or "compliance" in title)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()

    query = urllib.parse.urlencode({"state": "open", "per_page": "100"})
    prs = github_get(f"/pulls?{query}")
    matched = [pr for pr in prs if matches(pr, args.service, args.path)]
    if matched:
        selected = matched[0]
        set_output("exists", "true")
        set_output("url", selected["html_url"])
        set_output("number", str(selected["number"]))
        print(
            "Existing remediation PR found: "
            f"#{selected['number']} {selected['title']} {selected['html_url']}"
        )
        return 0

    set_output("exists", "false")
    set_output("url", "")
    set_output("number", "")
    print(f"No open remediation PR found for {args.service}/{args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
