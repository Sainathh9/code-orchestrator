-- =============================================================================
-- orchestrator_db — Bootstrap schema
-- Runs on first "docker compose up" when the postgres volume is empty.
-- =============================================================================

-- ── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID            PRIMARY KEY,
    google_id       VARCHAR(255)    UNIQUE,
    name            VARCHAR(255)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255),
    profile_picture TEXT,
    created_at      TIMESTAMPTZ     DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_email     ON users (email);

-- ── Executions ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS executions (
    id                UUID            PRIMARY KEY,
    user_id           UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    requirement       TEXT            NOT NULL,
    status            VARCHAR(20)     NOT NULL
                      CHECK (status IN ('queued','running','success','failed','cancelled')),
    current_step      VARCHAR(100),
    tries_used        INTEGER         DEFAULT 0,
    execution_time_ms BIGINT,
    workspace_path    TEXT,
    started_at        TIMESTAMPTZ,
    finished_at       TIMESTAMPTZ,
    created_at        TIMESTAMPTZ     DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_execution_user    ON executions (user_id);
CREATE INDEX IF NOT EXISTS idx_execution_status  ON executions (status);
CREATE INDEX IF NOT EXISTS idx_execution_created ON executions (created_at DESC);

-- ── Execution Iterations ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS execution_iterations (
    id               UUID        PRIMARY KEY,
    execution_id     UUID        NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    iteration_number INTEGER     NOT NULL,
    generated_code   TEXT,
    generated_tests  TEXT,
    test_output      TEXT,
    debugger_output  TEXT,
    error_type       VARCHAR(100),
    passed           BOOLEAN     DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_iteration_execution ON execution_iterations (execution_id);

-- ── Execution Logs ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS execution_logs (
    id           UUID        PRIMARY KEY,
    execution_id UUID        NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    level        VARCHAR(20) CHECK (level IN ('INFO','WARNING','ERROR','DEBUG')),
    message      TEXT        NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_log_execution ON execution_logs (execution_id);

-- ── Jobs ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id           UUID         PRIMARY KEY,
    execution_id UUID         NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    rq_job_id    VARCHAR(255) UNIQUE,
    status       VARCHAR(20)  CHECK (status IN ('queued','running','finished','failed')),
    queued_at    TIMESTAMPTZ,
    started_at   TIMESTAMPTZ,
    finished_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_job_execution ON jobs (execution_id);
CREATE INDEX IF NOT EXISTS idx_job_status    ON jobs (status);
