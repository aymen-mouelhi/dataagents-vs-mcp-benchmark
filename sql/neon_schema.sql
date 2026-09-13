CREATE SCHEMA IF NOT EXISTS benchmark;

CREATE TABLE IF NOT EXISTS benchmark.accounts (
  account_id text PRIMARY KEY,
  company_name text NOT NULL,
  segment text NOT NULL CHECK (segment IN ('SMB', 'Mid-market', 'Enterprise')),
  country_code text NOT NULL,
  crm_company_id text NOT NULL UNIQUE,
  billing_customer_id text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS benchmark.product_events (
  event_id text PRIMARY KEY,
  account_id text NOT NULL REFERENCES benchmark.accounts(account_id),
  event_name text NOT NULL,
  feature text NOT NULL,
  occurred_at timestamptz NOT NULL,
  received_at timestamptz NOT NULL,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS benchmark.identity_map (
  account_id text PRIMARY KEY REFERENCES benchmark.accounts(account_id),
  normalized_domain text NOT NULL UNIQUE,
  crm_company_id text NOT NULL,
  billing_customer_id text NOT NULL
);

CREATE INDEX IF NOT EXISTS product_events_account_occurred_idx
  ON benchmark.product_events (account_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS product_events_name_occurred_idx
  ON benchmark.product_events (event_name, occurred_at DESC);

CREATE OR REPLACE VIEW benchmark.daily_account_usage AS
SELECT
  account_id,
  date_trunc('day', occurred_at)::date AS usage_date,
  count(*) AS event_count,
  count(*) FILTER (WHERE event_name = 'session_started') AS sessions,
  count(DISTINCT properties->>'user_id') AS active_users
FROM benchmark.product_events
GROUP BY 1, 2;
