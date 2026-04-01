CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT,
    document_type TEXT,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    trust_score DOUBLE PRECISION,
    checksum TEXT,
    parser_used TEXT,
    parser_confidence DOUBLE PRECISION,
    original_size_bytes BIGINT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    indexed_at TIMESTAMPTZ,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    embedding_model TEXT,
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    last_verified_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    document_title TEXT,
    document_type TEXT,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    trust_score DOUBLE PRECISION,
    section_title TEXT,
    section_hierarchy JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_numbers JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    embedding_model TEXT,
    child_chunk_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    sequence_number INTEGER NOT NULL DEFAULT 0,
    parent_chunk_id TEXT,
    start_char INTEGER,
    end_char INTEGER,
    start_page INTEGER,
    end_page INTEGER,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', COALESCE(content, ''))
    ) STORED
);

CREATE TABLE IF NOT EXISTS chunk_vectors (
    chunk_id TEXT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_documents_ingested_at ON documents (ingested_at DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_sequence_number ON chunks (document_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_chunks_search_vector ON chunks USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_chunk_vectors_embedding_cosine
    ON chunk_vectors
    USING hnsw (embedding vector_cosine_ops);

CREATE VIEW IF NOT EXISTS documents_view AS
SELECT
    d.id AS document_id,
    d.title AS document_title,
    d.document_type,
    d.tags,
    d.trust_score,
    d.ingested_at AS created_at,
    COUNT(c.id) AS chunk_count
FROM documents d
LEFT JOIN chunks c ON c.document_id = d.id
GROUP BY d.id, d.title, d.document_type, d.tags, d.trust_score, d.ingested_at;
