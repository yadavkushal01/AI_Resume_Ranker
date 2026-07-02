import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "candidates.jsonl"
OUTPUT_FILE = BASE_DIR / "headlines.csv"


def get_headline(candidate: dict):
    if not isinstance(candidate, dict):
        return ""

    for key in ["headline", "Headline", "title", "Title"]:
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    profile = candidate.get("profile")
    if isinstance(profile, dict):
        for key in ["headline", "Headline", "title", "Title"]:
            value = profile.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return ""


def extract_headlines(input_path: Path, output_path: Path) -> int:
    count = 0
    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["headline"])

        for line_number, line in enumerate(infile, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                candidate = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON on line {line_number}: {exc}")
                continue

            headline = get_headline(candidate)
            writer.writerow([headline])
            count += 1

    return count


if __name__ == "__main__":
    count = extract_headlines(INPUT_FILE, OUTPUT_FILE)
    print(f"Extracted {count} headlines to {OUTPUT_FILE.name}")
