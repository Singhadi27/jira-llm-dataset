#!/usr/bin/env bash
set -euo pipefail
source venv/bin/activate

for project in HDFS SPARK HBASE; do
  echo "🚀 Scraping $project ..."
  python scraper/scraper_api.py --project "$project"
done

python scraper/transform_to_jsonl.py --project HDFS
python scraper/transform_to_jsonl.py --project SPARK
python scraper/transform_to_jsonl.py --project HBASE

echo "✅ Done. Outputs in sample_output/*.jsonl"

