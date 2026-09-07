-- ==========================================================
-- CYPHERIS SECURITY PLATFORM - PostgreSQL schema
-- ==========================================================
-- Reset-oriented initialization for local/dev environments.
-- Production should use versioned migrations.
-- ==========================================================

DROP TABLE IF EXISTS sensor_telemetry CASCADE;
DROP TABLE IF EXISTS drift_events CASCADE;
DROP TABLE IF EXISTS security_timeline CASCADE;
DROP TABLE IF EXISTS evidence CASCADE;
DROP TABLE IF EXISTS investigation_events CASCADE;
DROP TABLE IF EXISTS investigations CASCADE;
DROP TABLE IF EXISTS asset_registry CASCADE;
DROP TABLE IF EXISTS identity_events CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS security_integrations CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS sensor_enrollments CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS network_flows CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100), country VARCHAR(100), email VARCHAR(255) NOT NULL,
    phone VARCHAR(30), website VARCHAR(255), logo_url TEXT,
    brand_primary_color VARCHAR(7) NOT NULL DEFAULT '#00E5FF',
    brand_secondary_color VARCHAR(7) NOT NULL DEFAULT '#0A1628',
    subscription_plan VARCHAR(30) NOT NULL DEFAULT 'Free', status VARCHAR(30) NOT NULL DEFAULT 'Trial',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT companies_primary_color_hex CHECK (brand_primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    CONSTRAINT companies_secondary_color_hex CHECK (brand_secondary_color ~ '^#[0-9A-Fa-f]{6}$')
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, phone_number VARCHAR(30),
    password_hash TEXT NOT NULL, role VARCHAR(50) NOT NULL DEFAULT 'Admin', status VARCHAR(20) NOT NULL DEFAULT 'Active',
    last_login TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE network_flows (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_ip INET, destination_ip INET, protocol VARCHAR(20), packets BIGINT NOT NULL DEFAULT 0 CHECK (packets >= 0),
    bytes BIGINT NOT NULL DEFAULT 0 CHECK (bytes >= 0), duration DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (duration >= 0),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO', alert_type VARCHAR(100) NOT NULL, description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Open', created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sensor_enrollments (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    sensor_name VARCHAR(150) NOT NULL, environment_name VARCHAR(150) NOT NULL,
    environment_type VARCHAR(80) NOT NULL DEFAULT 'infrastructure', enrollment_token VARCHAR(128) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING', registered_at TIMESTAMPTZ, last_heartbeat TIMESTAMPTZ,
    last_status_change TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE security_integrations (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    connection_name VARCHAR(255) NOT NULL, environment_name VARCHAR(255) NOT NULL,
    environment_type VARCHAR(100) NOT NULL DEFAULT 'infrastructure', integration_type VARCHAR(50) NOT NULL,
    provider VARCHAR(100), api_platform VARCHAR(100), api_url TEXT, enrollment_token VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', registered_at TIMESTAMPTZ, last_heartbeat TIMESTAMPTZ,
    last_status_change TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    plan VARCHAR(30) NOT NULL DEFAULT 'Free', billing_cycle VARCHAR(20) NOT NULL DEFAULT 'Yearly',
    user_limit INTEGER NOT NULL DEFAULT 1 CHECK (user_limit > 0), current_users INTEGER NOT NULL DEFAULT 1 CHECK (current_users >= 0),
    annual_price NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (annual_price >= 0),
    trial_started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trial_ends_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    paid_started_at TIMESTAMPTZ, renewal_date DATE, payment_provider VARCHAR(30),
    external_customer_id VARCHAR(255), external_subscription_id VARCHAR(255), status VARCHAR(30) NOT NULL DEFAULT 'TRIALING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(200), message TEXT, is_read BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, action VARCHAR(255), ip_address INET,
    metadata JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE asset_registry (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    asset_key VARCHAR(255) NOT NULL, asset_name VARCHAR(255) NOT NULL, asset_type VARCHAR(80) NOT NULL DEFAULT 'unknown',
    environment_name VARCHAR(255), criticality VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', exposure VARCHAR(30) NOT NULL DEFAULT 'INTERNAL',
    owner_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, source VARCHAR(80) NOT NULL DEFAULT 'manual',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb, first_seen TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(company_id, asset_key)
);
CREATE TABLE identity_events (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, identity_key VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL, source VARCHAR(80) NOT NULL DEFAULT 'sensor',
    risk_score INTEGER NOT NULL DEFAULT 0 CHECK (risk_score BETWEEN 0 AND 100), metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE investigations (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL, status VARCHAR(30) NOT NULL DEFAULT 'OPEN', priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    owner_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, source_alert_id INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    summary TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, resolved_at TIMESTAMPTZ
);
CREATE TABLE investigation_events (
    id BIGSERIAL PRIMARY KEY, investigation_id BIGINT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE, event_type VARCHAR(80) NOT NULL,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, message TEXT, metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE evidence (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    investigation_id BIGINT REFERENCES investigations(id) ON DELETE CASCADE, evidence_type VARCHAR(80) NOT NULL,
    source VARCHAR(80) NOT NULL, subject_key VARCHAR(255), payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE security_timeline (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    event_type VARCHAR(80) NOT NULL, severity VARCHAR(20) NOT NULL DEFAULT 'INFO', subject_type VARCHAR(80), subject_key VARCHAR(255),
    message TEXT NOT NULL, source VARCHAR(80) NOT NULL DEFAULT 'platform', metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE drift_events (
    id BIGSERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    subject_type VARCHAR(80) NOT NULL, subject_key VARCHAR(255) NOT NULL, change_type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', before_state JSONB NOT NULL DEFAULT '{}'::jsonb, after_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    source VARCHAR(80) NOT NULL DEFAULT 'sensor', detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sensor_telemetry (
    id BIGSERIAL PRIMARY KEY, sensor_id INTEGER NOT NULL REFERENCES sensor_enrollments(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE, telemetry_type VARCHAR(80) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb, received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_network_flows_company_detected ON network_flows(company_id, detected_at DESC);
CREATE INDEX idx_alerts_company_created ON alerts(company_id, created_at DESC);
CREATE INDEX idx_alerts_company_status ON alerts(company_id, status);
CREATE INDEX idx_sensor_company_updated ON sensor_enrollments(company_id, updated_at DESC);
CREATE INDEX idx_integrations_company_created ON security_integrations(company_id, created_at DESC);
CREATE INDEX idx_integrations_company_status ON security_integrations(company_id, status);
CREATE INDEX idx_notifications_company_created ON notifications(company_id, created_at DESC);
CREATE INDEX idx_audit_logs_company_created ON audit_logs(company_id, created_at DESC);
CREATE INDEX idx_assets_company_seen ON asset_registry(company_id, last_seen DESC);
CREATE INDEX idx_identity_company_observed ON identity_events(company_id, observed_at DESC);
CREATE INDEX idx_investigations_company_updated ON investigations(company_id, updated_at DESC);
CREATE INDEX idx_investigation_events_investigation ON investigation_events(investigation_id, created_at DESC);
CREATE INDEX idx_evidence_company_observed ON evidence(company_id, observed_at DESC);
CREATE INDEX idx_timeline_company_occurred ON security_timeline(company_id, occurred_at DESC);
CREATE INDEX idx_drift_company_detected ON drift_events(company_id, detected_at DESC);
CREATE INDEX idx_sensor_telemetry_received ON sensor_telemetry(company_id, received_at DESC);

CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = CURRENT_TIMESTAMP; RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER sensor_enrollments_updated_at BEFORE UPDATE ON sensor_enrollments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER security_integrations_updated_at BEFORE UPDATE ON security_integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER investigations_updated_at BEFORE UPDATE ON investigations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
