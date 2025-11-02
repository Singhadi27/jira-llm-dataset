import json
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

input_path = args.input
output_path = args.output

# --- Load JSONL file properly ---
issues = []
with open(input_path, "r") as f:
    for line in f:
        if line.strip():
            try:
                issues.append(json.loads(line))
            except json.JSONDecodeError:
                continue

# --- Convert to DataFrame ---
df = pd.DataFrame(issues)

# --- Basic cleaning ---
if "title" in df.columns:
    df["title"] = df["title"].astype(str).str.strip()

if "description" in df.columns:
    df["description"] = (
        df["description"].astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

df.dropna(subset=["title"], inplace=True)
df.drop_duplicates(subset=["title"], inplace=True)

# --- Save outputs ---
csv_path = output_path.replace(".jsonl", ".csv")
df.to_csv(csv_path, index=False)

with open(output_path, "w") as f:
    for record in df.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

print("✅ Cleaned data saved to:")
print(f"  - {csv_path}")
print(f"  - {output_path}")

