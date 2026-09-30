# Project IRIS — Reusable Python Source Adapter Contract

A small, reusable ingestion core for Project IRIS. Any source adapter
that implements the documented interface can plug in without changes
to extraction, normalization, QA, or staging logic.

## Getting the code

```bash
git clone https://github.com/MAdebawojo/ReusablePythonSourceAdapterContract
cd ReusablePythonSourceAdapterContract
```

## Setup

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running

```bash
python -m iris_ingest.cli --source json
python -m iris_ingest.cli --source csv
```

Writes normalized records to `output/example_output.jsonl` (or
`--output <path>`) and prints a summary of accepted/rejected counts.

## Tests

```bash
pytest -v
```

13 tests currently cover country_code validation/normalization,
geometry validation, and both adapters end-to-end.

## Architecture

```
src/iris_ingest/
  models.py           CanonicalRecord (the canonical contract) + to_dict()
  countries.py         country_code normalize + strict validate
  geometry.py           geom normalize (Point) + validate
  validation.py         validate_record: combines country + geom checks
  errors.py              NormalizationError
  loaders.py             Loader (ABC) + JsonlLoader
  adapter.py              SourceAdapter (base class), run(), RunResult, Rejection
  adapters/
    fixture.py             JSON fixture adapter
    fixture_csv.py           CSV fixture adapter (proves reusability)
fixtures/
  raw_records.json          JSON source fixture (32 records)
  csv_records.csv           CSV source fixture (29 records)
migrations/
  001_staging.sql            staging table schema (country_code, geom, metadata)
tests/
  test_validation.py, test_geometry.py, test_csv_adapter.py
```

The core (everything outside `adapters/`) never changes when a new
source is added. Two adapters exist, with entirely different raw
field names and formats, and neither required editing any core file.

## Design decisions

### CanonicalRecord: frozen dataclass, not Pydantic

A dataclass is a plain data container; it does no validation itself.
That's deliberate: the brief separates extract/normalize/validate/load
into distinct responsibilities, and a dataclass keeps "does this
record hold valid data" entirely inside the `validate` step, rather
than folding it into construction the way Pydantic would. `frozen=True`
prevents a record from being silently mutated as it moves through the
pipeline (note: this does not make nested `dict` fields like
`attributes` immutable — a documented simplification).

Field types:
- `source_date: date` — the date the source data refers to.
- `fetched_at: datetime` (timezone-aware, UTC) — when the record was
  retrieved. Distinct from `source_date` because a source's data can
  be fetched long after it was produced.
- `region_code: str | None`, default `None` — the brief only requires
  `country_code` to be non-null; a source with no region is honestly
  represented as `None`, never invented.
- `attributes: dict[str, Any]` — free-form, so source-specific fields
  with no canonical home are kept, not discarded.
- `geom: dict | None` — GeoJSON, WGS84 (EPSG:4326), coordinates ordered
  `[longitude, latitude]`. `None` when the source has no geometry.

### country_code: strict validate, separate normalize

`validate_country_code` checks **exact, case-sensitive** membership in
the real ISO 3166-1 alpha-2 set (`{c.alpha_2 for c in pycountry.countries}`).
It does not accept lowercase or alpha-3 codes — that would let
validate silently repair data, blurring the line between judging and
fixing.

`normalize_country_code` does the fixing, before validate ever runs:
trims whitespace, uppercases, and converts alpha-3 to alpha-2
(`"deu"` → `"DE"`). It returns `None` if the input is missing, empty,
or an unrecognized alpha-3 code — it never guesses or defaults to a
country, per the brief's explicit "reject rather than default to DE."

One consequence worth noting: an unrecognized alpha-3 code (e.g.
`"DEUT"`, `"XYZ"`) normalizes to `None`, so it's reported as "Missing
country code" rather than "Invalid country code." The original raw
value isn't lost — it's preserved in `Rejection.raw_record` — but the
message itself doesn't distinguish "genuinely absent" from
"unrecognized alpha-3." Judged an acceptable tradeoff for this scope.

### Geometry: Point validated strictly, other types structurally only

The brief's acceptance criteria only mandate rejection for
`country_code`; there is no equivalent explicit rejection requirement
for `geom`. `validate_geom` still checks the following, on the
strength of the constraints page's "never silently invent missing
geospatial attributes" and "explicit data contracts" language, and
because a genuinely malformed geometry means `normalize` did not
actually produce a real, GeoJSON/WKB-compatible representation as the
task requires:

- `None` is valid (source has no geometry).
- If present, must be a dict with `type` and `coordinates`.
- `Point`: exactly two numeric coordinates; longitude in [-180, 180],
  latitude in [-90, 90] (axis order: longitude first, per GeoJSON).
- `LineString`/`Polygon`: accepted structurally (valid type,
  non-empty coordinates) without deep coordinate validation, since no
  current adapter produces them. A production version would add
  per-type validation as new geometry-bearing sources are added.

CRS is assumed to be WGS84 (EPSG:4326) throughout, stated explicitly
here rather than left implicit, per the brief's requirement to treat
CRS as an explicit contract.

### NormalizationError vs. validate: where the line sits

`normalize` raises `NormalizationError` only when it **cannot produce
a value at all** — a coordinate that won't parse as a float, a date
string that won't parse, a genuinely missing `source_id` or
`source_date`. These are translation failures, not judgment calls.

A value that translates successfully but is semantically wrong (an
unrecognized `country_code`) is deliberately allowed through to
`validate_record`, which is where the brief's actual rejection
requirement lives, and where it's already covered by tests. This
keeps normalize's contract narrow ("translate, or fail honestly") and
validate's contract broad ("judge whatever reaches you, regardless of
which adapter produced it").

### Loader: ABC, not Protocol

`Loader` is an abstract base class, matching `SourceAdapter`, for one
reason: consistency. Both are pluggable interfaces in this codebase,
and using the same mechanism for both makes the "this is an interface
a subclass must implement" pattern immediately recognizable throughout
the project, rather than mixing two different typing approaches for
conceptually similar problems.

### Loading: per-record, not batched

`run()` calls `loader.load(record)` once per valid record, immediately,
rather than accumulating valid records and inserting them all at the
end. This is a deliberate crash-safety choice: if the process fails
partway through a run, records already loaded are not lost.

This does not preclude batching for performance. The loader
*interface* accepts one record at a time to keep `run()` simple and
crash-safe; a production loader (e.g. writing to PostgreSQL) could
buffer internally and flush in batches of N for efficiency, entirely
behind the `Loader` interface, without `run()` or any adapter needing
to change.

### RunResult: reports rejections, not accepted records

`RunResult` holds `total_extracted`, `accepted_count`, and a list of
`Rejection(raw_record, reason)`. It does not hold the accepted
`CanonicalRecord`s themselves — those have already been handed to the
loader by the time `run()` returns, so keeping a second copy in memory
would be redundant. Rejections, by contrast, exist nowhere else, so
`RunResult` is their only record.

The field is named `adapter_name`, not `source_id`, to avoid colliding
with `CanonicalRecord.source_id`, which identifies one record within a
source, not the adapter/run itself.

### Test-first discipline

Every validation rule (`country_code` strictness, the normalize/
validate separation, each geometry failure mode) was written test-first:
a failing test defining the expected behavior, then the minimum
implementation to pass it. `tests/test_validation.py` and
`tests/test_geometry.py` cover these in isolation;
`tests/test_csv_adapter.py` proves a second adapter (different field
names: `unique_code`/`nation`/`state_code`/`y`/`x` vs.
`source_id`/`country`/`region`/`lat`/`lon`) runs correctly through the
unmodified core.

## Fixtures

- `fixtures/raw_records.json` — 32 records: 25 valid (covering 13
  countries, both alpha-2 and alpha-3 forms), 7 deliberately invalid
  (missing/invalid/unrecognized country codes, malformed coordinates,
  missing source_id, unparseable date).
- `fixtures/csv_records.csv` — 29 records: 24 valid, 5 invalid, same
  failure categories, proving the core's rules apply identically
  regardless of source format.

## Known simplifications (how this would evolve for production)

- **Staging is JSONL, not PostgreSQL/PostGIS.** The `Loader` interface
  is format-agnostic; a `PostgresLoader` implementing the same
  interface would write to the staging table defined in
  `migrations/001_staging.sql` (see that file for schema details)
  without any change to `run()` or the adapters. No live database was
  used to execute this migration, per the brief's "no external
  production credentials required."
- **No promotion logic.** The brief's objective mentions promotion
  from staging to trusted tables; this submission stops at staging by
  design, since the technical task's four steps end there. Promotion
  would be a separate, later stage reading from staging.
- **LineString/Polygon are not deeply validated**, as detailed above.
- **Mutable fields inside a frozen record** (`attributes`, `geom`) are
  not deep-frozen; a record's top-level fields can't be reassigned,
  but a dict's contents technically still can be mutated in place.
- **No batched database writes.** `run()` loads one record at a time
  for crash-safety and simplicity. A production loader could buffer
  and flush in batches for efficiency without changing `run()` or any
  adapter, since batching is entirely a loader-internal concern.

## Acceptance criteria

1. ✅ Clean run imports well over 20 fixture records (25 of 32 JSON,
   24 of 29 CSV).
2. ✅ A second adapter (`FixtureCsvAdapter`) is implemented only by
   subclassing `SourceAdapter`; no core file was modified to add it
   (verified via `git diff --stat` against non-`adapters/` paths).
3. ✅ Invalid `country_code` is rejected, never defaulted to `DE`.
4. ✅ Geometry field is named `geom` throughout the canonical contract.