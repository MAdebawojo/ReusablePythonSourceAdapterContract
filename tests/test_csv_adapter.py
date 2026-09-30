from iris_ingest.adapters.fixture_csv import FixtureCsvAdapter
from iris_ingest.loaders import JsonlLoader


def test_csv_adapter_processes_fixture_without_core_changes(tmp_path):
    adapter = FixtureCsvAdapter("fixtures/csv_records.csv")
    output_path = tmp_path / "csv_output.jsonl"

    with JsonlLoader(str(output_path)) as loader:
        result = adapter.run(loader)

    assert result.total_extracted == 29
    assert result.accepted_count == 24
    assert len(result.rejections) == 5