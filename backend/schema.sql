CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);

CREATE TABLE IF NOT EXISTS auth_challenges (
    nonce TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    message TEXT NOT NULL,
    issued_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    consumed_at INTEGER
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    csrf_token TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    uploader TEXT NOT NULL,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL,
    media_type TEXT NOT NULL,
    size INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS contents (
    content_hash TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    creator TEXT NOT NULL,
    chain_id INTEGER NOT NULL,
    target_contract TEXT NOT NULL,
    canonical_json TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS content_files (
    content_hash TEXT PRIMARY KEY REFERENCES contents(content_hash),
    file_id TEXT NOT NULL REFERENCES files(id)
);

CREATE TABLE IF NOT EXISTS verified_transactions (
    chain_id INTEGER NOT NULL,
    tx_hash TEXT NOT NULL,
    sender TEXT NOT NULL,
    target TEXT NOT NULL,
    method TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    status TEXT NOT NULL,
    value_wei TEXT NOT NULL,
    gas_used TEXT,
    block_number TEXT,
    block_hash TEXT,
    content_hash TEXT REFERENCES contents(content_hash),
    verified_at INTEGER NOT NULL,
    PRIMARY KEY (chain_id, tx_hash)
);

CREATE INDEX IF NOT EXISTS idx_files_uploader ON files(uploader);
CREATE INDEX IF NOT EXISTS idx_contents_creator_kind ON contents(creator, kind);
CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_transactions_sender_time ON verified_transactions(sender, verified_at, tx_hash);
