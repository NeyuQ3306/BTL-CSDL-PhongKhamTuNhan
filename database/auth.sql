-- Optional login extension; import after the 11 clinical tables. No default credentials.
-- Prefer: python -m flask --app app init-auth --username admin
CREATE TABLE IF NOT EXISTS app_user (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role VARCHAR(16) NOT NULL,
 doctor_id VARCHAR(12) NULL,
 nurse_id VARCHAR(12) NULL,
 active BOOLEAN NOT NULL DEFAULT TRUE,
 version INT UNSIGNED NOT NULL DEFAULT 1,
 failed_logins INT UNSIGNED NOT NULL DEFAULT 0,
 locked_until DATETIME NULL,
 CONSTRAINT fk_app_user_doctor FOREIGN KEY (doctor_id) REFERENCES bac_si(ma_bac_si),
 CONSTRAINT fk_app_user_nurse FOREIGN KEY (nurse_id) REFERENCES y_ta(ma_y_ta),
 CONSTRAINT ck_app_user_role CHECK (
   (role IN ('admin','reception') AND doctor_id IS NULL AND nurse_id IS NULL) OR
   (role='doctor' AND doctor_id IS NOT NULL AND nurse_id IS NULL) OR
   (role='nurse' AND nurse_id IS NOT NULL AND doctor_id IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
