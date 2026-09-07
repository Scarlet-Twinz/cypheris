-- ==========================================================
-- CYPHERIS SECURITY PLATFORM - PostgreSQL schema
-- ==========================================================
-- Reset-oriented initialization for local/dev environments.
-- Never run this script against a database containing data you
-- need to preserve. Production should use versioned migrations.
-- ==========================================================

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
    industry VARCHAR(100),
    country VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    website VARCHAR(255),
    logo_url TEXT,
    brand_primary_color VARCHAR(7) NOT NULL DEFAULT '#00E5FF',
    brand_secondary_color VARCHAR(7) NOT NULL DEFAULT '#0A1628',
    subscription_plan VARCHAR(30) NOT NULL DEFAULT 'Free',
    status VARCHAR(30) NOT NULL DEFAULT 'Trial',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT companies_primary_color_hex CHECK (brand_primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    CONSTRAINT companies_secondary_color_hex CHECK (brand_secondary_color ~ '^#[0-9A-Fa-f]{6}$')
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(30),
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Admin',
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE network_flows (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_ip INET,
    destination_ip INET,
    protocol VARCHAR(20),
    packets BIGINT NOT NULL DEFAULT 0 CHECK (packets >= 0),
    bytes BIGINT NOT NULL DEFAULT 0 CHECK (bytes >= 0),
    duration DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (duration >= 0),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
    alert_type VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensor_enrollments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    sensor_name VARCHAR(150) NOT NULL,
    environment_name VARCHAR(150) NOT NULL,
    environment_type VARCHAR(80) NOT NULL DEFAULT 'infrastructure',
    enrollment_token VARCHAR(128) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    registered_at TIMESTAMPTZ,
    last_heartbeat TIMESTAMPTZ,
    last_status_change TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE security_integrations (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    connection_name VARCHAR(255) NOT NULL,
    environment_name VARCHAR(255) NOT NULL,
    environment_type VARCHAR(100) NOT NULL DEFAULT 'infrastructure',
    integration_type VARCHAR(50) NOT NULL,
    provider VARCHAR(100),
    api_platform VARCHAR(100),
    api_url TEXT,
    enrollment_token VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    registered_at TIMESTAMPTZ,
    last_heartbeat TIMESTAMPTZ,
    last_status_change TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    plan VARCHAR(30) NOT NULL DEFAULT 'Free',
    billing_cycle VARCHAR(20) NOT NULL DEFAULT 'Yearly',
    user_limit INTEGER NOT NULL DEFAULT 1 CHECK (user_limit > 0),
    current_users INTEGER NOT NULL DEFAULT 1 CHECK (current_users >= 0),
    annual_price NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (annual_price >= 0),
    trial_started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trial_ends_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    paid_started_at TIMESTAMPTZ,
    renewal_date DATE,
    payment_provider VARCHAR(30),
    external_customer_id VARCHAR(255),
    external_subscription_id VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'TRIALING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(200),
    message TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255),
    ip_address INET,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
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

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER sensor_enrollments_updated_at BEFORE UPDATE ON sensor_enrollments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER security_integrations_updated_at BEFORE UPDATE ON security_integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
