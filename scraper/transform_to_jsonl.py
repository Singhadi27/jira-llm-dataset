# scraper/transform_to_jsonl.py
"""
Transform raw per-issue JSONL (sample_output/<PROJECT>_raw.jsonl) into final JSONL for LLM training.
Usage:
  python scraper/transform_to_jsonl.py --project HDFS
"""

from pathlib import Path
import argparse
import orjson as json
from bs4 import BeautifulSoup
import re

INPUT_DIR = Path("sample_output")
OUTPUT_DIR = Path("sample_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def html_to_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    txt = soup.get_text(separator="\n")
    return re.sub(r"\n\s+\n", "\n\n", txt).strip()


def simple_summary(text, max_len=200):
    t = text.strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    idx = t.rfind(".", 0, max_len)
    if idx != -1 and idx > max_len // 2:
        return t[:idx + 1]
    return t[:max_len].rstrip() + "..."


def derive_qas(title, description, comments):
    qas = []
    desc = (description or "").strip()
    if desc:
        first_sent = desc.split(".")[0].strip()
        qas.append({"q": "What is the main issue?", "a": first_sent})

    if re.search(r"error|exception|stack", description or "", re.I):
        snippet = ""
        m = re.search(r"([^.]*error[^.]*)", description or "", re.I)
        if m:
            snippet = m.group(1).strip()
        qas.append(
            {"q": "What error or log is reported?", "a": snippet or "See comments or logs."}
        )

    qas.append({"q": "Who reported this issue?", "a": ""})
    return qas


def transform_record(raw):
    description = html_to_text(raw.get("description_html") or raw.get("description"))
    comments_raw = raw.get("comments", []) or []

    comments = []
    for c in comments_raw:
        comments.append(
            {
                "author": c.get("author"),
                "body": html_to_text(c.get("body_html") or c.get("body")),
                "created_at": c.get("created_at"),
            }
        )

    obj = {
        "id": raw.get("key"),
        "project": raw.get("project") or raw.get("fields", {}).get("project", {}).get("key"),
        "title": raw.get("summary") or raw.get("title") or "",
        "status": raw.get("status"),
        "priority": raw.get("priority"),
        "reporter": raw.get("reporter"),
        "assignee": raw.get("assignee"),
        "labels": raw.get("labels", []),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "description": description,
        "comments": comments,
        "source_url": raw.get("source_url"),
    }

    obj["derived_summary"] = simple_summary(
        obj["description"] or obj["title"] or "", max_len=200
    )
    obj["derived_qas"] = derive_qas(
        obj["title"] or "", obj["description"] or "", comments
    )
    return obj


def transform_project(project):
    in_path = INPUT_DIR / f"{project}_raw.jsonl"
    out_path = OUTPUT_DIR / f"{project}_processed.jsonl"

    if not in_path.exists():
        print(f"No raw input found: {in_path}")
        return

    count = 0
    with in_path.open("rb") as inf, out_path.open("wb") as outf:
        for line in inf:
            raw = json.loads(line)
            try:
                out = transform_record(raw)
                outf.write(json.dumps(out) + b"\n")
                count += 1
            except Exception as e:
                print(f"Transform failed for {raw.get('key')}: {e}")
    print(f"[{project}] transformed {count} records -> {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, required=True, help="Project key to transform")
    args = parser.parse_args()
    transform_project(args.project.upper())

