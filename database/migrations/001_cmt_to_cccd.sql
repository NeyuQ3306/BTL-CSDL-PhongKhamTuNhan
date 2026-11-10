-- MySQL 8.0+/8.4. Select the EXISTING schema, stop the app and back up first.
-- Rename only: values, VARCHAR(20), NOT NULL and UNIQUE are preserved.
-- All three tables are checked before any ALTER. Reruns and interrupted/mixed
-- cmt/cccd states are supported. Both names or neither name aborts the preflight.
-- DDL implicitly commits: this is NOT a transaction across all three tables.
DROP PROCEDURE IF EXISTS clinic_migrate_cmt_to_cccd;
DELIMITER $$
CREATE PROCEDURE clinic_migrate_cmt_to_cccd()
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE target_table VARCHAR(64);
  DECLARE table_count INT;
  DECLARE old_count INT;
  DECLARE new_count INT;
  IF DATABASE() IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Select the target schema first';
  END IF;
  WHILE i <= 3 DO
    SET target_table = ELT(i, 'bac_si', 'y_ta', 'benh_nhan');
    SELECT COUNT(*) INTO table_count FROM information_schema.TABLES
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table AND TABLE_TYPE='BASE TABLE';
    SELECT COUNT(*) INTO old_count FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table AND COLUMN_NAME='cmt';
    SELECT COUNT(*) INTO new_count FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table AND COLUMN_NAME='cccd';
    IF table_count <> 1 OR old_count + new_count <> 1 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Expected exactly one of cmt/cccd in each profile table; no ALTER performed';
    END IF;
    SET i = i + 1;
  END WHILE;
  SET i = 1;
  WHILE i <= 3 DO
    SET target_table = ELT(i, 'bac_si', 'y_ta', 'benh_nhan');
    SELECT COUNT(*) INTO old_count FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table AND COLUMN_NAME='cmt';
    IF old_count = 1 THEN
      SET @clinic_cccd_ddl = CONCAT('ALTER TABLE `', target_table, '` RENAME COLUMN `cmt` TO `cccd`');
      PREPARE clinic_cccd_stmt FROM @clinic_cccd_ddl;
      EXECUTE clinic_cccd_stmt;
      DEALLOCATE PREPARE clinic_cccd_stmt;
    END IF;
    -- Match the automatically named unique index in freshly imported schemas.
    SELECT COUNT(*) INTO old_count FROM information_schema.STATISTICS
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table
        AND INDEX_NAME='cmt' AND COLUMN_NAME='cccd' AND NON_UNIQUE=0;
    SELECT COUNT(*) INTO new_count FROM information_schema.STATISTICS
      WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=target_table AND INDEX_NAME='cccd';
    IF old_count = 1 AND new_count = 0 THEN
      SET @clinic_cccd_ddl = CONCAT('ALTER TABLE `', target_table, '` RENAME INDEX `cmt` TO `cccd`');
      PREPARE clinic_cccd_stmt FROM @clinic_cccd_ddl;
      EXECUTE clinic_cccd_stmt;
      DEALLOCATE PREPARE clinic_cccd_stmt;
    END IF;
    SET i = i + 1;
  END WHILE;
  SET @clinic_cccd_ddl = NULL;
END$$
DELIMITER ;
CALL clinic_migrate_cmt_to_cccd();
DROP PROCEDURE clinic_migrate_cmt_to_cccd;
