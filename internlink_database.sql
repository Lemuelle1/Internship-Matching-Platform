
CREATE DATABASE IF NOT EXISTS internlink;
USE internlink;

-- ============================================================
-- TABLE 1: users
-- Stores login credentials for both students and admins.
-- The 'role' column separates the two.
-- ============================================================
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR ( 255 ) NOT NULL,          -- store hashed password (e.g. BCrypt)
    role          ENUM('STUDENT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: student_profiles
-- One-to-one with users (only STUDENT role users have a profile).
-- Stores personal and academic details shown on the student dashboard.
-- ============================================================
CREATE TABLE student_profiles (
    profile_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    phone_number    VARCHAR(20),
    date_of_birth   DATE,
    gender          ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY'),
    nationality     VARCHAR(100),
    institution     VARCHAR(200),                 -- university/college name
    course          VARCHAR(200),                 -- e.g. BSc Computer Science
    year_of_study   TINYINT,                      -- e.g. 1, 2, 3, 4
    gpa             DECIMAL(3,2),                 -- e.g. 3.75
    bio             TEXT,
    profile_picture VARCHAR(255),                 -- file path or URL
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_profile_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 3: cv_documents
-- A student can upload multiple CVs but only one is active.
-- Spring Boot saves the file and stores the path here.
-- ============================================================
CREATE TABLE cv_documents (
    cv_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    file_name   VARCHAR(255) NOT NULL,            -- original file name
    file_path   VARCHAR(500) NOT NULL,            -- server storage path
    file_size   INT,                              -- size in bytes
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,    -- the currently active CV
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cv_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 4: opportunities
-- Stores both internships and scholarships.
-- The 'type' column tells them apart.
-- ============================================================
CREATE TABLE opportunities (
    opportunity_id  INT AUTO_INCREMENT PRIMARY KEY,
    posted_by       INT NOT NULL,                 -- admin user_id
    type            ENUM('INTERNSHIP', 'SCHOLARSHIP') NOT NULL,
    title           VARCHAR(255) NOT NULL,
    organization    VARCHAR(200) NOT NULL,         -- company or fund name
    location        VARCHAR(200),                 -- city/country or 'Remote'
    description     TEXT NOT NULL,
    requirements    TEXT,                         -- eligibility / qualifications
    benefits        TEXT,                         -- stipend, allowances, etc.
    application_url VARCHAR(500),                 -- external link (optional)
    deadline        DATE NOT NULL,
    slots_available INT,                          -- NULL = unlimited
    status          ENUM('OPEN', 'CLOSED', 'DRAFT') NOT NULL DEFAULT 'OPEN',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_opportunity_admin FOREIGN KEY (posted_by)
        REFERENCES users(user_id) ON DELETE RESTRICT
);

-- ============================================================
-- TABLE 5: applications
-- Tracks every student application for an opportunity.
-- One student cannot apply for the same opportunity twice.
-- ============================================================
CREATE TABLE applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,                 -- student
    opportunity_id  INT NOT NULL,
    cv_id           INT NOT NULL,                 -- which CV was used
    cover_letter    TEXT,                         -- optional message to admin
    status          ENUM('PENDING', 'REVIEWED', 'SHORTLISTED', 'ACCEPTED', 'REJECTED')
                    NOT NULL DEFAULT 'PENDING',
    admin_notes     TEXT,                         -- internal notes by admin
    applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- prevent duplicate applications
    CONSTRAINT uq_application UNIQUE (user_id, opportunity_id),

    CONSTRAINT fk_application_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE,

    CONSTRAINT fk_application_opportunity FOREIGN KEY (opportunity_id)
        REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,

    CONSTRAINT fk_application_cv FOREIGN KEY (cv_id)
        REFERENCES cv_documents(cv_id) ON DELETE RESTRICT
);

-- ============================================================
-- TABLE 6: notifications  (bonus – useful for your app)
-- Lets the backend push status updates to students.
-- ============================================================
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    message         VARCHAR(500) NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES  (speed up the most common queries)
-- ============================================================
CREATE INDEX idx_opportunities_type     ON opportunities(type);
CREATE INDEX idx_opportunities_status   ON opportunities(status);
CREATE INDEX idx_opportunities_deadline ON opportunities(deadline);
CREATE INDEX idx_applications_user      ON applications(user_id);
CREATE INDEX idx_applications_status    ON applications(status);
CREATE INDEX idx_cv_user_active         ON cv_documents(user_id, is_active);

-- ============================================================
-- SEED DATA – default admin account
-- Password shown here is a placeholder; hash it with BCrypt in Spring Boot.
-- ============================================================
INSERT INTO users (email, password_hash, role)
VALUES ('admin@internlink.com', '$2a$10$PLACEHOLDER_HASH', 'ADMIN');
