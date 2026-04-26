CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS concepts (
    concept_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    name TEXT NOT NULL,
    definition TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    importance_score DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    source_chunks JSONB NOT NULL DEFAULT '[]'::jsonb,
    embedding VECTOR(384) NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    applicable_roles JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    text_content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_chunks_book_hash ON chunks (book_id, text_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_book_id ON chunks (book_id);

CREATE INDEX IF NOT EXISTS idx_concepts_book_id ON concepts (book_id);
CREATE INDEX IF NOT EXISTS idx_concepts_embedding_cosine
ON concepts USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_concepts_roles_gin
ON concepts USING gin (applicable_roles jsonb_path_ops);

CREATE INDEX IF NOT EXISTS idx_concepts_tags_gin
ON concepts USING gin (tags jsonb_path_ops);

CREATE INDEX IF NOT EXISTS idx_concepts_source_chunks_gin
ON concepts USING gin (source_chunks jsonb_path_ops);

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

DROP TRIGGER IF EXISTS trg_chunks_updated_at ON chunks;
CREATE TRIGGER trg_chunks_updated_at
BEFORE UPDATE ON chunks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
