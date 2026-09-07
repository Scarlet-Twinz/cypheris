-- ==========================================================
-- CYPHERIS ENTERPRISE SECURITY PLATFORM
-- Database Initialization Script
-- Version: 1.0.0
-- Database: PostgreSQL
-- Powered by PNSTAP™
--
-- DEVELOPMENT RESET SCRIPT
-- WARNING: This drops and recreates application tables.
-- Do NOT run against production data.
-- ==========================================================


-- ==========================================================
-- CLEAN RESET
-- ==========================================================

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS network_flows CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS companies CASCADE;


-- ==========================================================
-- COMPANIES
-- ==========================================================

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,

    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    country VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    website VARCHAR(255),

    subscription_plan VARCHAR(30)
        NOT NULL DEFAULT 'Free',

    status VARCHAR(20)
        NOT NULL DEFAULT 'Active',

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================================
-- USERS
-- ==========================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL,

    full_name VARCHAR(150) NOT NULL,

    email VARCHAR(255)
        NOT NULL UNIQUE,

    phone_number VARCHAR(30),

    password_hash TEXT NOT NULL,

    role VARCHAR(50)
        NOT NULL DEFAULT 'Admin',

    status VARCHAR(20)
        NOT NULL DEFAULT 'Active',

    last_login TIMESTAMP,

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);


-- ==========================================================
-- NETWORK FLOWS
-- ==========================================================

CREATE TABLE network_flows (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL,

    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),

    protocol VARCHAR(20),

    packets BIGINT
        NOT NULL DEFAULT 0,

    bytes BIGINT
        NOT NULL DEFAULT 0,

    duration DOUBLE PRECISION
        NOT NULL DEFAULT 0,

    detected_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_network_flows_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);


-- ==========================================================
-- ALERTS
-- ==========================================================

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL,

    severity VARCHAR(20),
    alert_type VARCHAR(100),
    description TEXT,

    status VARCHAR(20)
        NOT NULL DEFAULT 'Open',

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alerts_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);


-- ==========================================================
-- SUBSCRIPTIONS
-- ==========================================================

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL UNIQUE,

    plan VARCHAR(30)
        NOT NULL DEFAULT 'Free',

    billing_cycle VARCHAR(20)
        NOT NULL DEFAULT 'Yearly',

    user_limit INTEGER
        NOT NULL DEFAULT 1
        CHECK (user_limit > 0),

    current_users INTEGER
        NOT NULL DEFAULT 1
        CHECK (current_users >= 0),

    annual_price NUMERIC(10,2)
        NOT NULL DEFAULT 0.00
        CHECK (annual_price >= 0),

    renewal_date DATE,

    status VARCHAR(20)
        NOT NULL DEFAULT 'Active',

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_subscriptions_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);


-- ==========================================================
-- NOTIFICATIONS
-- ==========================================================

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL,

    title VARCHAR(200),
    message TEXT,

    is_read BOOLEAN
        NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notifications_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);


-- ==========================================================
-- AUDIT LOGS
-- ==========================================================

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,

    company_id INTEGER NOT NULL,

    user_id INTEGER,

    action VARCHAR(255),

    ip_address VARCHAR(45),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_logs_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);


-- ==========================================================
-- INDEXES
-- ==========================================================

-- Users
CREATE INDEX idx_users_company_id
    ON users(company_id);

CREATE INDEX idx_users_email
    ON users(email);


-- Network flows
CREATE INDEX idx_network_flows_company_id
    ON network_flows(company_id);

CREATE INDEX idx_network_flows_detected_at
    ON network_flows(detected_at);


-- Alerts
CREATE INDEX idx_alerts_company_id
    ON alerts(company_id);

CREATE INDEX idx_alerts_created_at
    ON alerts(created_at);

CREATE INDEX idx_alerts_status
    ON alerts(status);


-- Notifications
CREATE INDEX idx_notifications_company_id
    ON notifications(company_id);

CREATE INDEX idx_notifications_created_at
    ON notifications(created_at);


-- Audit logs
CREATE INDEX idx_audit_logs_company_id
    ON audit_logs(company_id);

CREATE INDEX idx_audit_logs_user_id
    ON audit_logs(user_id);

CREATE INDEX idx_audit_logs_created_at
    ON audit_logs(created_at);


-- ==========================================================
-- UPDATED_AT TRIGGER
-- ==========================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER companies_updated_at
BEFORE UPDATE ON companies
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER subscriptions_updated_at
BEFORE UPDATE ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ==========================================================
-- END OF CYPHERIS DATABASE SCHEMA
-- ==========================================================