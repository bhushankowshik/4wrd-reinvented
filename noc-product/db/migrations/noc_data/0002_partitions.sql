-- Pre-create monthly partitions for partitioned tables.
-- Covers current month ± 6 months (poor-man's partman for dev).
-- In production E8 uses pg_partman with daily run_maintenance_proc().

DO $$
DECLARE
  start_month DATE := date_trunc('month', now())::date - INTERVAL '6 months';
  end_month   DATE := date_trunc('month', now())::date + INTERVAL '12 months';
  cur_month   DATE;
  next_month  DATE;
  pname       TEXT;
BEGIN
  cur_month := start_month;
  WHILE cur_month < end_month LOOP
    next_month := (cur_month + INTERVAL '1 month')::date;

    pname := 'incident_p' || to_char(cur_month, 'YYYYMM');
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF incident
       FOR VALUES FROM (%L) TO (%L)',
      pname, cur_month, next_month
    );

    pname := 'agent_output_p' || to_char(cur_month, 'YYYYMM');
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF agent_output
       FOR VALUES FROM (%L) TO (%L)',
      pname, cur_month, next_month
    );

    pname := 'recommendation_p' || to_char(cur_month, 'YYYYMM');
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF recommendation
       FOR VALUES FROM (%L) TO (%L)',
      pname, cur_month, next_month
    );

    pname := 'operator_decision_p' || to_char(cur_month, 'YYYYMM');
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF operator_decision
       FOR VALUES FROM (%L) TO (%L)',
      pname, cur_month, next_month
    );

    cur_month := next_month;
  END LOOP;
END $$;
