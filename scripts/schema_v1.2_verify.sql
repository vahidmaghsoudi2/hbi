SELECT 'SCHEMA_VERSION' AS check_name, user_version AS value FROM pragma_user_version;
SELECT 'POST_RECORD_COUNT' AS check_name, COUNT(*) AS value FROM Evidence;
SELECT name AS column_name FROM pragma_table_info('Evidence') WHERE name IN ('claim_id','field','market_region','notes','qa_status','evidence_strength','evidence_date') ORDER BY cid;
SELECT 'DUPLICATE_CLAIM_IDS' AS check_name, COUNT(*) AS value FROM (SELECT claim_id FROM Evidence WHERE claim_id IS NOT NULL GROUP BY claim_id HAVING COUNT(*) > 1);
PRAGMA foreign_key_check(Evidence);
