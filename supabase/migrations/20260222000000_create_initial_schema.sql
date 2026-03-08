-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS — Core user identity and auth
-- ============================================================
CREATE TABLE users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name      VARCHAR     NOT NULL,
    last_name       VARCHAR     NOT NULL,
    email           VARCHAR     UNIQUE NOT NULL,
    password_hash   TEXT        NOT NULL,
    role            VARCHAR     NOT NULL,
    status          VARCHAR     NOT NULL DEFAULT 'active',
    email_verified  BOOLEAN     NOT NULL DEFAULT false,
    last_login_at   TIMESTAMP,
    created_at      TIMESTAMP   NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT now()
);

-- ============================================================
-- 2. PROFILES — Platform profiles (linkedin, upwork, indeed)
-- ============================================================
CREATE TABLE profiles (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name  VARCHAR     NOT NULL,
    last_name   VARCHAR     NOT NULL,
    type        VARCHAR     NOT NULL CHECK (type IN ('linkedin', 'upwork', 'indeed')),
    email       VARCHAR     NOT NULL,
    link        TEXT,
    country     VARCHAR,
    status      VARCHAR     NOT NULL DEFAULT 'active',
    created_at  TIMESTAMP   NOT NULL DEFAULT now()
);

-- ============================================================
-- 3. DOCUMENTS — Resumes and cover letters per profile
-- ============================================================
CREATE TABLE documents (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id  UUID        NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    type        VARCHAR     NOT NULL CHECK (type IN ('resume', 'cover_letter')),
    title       VARCHAR     NOT NULL,
    file_url    TEXT        NOT NULL,
    status      VARCHAR     NOT NULL DEFAULT 'active',
    created_at  TIMESTAMP   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMP   NOT NULL DEFAULT now()
);

-- ============================================================
-- 4. BD_PROFILE_ASSIGNMENTS — Many-to-many: users <-> profiles
-- ============================================================
CREATE TABLE bd_profile_assignments (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_id      UUID        NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    assigned_by     UUID        NOT NULL REFERENCES users(id),
    assigned_at     TIMESTAMP   NOT NULL DEFAULT now(),
    unassigned_at   TIMESTAMP,
    status          VARCHAR     NOT NULL DEFAULT 'active'
);

-- ============================================================
-- 5. APPLICATIONS — Job applications
-- ============================================================
CREATE TABLE applications (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id          UUID        NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id           UUID        REFERENCES documents(id),
    cover_letter_id     UUID        REFERENCES documents(id),
    bidder_id           UUID        NOT NULL REFERENCES users(id),
    assignee_id         UUID        REFERENCES users(id),
    company_name        VARCHAR     NOT NULL,
    job_title           VARCHAR     NOT NULL,
    job_url             TEXT,
    location            VARCHAR,
    job_type            VARCHAR,
    priority            VARCHAR,
    is_global           BOOLEAN     NOT NULL DEFAULT false,
    current_stage       VARCHAR     NOT NULL DEFAULT 'applied',
    interview_date      TIMESTAMP,
    has_assessment      BOOLEAN     NOT NULL DEFAULT false,
    assessment_status   VARCHAR,
    applied_date        TIMESTAMP   NOT NULL DEFAULT now(),
    created_at          TIMESTAMP   NOT NULL DEFAULT now(),
    notes               TEXT
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_users_email                        ON users(email);
CREATE INDEX idx_users_role                         ON users(role);

CREATE INDEX idx_profiles_type                      ON profiles(type);

CREATE INDEX idx_documents_profile_id               ON documents(profile_id);
CREATE INDEX idx_documents_type                     ON documents(type);

CREATE INDEX idx_bd_profile_assignments_user_id     ON bd_profile_assignments(user_id);
CREATE INDEX idx_bd_profile_assignments_profile_id  ON bd_profile_assignments(profile_id);

CREATE INDEX idx_applications_profile_id            ON applications(profile_id);
CREATE INDEX idx_applications_bidder_id             ON applications(bidder_id);
CREATE INDEX idx_applications_assignee_id           ON applications(assignee_id);
CREATE INDEX idx_applications_current_stage         ON applications(current_stage);
