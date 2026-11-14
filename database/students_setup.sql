-- =====================================================================
-- COMP 3005 - Assignment 3: PostgreSQL CRUD Application
-- File:    students_setup.sql
-- Purpose: Creates the "students" table from the provided schema and
--          populates it with the initial data set.
--
-- How to run:
--   1. In pgAdmin, create a database named  students_db
--   2. Right-click students_db -> Query Tool
--   3. Open this file (folder icon) and press Execute (F5)
--   (or from a terminal:  psql -U postgres -d students_db -f students_setup.sql)
-- =====================================================================

-- Drop the table first (if it already exists) so the script can be
-- re-run any time to reset the database to its original state.
DROP TABLE IF EXISTS students;

-- ---------------------------------------------------------------------
-- Table: students
--   student_id      : SERIAL = auto-incrementing integer, PRIMARY KEY
--   first_name      : TEXT, required (NOT NULL)
--   last_name       : TEXT, required (NOT NULL)
--   email           : TEXT, required (NOT NULL) and must be UNIQUE
--   enrollment_date : DATE, optional (may be NULL)
-- ---------------------------------------------------------------------
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    first_name      TEXT   NOT NULL,
    last_name       TEXT   NOT NULL,
    email           TEXT   NOT NULL UNIQUE,
    enrollment_date DATE
);

-- ---------------------------------------------------------------------
-- Initial data (student_id is generated automatically: 1, 2, 3)
-- ---------------------------------------------------------------------
INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
('John', 'Doe',   'john.doe@example.com',   '2023-09-01'),
('Jane', 'Smith', 'jane.smith@example.com', '2023-09-01'),
('Jim',  'Beam',  'jim.beam@example.com',   '2023-09-02');

-- Verify the setup
SELECT * FROM students ORDER BY student_id;
