import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import csv
from pathlib import Path

BASE_URL = "https://issues.apache.org/jira/browse"

async def fetch_issue(session, issue_key):
    url = f"https://issues.apache.org/jira/rest/api/2/issue/{issue_key}"
    async with session.get(url) as response:
        if response.status != 200:
            print(f"❌ Failed to fetch {issue_key}: {response.status}")
            return None

        data = await response.json()
        fields = data.get("fields", {})

        return {
            "key": issue_key,
            "title": fields.get("summary"),
            "description": fields.get("description"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "reporter": fields.get("reporter", {}).get("displayName"),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "labels": fields.get("labels", []),
            "created_at": fields.get("created"),
            "updated_at": fields.get("updated"),
            "source_url": f"https://issues.apache.org/jira/browse/{issue_key}"
        }

async def scrape_jira(project_key="HADOOP", start=10000, end=10010):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_issue(session, f"{project_key}-{i}") for i in range(start, end)]
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scraping Jira"):
            issue = await coro
            if issue["title"]:
                results.append(issue)
    return results

def save_data(data, project):
    output_dir = Path("../data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / f"{project.lower()}_issues.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    # Save CSV (include all keys that may appear)
    csv_path = output_dir / f"{project.lower()}_issues.csv"
    fieldnames = [
        "key",
        "title",
        "description",
        "status",
        "priority",
        "reporter",
        "assignee",
        "labels",
        "created_at",
        "updated_at",
        "source_url"
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Data saved to:\n  - {json_path}\n  - {csv_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, default="HADOOP", help="Jira project key (e.g., HADOOP, KAFKA, SPARK)")
    parser.add_argument("--start", type=int, default=10000, help="Start issue number")
    parser.add_argument("--end", type=int, default=10010, help="End issue number")
    args = parser.parse_args()

    # Run scraper
    data = asyncio.run(scrape_jira(args.project, args.start, args.end))

    print("\nSample Issues:")
    for issue in data[:5]:
        print(f"{issue['key']}: {issue['title']}")

    save_data(data, args.project)

