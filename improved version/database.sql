-- =========================================================
-- AI Degree Guidance Platform
--  PostgreSQL Database Schema
-- =========================================================

-- Optional: run this only if you want to reset everything
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- =========================================================
-- 1. ROLE
-- =========================================================

CREATE TABLE role (
    role_id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- =========================================================
-- 2. USER
-- Table name changed to app_user because USER can be reserved
-- =========================================================

CREATE TABLE app_user (
    user_id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,

    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id)
        REFERENCES role(role_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================================================
-- 3. A_LEVEL_STREAM
-- =========================================================

CREATE TABLE a_level_stream (
    stream_id BIGSERIAL PRIMARY KEY,
    stream_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- =========================================================
-- 4. SUBJECT
-- =========================================================

CREATE TABLE subject (
    subject_id BIGSERIAL PRIMARY KEY,
    subject_name VARCHAR(150) NOT NULL UNIQUE,
    subject_code VARCHAR(50) UNIQUE
);

-- =========================================================
-- 5. STREAM_SUBJECT
-- Associative entity: A_Level_Stream M:N Subject
-- =========================================================

CREATE TABLE stream_subject (
    stream_subject_id BIGSERIAL PRIMARY KEY,
    stream_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    is_optional BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_stream_subject_stream
        FOREIGN KEY (stream_id)
        REFERENCES a_level_stream(stream_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_stream_subject_subject
        FOREIGN KEY (subject_id)
        REFERENCES subject(subject_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_stream_subject
        UNIQUE (stream_id, subject_id)
);

-- =========================================================
-- 6. DISTRICT
-- =========================================================

CREATE TABLE district (
    district_id BIGSERIAL PRIMARY KEY,
    district_name VARCHAR(100) NOT NULL UNIQUE,
    province VARCHAR(100)
);

-- =========================================================
-- 7. FIELD_OF_INTEREST
-- =========================================================

CREATE TABLE field_of_interest (
    field_id BIGSERIAL PRIMARY KEY,
    field_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT
);

-- =========================================================
-- 8. UNIVERSITY
-- =========================================================

CREATE TABLE university (
    university_id BIGSERIAL PRIMARY KEY,
    university_name VARCHAR(255) NOT NULL UNIQUE,
    short_code VARCHAR(50) UNIQUE,
    location VARCHAR(255),
    province VARCHAR(100),
    website TEXT,
    description TEXT
);

-- =========================================================
-- 9. UNIVERSITY_IMAGE
-- For storing multiple university images
-- =========================================================

CREATE TABLE university_image (
    image_id BIGSERIAL PRIMARY KEY,
    university_id BIGINT NOT NULL,
    image_url TEXT NOT NULL,
    caption TEXT,

    CONSTRAINT fk_university_image_university
        FOREIGN KEY (university_id)
        REFERENCES university(university_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- =========================================================
-- 10. DEGREE_PROGRAM
-- =========================================================

CREATE TABLE degree_program (
    program_id BIGSERIAL PRIMARY KEY,
    university_id BIGINT NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    degree_level VARCHAR(100),
    duration_years NUMERIC(3,1),
    medium VARCHAR(100),
    aptitude_required BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    syllabus_overview TEXT,
    special_notes TEXT,
    ugc_link TEXT,
    university_link TEXT,

    CONSTRAINT fk_degree_program_university
        FOREIGN KEY (university_id)
        REFERENCES university(university_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_degree_program_university
        UNIQUE (university_id, program_name)
);

-- =========================================================
-- 11. PROGRAM_STREAM
-- Associative entity: Degree_Program M:N A_Level_Stream
-- =========================================================

CREATE TABLE program_stream (
    program_stream_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    stream_id BIGINT NOT NULL,
    eligibility_note TEXT,

    CONSTRAINT fk_program_stream_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_program_stream_stream
        FOREIGN KEY (stream_id)
        REFERENCES a_level_stream(stream_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_program_stream
        UNIQUE (program_id, stream_id)
);

-- =========================================================
-- 12. PROGRAM_SUBJECT_REQUIREMENT
-- Associative entity: Degree_Program M:N Subject
-- =========================================================

CREATE TABLE program_subject_requirement (
    requirement_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    requirement_type VARCHAR(50) NOT NULL,
    min_grade VARCHAR(10),
    note TEXT,

    CONSTRAINT fk_program_subject_requirement_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_program_subject_requirement_subject
        FOREIGN KEY (subject_id)
        REFERENCES subject(subject_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_requirement_type
        CHECK (requirement_type IN ('Mandatory', 'Optional', 'Recommended')),

    CONSTRAINT uq_program_subject_requirement
        UNIQUE (program_id, subject_id, requirement_type)
);

-- =========================================================
-- 13. PROGRAM_FIELD
-- Associative entity: Degree_Program M:N Field_Of_Interest
-- =========================================================

CREATE TABLE program_field (
    program_field_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    field_id BIGINT NOT NULL,
    relevance_weight NUMERIC(5,2) DEFAULT 100.00,

    CONSTRAINT fk_program_field_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_program_field_field
        FOREIGN KEY (field_id)
        REFERENCES field_of_interest(field_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_relevance_weight
        CHECK (relevance_weight >= 0 AND relevance_weight <= 100),

    CONSTRAINT uq_program_field
        UNIQUE (program_id, field_id)
);

-- =========================================================
-- 14. SPECIALIZATION
-- =========================================================

CREATE TABLE specialization (
    specialization_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    specialization_name VARCHAR(255) NOT NULL,
    description TEXT,

    CONSTRAINT fk_specialization_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_program_specialization
        UNIQUE (program_id, specialization_name)
);

-- =========================================================
-- 15. CAREER_PATH
-- =========================================================

CREATE TABLE career_path (
    career_id BIGSERIAL PRIMARY KEY,
    career_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    demand_level VARCHAR(50),

    CONSTRAINT chk_career_demand_level
        CHECK (demand_level IN ('Low', 'Medium', 'High') OR demand_level IS NULL)
);

-- =========================================================
-- 16. PROGRAM_CAREER
-- Associative entity: Degree_Program M:N Career_Path
-- =========================================================

CREATE TABLE program_career (
    program_career_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    career_id BIGINT NOT NULL,

    CONSTRAINT fk_program_career_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_program_career_career
        FOREIGN KEY (career_id)
        REFERENCES career_path(career_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_program_career
        UNIQUE (program_id, career_id)
);

-- =========================================================
-- 17. UPLOADED_PDF
-- =========================================================

CREATE TABLE uploaded_pdf (
    pdf_id BIGSERIAL PRIMARY KEY,
    uploaded_by BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    academic_year INT NOT NULL,
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Uploaded',

    CONSTRAINT fk_uploaded_pdf_user
        FOREIGN KEY (uploaded_by)
        REFERENCES app_user(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_uploaded_pdf_status
        CHECK (status IN ('Uploaded', 'Processing', 'Completed', 'Failed'))
);

-- =========================================================
-- 18. OCR_JOB
-- =========================================================

CREATE TABLE ocr_job (
    ocr_job_id BIGSERIAL PRIMARY KEY,
    pdf_id BIGINT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Processing',
    confidence_score NUMERIC(5,2),
    error_message TEXT,

    CONSTRAINT fk_ocr_job_pdf
        FOREIGN KEY (pdf_id)
        REFERENCES uploaded_pdf(pdf_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_ocr_job_status
        CHECK (status IN ('Processing', 'Completed', 'Failed')),

    CONSTRAINT chk_ocr_job_confidence
        CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100))
);

-- =========================================================
-- 19. OCR_EXTRACTED_ROW
-- Staging table for raw OCR output
-- =========================================================

CREATE TABLE ocr_extracted_row (
    extracted_row_id BIGSERIAL PRIMARY KEY,
    ocr_job_id BIGINT NOT NULL,
    row_number INT NOT NULL,
    raw_university_name TEXT,
    raw_program_name TEXT,
    raw_district_name TEXT,
    raw_cutoff_z_score NUMERIC(6,4),
    page_number INT,
    confidence_score NUMERIC(5,2),
    verification_status VARCHAR(50) NOT NULL DEFAULT 'Pending',

    -- Optional matching fields for semi-automated admin review
    matched_program_id BIGINT,
    matched_district_id BIGINT,
    verified_by BIGINT,
    verified_at TIMESTAMP,
    rejection_reason TEXT,
    review_note TEXT,

    CONSTRAINT fk_ocr_row_job
        FOREIGN KEY (ocr_job_id)
        REFERENCES ocr_job(ocr_job_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_ocr_row_matched_program
        FOREIGN KEY (matched_program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_ocr_row_matched_district
        FOREIGN KEY (matched_district_id)
        REFERENCES district(district_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_ocr_row_verified_by
        FOREIGN KEY (verified_by)
        REFERENCES app_user(user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_ocr_row_confidence
        CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),

    CONSTRAINT chk_ocr_row_verification_status
        CHECK (verification_status IN ('Pending', 'Auto-Matched', 'Needs Review', 'Verified', 'Rejected', 'Corrected')),

    CONSTRAINT uq_ocr_job_row_number
        UNIQUE (ocr_job_id, row_number)
);

-- =========================================================
-- 20. CUTOFF_MARK
-- Official verified cutoff data
-- =========================================================

CREATE TABLE cutoff_mark (
    cutoff_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    district_id BIGINT NOT NULL,
    source_pdf_id BIGINT,
    academic_year INT NOT NULL,
    cutoff_z_score NUMERIC(6,4) NOT NULL,
    verification_status VARCHAR(50) NOT NULL DEFAULT 'Verified',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cutoff_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_cutoff_district
        FOREIGN KEY (district_id)
        REFERENCES district(district_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_cutoff_source_pdf
        FOREIGN KEY (source_pdf_id)
        REFERENCES uploaded_pdf(pdf_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_cutoff_verification_status
        CHECK (verification_status IN ('Pending', 'Verified', 'Rejected', 'Corrected')),

    CONSTRAINT uq_cutoff_program_district_year
        UNIQUE (program_id, district_id, academic_year)
);

-- =========================================================
-- 21. INDUSTRY_SCORE
-- Job market score for each degree programme
-- =========================================================

CREATE TABLE industry_score (
    industry_score_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL,
    score_year INT NOT NULL,
    job_demand_score NUMERIC(5,2),
    salary_score NUMERIC(5,2),
    growth_score NUMERIC(5,2),
    final_score NUMERIC(5,2),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_industry_score_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_job_demand_score
        CHECK (job_demand_score IS NULL OR (job_demand_score >= 0 AND job_demand_score <= 100)),

    CONSTRAINT chk_salary_score
        CHECK (salary_score IS NULL OR (salary_score >= 0 AND salary_score <= 100)),

    CONSTRAINT chk_growth_score
        CHECK (growth_score IS NULL OR (growth_score >= 0 AND growth_score <= 100)),

    CONSTRAINT chk_final_score
        CHECK (final_score IS NULL OR (final_score >= 0 AND final_score <= 100)),

    CONSTRAINT uq_industry_score_program_year
        UNIQUE (program_id, score_year)
);

-- =========================================================
-- 22. USER_QUERY
-- Stores one student search/recommendation request
-- =========================================================

CREATE TABLE user_query (
    query_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    stream_id BIGINT NOT NULL,
    district_id BIGINT NOT NULL,
    z_score NUMERIC(6,4) NOT NULL,
    result_year INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',

    CONSTRAINT fk_user_query_user
        FOREIGN KEY (user_id)
        REFERENCES app_user(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_user_query_stream
        FOREIGN KEY (stream_id)
        REFERENCES a_level_stream(stream_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_user_query_district
        FOREIGN KEY (district_id)
        REFERENCES district(district_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_user_query_status
        CHECK (status IN ('Pending', 'Completed', 'Failed')),

    CONSTRAINT chk_user_query_z_score
        CHECK (z_score >= -4.0000 AND z_score <= 4.0000)
);

-- =========================================================
-- 23. USER_QUERY_SUBJECT
-- Associative entity: User_Query M:N Subject
-- =========================================================

CREATE TABLE user_query_subject (
    query_subject_id BIGSERIAL PRIMARY KEY,
    query_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    subject_order INT NOT NULL,

    CONSTRAINT fk_user_query_subject_query
        FOREIGN KEY (query_id)
        REFERENCES user_query(query_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_user_query_subject_subject
        FOREIGN KEY (subject_id)
        REFERENCES subject(subject_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_subject_order
        CHECK (subject_order BETWEEN 1 AND 3),

    CONSTRAINT uq_user_query_subject
        UNIQUE (query_id, subject_id),

    CONSTRAINT uq_user_query_subject_order
        UNIQUE (query_id, subject_order)
);

-- =========================================================
-- 24. USER_QUERY_FIELD
-- Associative entity: User_Query M:N Field_Of_Interest
-- =========================================================

CREATE TABLE user_query_field (
    query_field_id BIGSERIAL PRIMARY KEY,
    query_id BIGINT NOT NULL,
    field_id BIGINT NOT NULL,

    CONSTRAINT fk_user_query_field_query
        FOREIGN KEY (query_id)
        REFERENCES user_query(query_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_user_query_field_field
        FOREIGN KEY (field_id)
        REFERENCES field_of_interest(field_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_user_query_field
        UNIQUE (query_id, field_id)
);

-- =========================================================
-- 25. RECOMMENDATION_RESULT
-- Stores generated recommendations for each User_Query
-- =========================================================

CREATE TABLE recommendation_result (
    result_id BIGSERIAL PRIMARY KEY,
    query_id BIGINT NOT NULL,
    program_id BIGINT NOT NULL,
    cutoff_id BIGINT,
    match_type VARCHAR(50) NOT NULL,
    z_score_difference NUMERIC(7,4),
    preference_score NUMERIC(5,2),
    industry_score_used NUMERIC(5,2),
    final_rank_score NUMERIC(5,2),
    recommendation_rank INT,
    explanation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recommendation_query
        FOREIGN KEY (query_id)
        REFERENCES user_query(query_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_recommendation_program
        FOREIGN KEY (program_id)
        REFERENCES degree_program(program_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_recommendation_cutoff
        FOREIGN KEY (cutoff_id)
        REFERENCES cutoff_mark(cutoff_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_match_type
        CHECK (match_type IN ('Best Matching', 'Pending/Potential', 'Not Eligible')),

    CONSTRAINT chk_preference_score
        CHECK (preference_score IS NULL OR (preference_score >= 0 AND preference_score <= 100)),

    CONSTRAINT chk_industry_score_used
        CHECK (industry_score_used IS NULL OR (industry_score_used >= 0 AND industry_score_used <= 100)),

    CONSTRAINT chk_final_rank_score
        CHECK (final_rank_score IS NULL OR (final_rank_score >= 0 AND final_rank_score <= 100)),

    CONSTRAINT uq_recommendation_query_program
        UNIQUE (query_id, program_id)
);

-- =========================================================
-- 26. ADMIN_AUDIT_LOG
-- Tracks admin actions
-- =========================================================

CREATE TABLE admin_audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    description TEXT,
    action_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_admin_audit_user
        FOREIGN KEY (admin_id)
        REFERENCES app_user(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================================================
-- 27. USEFUL INDEXES
-- These help speed up joins and searches
-- =========================================================

CREATE INDEX idx_app_user_role_id
ON app_user(role_id);

CREATE INDEX idx_user_query_user_id
ON user_query(user_id);

CREATE INDEX idx_user_query_stream_id
ON user_query(stream_id);

CREATE INDEX idx_user_query_district_id
ON user_query(district_id);

CREATE INDEX idx_degree_program_university_id
ON degree_program(university_id);

CREATE INDEX idx_cutoff_program_id
ON cutoff_mark(program_id);

CREATE INDEX idx_cutoff_district_id
ON cutoff_mark(district_id);

CREATE INDEX idx_cutoff_academic_year
ON cutoff_mark(academic_year);

CREATE INDEX idx_cutoff_verified
ON cutoff_mark(verification_status);

CREATE INDEX idx_recommendation_query_id
ON recommendation_result(query_id);

CREATE INDEX idx_recommendation_program_id
ON recommendation_result(program_id);

CREATE INDEX idx_ocr_job_pdf_id
ON ocr_job(pdf_id);

CREATE INDEX idx_ocr_row_job_id
ON ocr_extracted_row(ocr_job_id);

CREATE INDEX idx_ocr_row_verification_status
ON ocr_extracted_row(verification_status);

CREATE INDEX idx_program_field_program_id
ON program_field(program_id);

CREATE INDEX idx_program_field_field_id
ON program_field(field_id);

CREATE INDEX idx_program_stream_program_id
ON program_stream(program_id);

CREATE INDEX idx_program_subject_requirement_program_id
ON program_subject_requirement(program_id);