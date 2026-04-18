-- Monthly partitions for governance_chain.

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
    pname := 'governance_chain_p' || to_char(cur_month, 'YYYYMM');
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF governance_chain
       FOR VALUES FROM (%L) TO (%L)',
      pname, cur_month, next_month
    );
    cur_month := next_month;
  END LOOP;
END $$;
