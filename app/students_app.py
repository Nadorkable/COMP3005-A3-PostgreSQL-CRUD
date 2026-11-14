"""
COMP 3005 - Assignment 3: PostgreSQL CRUD Application
File:    students_app.py
Student:  Nada Thabet
Student ID: 101244661

Purpose:
    A small Python command-line application that connects to a PostgreSQL
    database and performs CRUD (Create, Read, Update, Delete) operations
    on the "students" table:

        getAllStudents()                       -> READ
        addStudent(first, last, email, date)   -> CREATE
        updateStudentEmail(student_id, email)  -> UPDATE
        deleteStudent(student_id)              -> DELETE

Usage:
    python students_app.py              (interactive menu)

Connection settings are read from environment variables if they are set,
otherwise the defaults below are used. If no password is set, the program
asks for it securely (the password is not shown while typing).
"""

import os
import sys
from datetime import date, datetime
from getpass import getpass

import psycopg2
from psycopg2 import errors


# ---------------------------------------------------------------------------
# Database connection settings
# ---------------------------------------------------------------------------
# Each value can be overridden with an environment variable, e.g.
#   set DB_PASSWORD=mypassword   (Windows CMD)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "students_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),  # ask the user
}


def get_connection():
    """Open and return a new connection to the PostgreSQL database.

    Exits the program with a helpful message if the connection fails
    (e.g. wrong password, PostgreSQL not running, database missing).
    """
    if DB_CONFIG["password"] is None:
        DB_CONFIG["password"] = getpass(
            f"Password for PostgreSQL user '{DB_CONFIG['user']}': "
        )
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print("\n[ERROR] Could not connect to the database.")
        print("        Check that PostgreSQL is running, the database "
              f"'{DB_CONFIG['dbname']}' exists, and the password is correct.")
        print(f"        Details: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------

def getAllStudents(conn):
    """READ: retrieve every row of the students table and print it as a table.

    Returns the list of rows so it can also be used by other code
    (an empty list if the query failed).
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT student_id, first_name, last_name, email, enrollment_date "
                "FROM students ORDER BY student_id;"
            )
            rows = cur.fetchall()
        # psycopg2 opens a transaction even for a SELECT. Ending it here means
        # the app doesn't sit "idle in transaction" holding a lock on the table
        # (which would block a DROP/reset from pgAdmin while the app is open).
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[ERROR] Could not read students: {e}\n")
        return []

    # Print a neatly aligned table
    header = f"{'ID':<4} {'First Name':<12} {'Last Name':<12} {'Email':<30} {'Enrolled':<10}"
    print("\n" + header)
    print("-" * len(header))
    for sid, first, last, email, enrolled in rows:
        print(f"{sid:<4} {first:<12} {last:<12} {email:<30} {str(enrolled or ''):<10}")
    print(f"({len(rows)} student(s))\n")
    return rows


def addStudent(conn, first_name, last_name, email, enrollment_date):
    """CREATE: insert a new student record.

    student_id is not supplied - PostgreSQL generates it automatically (SERIAL).
    Uses a parameterised query (%s placeholders) to prevent SQL injection.
    Returns the new student_id, or None if the insert failed.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO students (first_name, last_name, email, enrollment_date) "
                "VALUES (%s, %s, %s, %s) RETURNING student_id;",
                (first_name, last_name, email, enrollment_date),
            )
            new_id = cur.fetchone()[0]
        conn.commit()  # make the change permanent
        print(f"[OK] Added {first_name} {last_name} with student_id = {new_id}.\n")
        return new_id
    except errors.UniqueViolation:
        conn.rollback()  # undo the failed transaction
        print(f"[ERROR] The email '{email}' is already used by another student.\n")
    except errors.NotNullViolation:
        conn.rollback()
        print("[ERROR] First name, last name and email are required.\n")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[ERROR] Could not add student: {e}\n")
    return None


def updateStudentEmail(conn, student_id, new_email):
    """UPDATE: change the email address of the student with the given id.

    Returns True if a row was updated, False otherwise.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE students SET email = %s WHERE student_id = %s;",
                (new_email, student_id),
            )
            updated = cur.rowcount  # number of rows affected
        conn.commit()
        if updated == 0:
            print(f"[INFO] No student found with student_id = {student_id}.\n")
            return False
        print(f"[OK] Email for student_id {student_id} changed to {new_email}.\n")
        return True
    except errors.UniqueViolation:
        conn.rollback()
        print(f"[ERROR] The email '{new_email}' is already used by another student.\n")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[ERROR] Could not update email: {e}\n")
    return False


def deleteStudent(conn, student_id):
    """DELETE: remove the student with the given id.

    Returns True if a row was deleted, False otherwise.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
            deleted = cur.rowcount
        conn.commit()
        if deleted == 0:
            print(f"[INFO] No student found with student_id = {student_id}.\n")
            return False
        print(f"[OK] Deleted student with student_id = {student_id}.\n")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[ERROR] Could not delete student: {e}\n")
    return False


# ---------------------------------------------------------------------------
# Input helpers (validate what the user types before touching the database)
# ---------------------------------------------------------------------------

def ask_text(prompt):
    """Ask until the user types a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty.")


def ask_int(prompt):
    """Ask until the user types a whole number."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("  Please enter a whole number (e.g. 4).")


def ask_date(prompt):
    """Ask for a date in YYYY-MM-DD format. Blank = today's date."""
    while True:
        value = input(prompt).strip()
        if value == "":
            return date.today()
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("  Please use the format YYYY-MM-DD (e.g. 2023-09-03).")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

MENU = """========== Students Database ==========
 1. Get all students
 2. Add a student
 3. Update a student's email
 4. Delete a student
 0. Exit
======================================="""


def main():
    """Connect once, then loop over the menu until the user chooses Exit."""
    conn = get_connection()
    print(f"Connected to database '{DB_CONFIG['dbname']}' on "
          f"{DB_CONFIG['host']}:{DB_CONFIG['port']}.\n")
    try:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()

            if choice == "1":
                getAllStudents(conn)

            elif choice == "2":
                first = ask_text("First name: ")
                last = ask_text("Last name: ")
                email = ask_text("Email: ")
                enrolled = ask_date("Enrollment date (YYYY-MM-DD, blank = today): ")
                addStudent(conn, first, last, email, enrolled)

            elif choice == "3":
                sid = ask_int("Student ID to update: ")
                email = ask_text("New email: ")
                updateStudentEmail(conn, sid, email)

            elif choice == "4":
                sid = ask_int("Student ID to delete: ")
                deleteStudent(conn, sid)

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option, please choose 0-4.\n")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: leave the program cleanly
        print("\nExiting.")
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        # The connection dropped mid-session (server stopped, network/tunnel closed)
        print("\n[ERROR] Lost the connection to the database. "
              "Check that PostgreSQL is reachable, then restart the app.")
        print(f"        Details: {e}")
    finally:
        conn.close()  # always release the connection


if __name__ == "__main__":
    main()
