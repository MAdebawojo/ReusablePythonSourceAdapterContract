-- Project IRIS: staging table for ingested source records.
-- Country-scoped: every row must carry a valid, non-null country_code.
-- geom uses PostGIS geometry, WGS84 (SRID 4326), matching the
-- canonical contract's GeoJSON convention (longitude, latitude).
-- Point-only, matching this submission's geometry validation scope.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS staging_records (
    id              BIGSERIAL PRIMARY KEY,
    country_code    CHAR(2)      NOT NULL,
    region_code     TEXT,
    source_id       TEXT         NOT NULL,
    source_date     DATE         NOT NULL,
    fetched_at      TIMESTAMPTZ  NOT NULL,
    attributes      JSONB        NOT NULL DEFAULT '{}'::jsonb,
    geom            GEOMETRY(Point, 4326),
    adapter_name    TEXT         NOT NULL,
    loaded_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT staging_records_country_code_valid
        CHECK (country_code ~ '^[A-Z]{2}$'),

    CONSTRAINT staging_records_unique_source_record
        UNIQUE (adapter_name, country_code, source_id)
);

CREATE INDEX IF NOT EXISTS idx_staging_records_country_code
    ON staging_records (country_code);

CREATE INDEX IF NOT EXISTS idx_staging_records_geom
    ON staging_records USING GIST (geom);

COMMENT ON TABLE staging_records IS
    'Landing table for validated CanonicalRecord rows from any source adapter. Promotion to trusted tables happens from here in a later stage (not implemented in this submission).';