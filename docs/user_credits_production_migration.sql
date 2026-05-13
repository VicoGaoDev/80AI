-- Production migration: move remaining credits from users.credits
-- into the new user_credits table.
--
-- Recommended execution steps:
-- 1. Back up the production database first.
-- 2. Stop backend application instances before running.
-- 3. Connect to the target database, then execute this file.
--
-- Example:
--   mysql -h <host> -P <port> -u <user> -p <database> < user_credits_production_migration.sql

SELECT DATABASE() AS current_database;

SELECT
  TABLE_NAME,
  COLUMN_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'credits';

SHOW TABLES LIKE 'user_credits';

CREATE TABLE IF NOT EXISTS user_credits (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  type INT NOT NULL DEFAULT 0,
  balance INT NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_credits_user_id_type (user_id, type),
  KEY ix_user_credits_user_id (user_id),
  KEY ix_user_credits_type (type),
  CONSTRAINT fk_user_credits_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET @has_legacy_credits := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'users'
    AND COLUMN_NAME = 'credits'
);

SET @backfill_sql := IF(
  @has_legacy_credits > 0,
  '
  INSERT INTO user_credits (user_id, type, balance, created_at, updated_at)
  SELECT u.id, 0, COALESCE(u.credits, 0), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
  FROM users u
  LEFT JOIN user_credits uc
    ON uc.user_id = u.id
   AND uc.type = 0
  WHERE uc.id IS NULL
  ',
  '
  INSERT INTO user_credits (user_id, type, balance, created_at, updated_at)
  SELECT u.id, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
  FROM users u
  LEFT JOIN user_credits uc
    ON uc.user_id = u.id
   AND uc.type = 0
  WHERE uc.id IS NULL
  '
);

PREPARE stmt_backfill FROM @backfill_sql;
EXECUTE stmt_backfill;
DEALLOCATE PREPARE stmt_backfill;

SET @drop_legacy_sql := IF(
  @has_legacy_credits > 0,
  'ALTER TABLE users DROP COLUMN credits',
  'SELECT ''users.credits already removed'' AS info'
);

PREPARE stmt_drop_legacy FROM @drop_legacy_sql;
EXECUTE stmt_drop_legacy;
DEALLOCATE PREPARE stmt_drop_legacy;

SELECT COUNT(*) AS user_count FROM users;

SELECT COUNT(*) AS credit_account_count
FROM user_credits
WHERE type = 0;

SELECT
  u.id,
  u.username,
  uc.type,
  uc.balance
FROM users u
LEFT JOIN user_credits uc
  ON uc.user_id = u.id
 AND uc.type = 0
ORDER BY u.id ASC
LIMIT 20;

SELECT
  u.id,
  u.username,
  COUNT(*) AS account_count
FROM user_credits uc
JOIN users u ON u.id = uc.user_id
WHERE uc.type = 0
GROUP BY u.id, u.username
HAVING COUNT(*) > 1;
