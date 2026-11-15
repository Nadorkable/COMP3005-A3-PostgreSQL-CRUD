# COMP 3005 – Assignment 3: PostgreSQL CRUD Application

**Author:** Nada Thabet (101244661)

A Python command-line application that connects to a PostgreSQL database and performs
CRUD (Create, Read, Update, Delete) operations on a `students` table.

## 🎥 Video Demonstration

**Video link:** *To be added once the demonstration video has been recorded and uploaded.*

---

## Repository Structure

```
.
├── database/
│   └── students_setup.sql   # Creates the students table + inserts the initial data
├── app/
│   ├── students_app.py      # Python application with the 4 CRUD functions
│   └── requirements.txt     # Python dependency (psycopg2-binary)
└── README.md
```

## Database Schema

| Field             | Type                  | Constraints               |
|-------------------|-----------------------|---------------------------|
| `student_id`      | `SERIAL` (integer)    | Primary Key, auto-increment |
| `first_name`      | `TEXT`                | NOT NULL                  |
| `last_name`       | `TEXT`                | NOT NULL                  |
| `email`           | `TEXT`                | NOT NULL, UNIQUE          |
| `enrollment_date` | `DATE`                | —                         |

## Application Functions

| Function | Operation | What it does |
|----------|-----------|--------------|
| `getAllStudents()` | READ | Runs `SELECT` on the `students` table and prints every record in a formatted table. |
| `addStudent(first_name, last_name, email, enrollment_date)` | CREATE | Runs `INSERT`; PostgreSQL generates the `student_id`. Shows an error if the email already exists. |
| `updateStudentEmail(student_id, new_email)` | UPDATE | Runs `UPDATE ... SET email`. Reports if the ID does not exist or the email is already taken. |
| `deleteStudent(student_id)` | DELETE | Runs `DELETE`. Reports if the ID does not exist. |

In the code each function also takes the open database connection (`conn`) as its first
argument, e.g. `addStudent(conn, first_name, last_name, email, enrollment_date)`, so the
app opens one connection at startup and reuses it for every operation.

All queries use parameterised placeholders (`%s`) to prevent SQL injection, and every
change is committed (or rolled back on error) so the database is never left half-updated.
Errors such as a duplicate email, an unknown `student_id`, or a lost connection are
reported with a clear message instead of crashing the program.

---

## Prerequisites

- [PostgreSQL](https://www.postgresql.org/download/) (includes pgAdmin 4)
- [Python 3.8+](https://www.python.org/downloads/)

## Setup and Run Instructions

### 1. Clone the repository
```bash
git clone <this-repo-url>
cd <repo-folder>
```

### 2. Create the database (pgAdmin)
1. Open **pgAdmin 4** and connect to your server.
2. Right-click **Databases → Create → Database…**, name it **`students_db`**, click **Save**.
3. Right-click **`students_db` → Query Tool**.
4. Click the **Open File** icon, select `database/students_setup.sql`, then press **Execute (F5)**.
5. The output shows the 3 initial students.

*Alternative (terminal):*
```bash
psql -U postgres -c "CREATE DATABASE students_db;"
psql -U postgres -d students_db -f database/students_setup.sql
```

### 3. Install the Python dependency
```bash
cd app
pip install -r requirements.txt
```

### 4. Run the application
```bash
python students_app.py
```
Enter your PostgreSQL password when prompted, then choose an option from the menu:

```
========== Students Database ==========
 1. Get all students
 2. Add a student
 3. Update a student's email
 4. Delete a student
 0. Exit
=======================================
```

### Connection settings (optional)
Defaults: host `localhost`, port `5432`, database `students_db`, user `postgres`.
Override them with environment variables if yours differ:

| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `students_db` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | *(asked at startup)* |

Example (Windows Command Prompt):
```bat
set DB_PORT=5433
python students_app.py
```
Example (Windows PowerShell): `$env:DB_PORT="5433"; python students_app.py`

**Remote server (as in the demo video):** my PostgreSQL runs on a course virtual machine.
I reach it through an SSH tunnel, `ssh -L 5433:localhost:5432 <user>@<vm-address>`, which
forwards local port 5433 to PostgreSQL on the VM. With the tunnel open, set
`DB_HOST=localhost` and `DB_PORT=5433` before running the app. If PostgreSQL is installed
on your own machine, the defaults work and no tunnel is needed.

### Resetting the database
Re-run `database/students_setup.sql`. It drops and recreates the table with the original 3 students.
