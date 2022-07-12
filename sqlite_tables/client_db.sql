CREATE TABLE contacts (
    talentlms_user_id INT PRIMARY KEY,
    firstname TEXT,
    lastname TEXT,
	login TEXT,
    active TEXT, -- Will be checkbox (True, False) in HS
    email TEXT,
    most_recent_linkedin_badge TEXT
);

CREATE TABLE courses (
    talentlms_course_id INT PRIMARY KEY,
    class_name TEXT,
    code TEXT,
    "start_date" INT,
    end_date INT,
    live_session_datetime INT,
    assignment_due_date INT
);

CREATE TABLE student_course_instance (
    talentlms_user_id INT,
    talentlms_course_id INT,
    student_name TEXT,
    class_name TEXT,
    completed_on INT,
    completion_status TEXT,
    completion_percent INT,
    total_time TEXT,
    total_time_seconds INT,
    last_accessed_unit_url TEXT,
    linkedin_badge TEXT,
    FOREIGN KEY(talentlms_user_id) REFERENCES contacts(talentlms_user_id),
    FOREIGN KEY(talentlms_course_id) REFERENCES courses(talentlms_course_id)
);

CREATE TABLE contact_hs_history (
    talentlms_user_id INT UNIQUE,
    hs_contact_id INT UNIQUE,
    FOREIGN KEY(talentlms_user_id) REFERENCES contacts(talentlms_user_id)
);

CREATE TABLE course_hs_history (
    talentlms_course_id INT UNIQUE,
    hs_course_id INT UNIQUE,
    FOREIGN KEY(talentlms_course_id) REFERENCES courses(talentlms_course_id)
);

CREATE TABLE student_course_instance_history (
    talentlms_user_id INT,
    talentlms_course_id INT,
    hs_association_id INT UNIQUE
    FOREIGN KEY(talentlms_user_id) REFERENCES contacts(talentlms_user_id),
    FOREIGN KEY(talentlms_course_id) REFERENCES courses(talentlmst_course_id)
);

CREATE TABLE time_tracking (
    last_modified_time TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime')),
    obj TEXT CHECK(obj IN ('contacts', 'courses', 'student_course_instance'))
);