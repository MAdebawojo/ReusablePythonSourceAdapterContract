import argparse
import os
import sys

from iris_ingest.adapters.fixture import FixtureAdapter
from iris_ingest.adapters.fixture_csv import FixtureCsvAdapter
from iris_ingest.loaders import JsonlLoader

ADAPTERS = {
    "json": FixtureAdapter,
    "csv": FixtureCsvAdapter,
}

DEFAULT_INPUTS = {
    "json": "fixtures/raw_records.json",
    "csv": "fixtures/csv_records.csv",
}


def main():
    parser = argparse.ArgumentParser(
        description="Run a Project IRIS source adapter end-to-end."
    )
    parser.add_argument("--source", choices=ADAPTERS.keys(), default="json")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default="output/example_output.jsonl")
    args = parser.parse_args()

    input_path = args.input or DEFAULT_INPUTS[args.source]
    adapter = ADAPTERS[args.source](input_path)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    with JsonlLoader(args.output) as loader:
        result = adapter.run(loader)

    print(f"Adapter: {result.adapter_name}")
    print(f"Total extracted: {result.total_extracted}")
    print(f"Accepted: {result.accepted_count}")
    print(f"Rejected: {len(result.rejections)}")
    for r in result.rejections:
        identifier = r.raw_record.get("source_id") or r.raw_record.get("unique_code") or "unknown source" # default to "unknown source" if neither is present; for display purposes only
        print(f"  - {identifier}: {r.reason}")

    if result.accepted_count < 20:
        print("WARNING: fewer than 20 records accepted", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()