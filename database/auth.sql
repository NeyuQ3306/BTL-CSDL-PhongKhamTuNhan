-- Optional login extension. Import after the 11 clinical tables. No default credentials.
-- Prefer: python -m flask --app app init-auth --username admin
-- Flask executes this script statement by statement. Keep semicolons at statement boundaries.
-- Read each staff key separately because older tables inherit the database defaults at import time.
SET @clinic_auth_doctor_type = (
 SELECT CONCAT(COLUMN_TYPE, ' CHARACTER SET ', CHARACTER_SET_NAME, ' COLLATE ', COLLATION_NAME)
 FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'bac_si' AND COLUMN_NAME = 'ma_bac_si'
);
SET @clinic_auth_nurse_type = (
 SELECT CONCAT(COLUMN_TYPE, ' CHARACTER SET ', CHARACTER_SET_NAME, ' COLLATE ', COLLATION_NAME)
 FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'y_ta' AND COLUMN_NAME = 'ma_y_ta'
);

SET @clinic_auth_ddl = CONCAT('CREATE TABLE IF NOT EXISTS app_user (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role VARCHAR(16) NOT NULL,
 doctor_id ', @clinic_auth_doctor_type, ' NULL,
 nurse_id ', @clinic_auth_nurse_type, ' NULL,
 active BOOLEAN NOT NULL DEFAULT TRUE,
 version INT UNSIGNED NOT NULL DEFAULT 1,
 failed_logins INT UNSIGNED NOT NULL DEFAULT 0,
 locked_until DATETIME NULL,
 CONSTRAINT fk_app_user_doctor FOREIGN KEY (doctor_id) REFERENCES bac_si(ma_bac_si),
 CONSTRAINT fk_app_user_nurse FOREIGN KEY (nurse_id) REFERENCES y_ta(ma_y_ta),
 CONSTRAINT ck_app_user_role CHECK (
   (role IN (''admin'',''reception'',''viewer'') AND doctor_id IS NULL AND nurse_id IS NULL) OR
   (role=''doctor'' AND doctor_id IS NOT NULL AND nurse_id IS NULL) OR
   (role=''nurse'' AND nurse_id IS NOT NULL AND doctor_id IS NULL))
) ENGINE=InnoDB');
PREPARE clinic_auth_create FROM @clinic_auth_ddl;
EXECUTE clinic_auth_create;
DEALLOCATE PREPARE clinic_auth_create;
