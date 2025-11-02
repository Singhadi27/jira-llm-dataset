import asyncio
import aiohttp
import json
import os
from tenacity import retry, stop_after_attempt, wait_fixed

JIRA_API_URL = "https://issues.apache.org/jira/rest/api/2/search"
JIRA_ISSUE_URL = "https://issues.apache.org/jira/rest/api/2/issue"


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
async def fetch_page(session, project_key, start_at, max_results=30):
    """Fetch a single page of issues for a given JIRA project."""
    jql = f"project={project_key}"
    params = {"jql": jql, "startAt": start_at, "maxResults": max_results}
    async with session.get(JIRA_API_URL, params=params) as resp:
        if resp.status != 200:
            raise Exception(f"Failed to fetch {project_key} page at {start_at}, status={resp.status}")
        return await resp.json()


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
async def fetch_issue(session, issue_key):
    """Fetch full issue details for a given issue key."""
    async with session.get(f"{JIRA_ISSUE_URL}/{issue_key}") as resp:
        if resp.status != 200:
            raise Exception(f"Failed to fetch issue {issue_key}, status={resp.status}")
        return await resp.json()


async def scrape_project(project_key: str, output_dir="sample_output"):
    """Scrape all issues for a given JIRA project and save as JSONL."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{project_key}_raw.jsonl")

    # resume support: skip already fetched issues
    already_fetched = 0
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            already_fetched = sum(1 for _ in f)
        print(f"[{project_key}] Resuming — {already_fetched} issues already saved.")

    connector_sem = asyncio.Semaphore(10)
    total = None

    async with aiohttp.ClientSession() as session:
        start_at = already_fetched
        while True:
            try:
                page = await fetch_page(session, project_key, start_at)
            except Exception as e:
                print(f"[{project_key}] ERROR fetching page at {start_at}: {e}. Retrying...")
                continue

            issues = page.get("issues", []) or []
            if total is None:
                total = page.get("total", None)
            if not issues:
                print(f"[{project_key}] No more issues found, scraping complete.")
                break

            async def fetch_and_write(issue_summary):
                key = issue_summary.get("key")
                try:
                    async with connector_sem:
                        raw_issue = await fetch_issue(session, key)
                except Exception as e:
                    print(f"[{project_key}] Failed to fetch issue {key}: {e}")
                    return None

                fields = raw_issue.get("fields", {}) or {}

                comments = []
                for c in fields.get("comment", {}).get("comments", []):
                    comments.append({
                        "author": c.get("author", {}).get("displayName") if c.get("author") else None,
                        "body_html": c.get("body") or c.get("renderedBody") or None,
                        "created_at": c.get("created")
                    })

                rec = {
                    "key": raw_issue.get("key"),
                    "project": fields.get("project", {}).get("key") if fields.get("project") else project_key,
                    "title": fields.get("summary"),
                    "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                    "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                    "reporter": fields.get("creator", {}).get("displayName") if fields.get("creator") else None,
                    "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                    "labels": fields.get("labels") or [],
                    "created_at": fields.get("created"),
                    "updated_at": fields.get("updated"),
                    "description": fields.get("description") or "",
                    "comments": comments,
                    "source_url": f"https://issues.apache.org/jira/browse/{raw_issue.get('key')}"
                }

                return rec

            tasks = [asyncio.create_task(fetch_and_write(s)) for s in issues]
            written = 0

            # append results
            with open(out_path, "a", encoding="utf-8") as f:
                for coro in asyncio.as_completed(tasks):
                    rec = await coro
                    if rec:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        written += 1

            print(f"[{project_key}] wrote {written} issues. progress {start_at + written}/{total}")
            start_at += len(issues)

            if total and start_at >= total:
                break

    print(f"[{project_key}] ✅ scraping complete — saved to {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="JIRA project key, e.g. HADOOP or KAFKA")
    parser.add_argument("--output_dir", default="sample_output")
    args = parser.parse_args()

    asyncio.run(scrape_project(args.project.upper(), args.output_dir))

