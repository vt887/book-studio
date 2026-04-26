CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS concepts (
    concept_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    name TEXT NOT NULL,
    definition TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    embedding VECTOR(384) NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    applicable_roles JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_concepts_book_id ON concepts (book_id);
CREATE INDEX IF NOT EXISTS idx_concepts_embedding_cosine
ON concepts USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_concepts_roles_gin
ON concepts USING gin (applicable_roles jsonb_path_ops);

CREATE INDEX IF NOT EXISTS idx_concepts_tags_gin
ON concepts USING gin (tags jsonb_path_ops);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_concepts_updated_at ON concepts;
CREATE TRIGGER trg_concepts_updated_at
BEFORE UPDATE ON concepts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
