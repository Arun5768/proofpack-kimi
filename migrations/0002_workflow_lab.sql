CREATE TABLE IF NOT EXISTS lab_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  mode TEXT NOT NULL,
  goal TEXT NOT NULL,
  source_text TEXT NOT NULL,
  source_count INTEGER NOT NULL,
  analysis_json TEXT NOT NULL,
  composition_json TEXT NOT NULL,
  validation_json TEXT NOT NULL,
  validation_score INTEGER NOT NULL,
  latency_ms INTEGER NOT NULL,
  model TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lab_runs_user_created ON lab_runs(user_id, created_at DESC);
