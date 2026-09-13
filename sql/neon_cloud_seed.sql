-- Deterministic, credential-free cloud bootstrap matching dataset seed 20260914.
-- Safe to rerun: canonical rows are upserted.
\ir neon_schema.sql

INSERT INTO benchmark.accounts
SELECT
  'acct_' || lpad(i::text,4,'0'),
  'Northstar Customer ' || lpad(i::text,4,'0'),
  (ARRAY['SMB','Mid-market','Enterprise'])[1 + ((i-1) % 3)],
  (ARRAY['FR','DE','GB','US','ES'])[1 + ((i-1) % 5)],
  'hs_' || (100000+i)::text,
  'cus_bench_' || (100000+i)::text,
  timestamptz '2026-07-01 00:00:00+00' - make_interval(days => 120-i)
FROM generate_series(1,120) i
ON CONFLICT (account_id) DO UPDATE SET
  company_name=EXCLUDED.company_name,
  segment=EXCLUDED.segment,
  country_code=EXCLUDED.country_code,
  crm_company_id=EXCLUDED.crm_company_id,
  billing_customer_id=EXCLUDED.billing_customer_id,
  created_at=EXCLUDED.created_at;

INSERT INTO benchmark.identity_map
SELECT account_id,
       'customer-' || (substring(account_id from 6)::int)::text || '.example',
       crm_company_id,
       billing_customer_id
FROM benchmark.accounts
ON CONFLICT (account_id) DO UPDATE SET
  normalized_domain=EXCLUDED.normalized_domain,
  crm_company_id=EXCLUDED.crm_company_id,
  billing_customer_id=EXCLUDED.billing_customer_id;

INSERT INTO benchmark.product_events
SELECT
  'evt_' || lpad(i::text,4,'0') || '_' || lpad(day_no::text,2,'0') || '_' || lpad(n::text,2,'0'),
  'acct_' || lpad(i::text,4,'0'),
  CASE WHEN n % 3 = 0 THEN 'session_started' ELSE 'feature_used' END,
  CASE WHEN i % 4 = 0 THEN 'bulk_export' ELSE (ARRAY['dashboard','alerts','reports'])[1+(n%3)] END,
  timestamptz '2026-07-01 00:00:00+00' + make_interval(days=>day_no,hours=>((i+n)%24),mins=>((i*n)%60)),
  timestamptz '2026-07-01 00:00:00+00' + make_interval(days=>day_no,hours=>((i+n)%24),mins=>((i*n)%60)+((i+n)%9)),
  jsonb_build_object('user_id','usr_' || lpad(i::text,4,'0') || '_' || lpad((n%6)::text,2,'0'))
FROM generate_series(1,120) i
CROSS JOIN generate_series(0,44) day_no
CROSS JOIN LATERAL generate_series(
  0,
  CASE
    WHEN i % 3 = 1 THEN 2
    WHEN i % 3 = 2 THEN 6
    WHEN day_no >= 35 AND i % 4 = 0 THEN 1
    ELSE 13
  END
) n
ON CONFLICT (event_id) DO UPDATE SET
  account_id=EXCLUDED.account_id,
  event_name=EXCLUDED.event_name,
  feature=EXCLUDED.feature,
  occurred_at=EXCLUDED.occurred_at,
  received_at=EXCLUDED.received_at,
  properties=EXCLUDED.properties;

SELECT count(*) AS accounts FROM benchmark.accounts;
SELECT count(*) AS identity_mappings FROM benchmark.identity_map;
SELECT count(*) AS product_events FROM benchmark.product_events;
