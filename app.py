from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps
from datetime import date

app = Flask(__name__)
app.secret_key = "student_management_secret"

DATABASE = "database.db"


# Helper function to connect to the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables automatically when the application starts
def init_db():
    conn = get_db()

    # 1. Students table (roll number is UNIQUE to prevent duplicates)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT UNIQUE NOT NULL,
            class TEXT NOT NULL
        )
    """)

    # 2. Attendance table (UNIQUE constraint on student_id and date)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # 3. Internal Marks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize database tables on startup
init_db()


# Decorator to protect routes so only logged-in faculty can access them
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "faculty" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# A. Faculty Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Check demonstration faculty credentials
        if username == "admin" and password == "admin123":
            session["faculty"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password. Please try again.")

    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    session.pop("faculty", None)
    return redirect(url_for("login"))


# B. Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    today_str = date.today().isoformat()

    # Total registered students
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    # Today's attendance counts from SQLite
    present_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'",
        (today_str,)
    ).fetchone()[0]

    absent_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Absent'",
        (today_str,)
    ).fetchone()[0]

    # Overall attendance percentage across all SQLite attendance records
    total_attendance_records = conn.execute(
        "SELECT COUNT(*) FROM attendance"
    ).fetchone()[0]
    total_present_records = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE status = 'Present'"
    ).fetchone()[0]

    attendance_percentage = (
        round((total_present_records / total_attendance_records) * 100, 1)
        if total_attendance_records > 0
        else 0.0
    )

    # Recent registered students (latest 5)
    recent_students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"
    ).fetchall()

    # Today's attendance records joined with student info
    today_records = conn.execute("""
        SELECT a.date, a.status, s.name, s.roll, s.class
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.id DESC
    """, (today_str,)).fetchall()

    conn.close()

    unmarked_today = max(0, total - (present_today + absent_today))

    return render_template(
        "dashboard.html",
        total=total,
        present_today=present_today,
        absent_today=absent_today,
        unmarked_today=unmarked_today,
        attendance_percentage=attendance_percentage,
        recent_students=recent_students,
        today_records=today_records,
        today=today_str
    )


# C. Student Management (Add and View Students)
@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    conn = get_db()
    message = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll", "").strip()
        student_class = request.form.get("class", "").strip()

        if not name or not roll or not student_class:
            error = "All fields (Name, Roll Number, and Class) are required."
        else:
            try:
                conn.execute(
                    "INSERT INTO students (name, roll, class) VALUES (?, ?, ?)",
                    (name, roll, student_class)
                )
                conn.commit()
                message = f"Student '{name}' (Roll No: {roll}) added successfully!"
            except sqlite3.IntegrityError:
                error = f"Roll Number '{roll}' already exists! Duplicate roll numbers are not allowed."

    student_list = conn.execute("SELECT * FROM students ORDER BY id ASC").fetchall()
    conn.close()

    return render_template(
        "students.html",
        students=student_list,
        message=message,
        error=error
    )


# D. Attendance Management
@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    conn = get_db()
    message = None
    error = None
    today_str = date.today().isoformat()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        attendance_date = request.form.get("date", "").strip()
        status = request.form.get("status", "").strip()

        if not student_id or not attendance_date or status not in ("Present", "Absent"):
            error = "Please select a student, valid date, and attendance status."
        else:
            # Check if attendance already exists for this student on this date
            existing = conn.execute(
                "SELECT id FROM attendance WHERE student_id = ? AND date = ?",
                (student_id, attendance_date)
            ).fetchone()

            if existing:
                # Update existing attendance record if submitted again for the same date
                conn.execute(
                    "UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?",
                    (status, student_id, attendance_date)
                )
                message = f"Attendance updated to '{status}' for {attendance_date}."
            else:
                conn.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                    (student_id, attendance_date, status)
                )
                message = f"Attendance marked as '{status}' for {attendance_date}."

            conn.commit()

    student_list = conn.execute("SELECT * FROM students ORDER BY id ASC").fetchall()
    attendance_records = conn.execute("""
        SELECT a.date, a.status, s.name, s.roll, s.class
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, s.id ASC
    """).fetchall()

    # Today's summary counts for the attendance page
    present_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'",
        (today_str,)
    ).fetchone()[0]
    absent_today = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Absent'",
        (today_str,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "attendance.html",
        students=student_list,
        attendance_records=attendance_records,
        today=today_str,
        present_today=present_today,
        absent_today=absent_today,
        message=message,
        error=error
    )


# E. Internal Marks Management
@app.route("/marks", methods=["GET", "POST"])
@login_required
def marks():
    conn = get_db()
    message = None
    error = None

    if request.method == "POST":
        student_id = request.form.get("student_id")
        subject = request.form.get("subject", "").strip()
        mark_input = request.form.get("marks", "").strip()

        if not student_id or not subject or mark_input == "":
            error = "Please select a student, enter a subject, and provide marks."
        else:
            try:
                mark_value = int(mark_input)
                if mark_value < 0 or mark_value > 100:
                    error = "Internal marks must be between 0 and 100."
                else:
                    conn.execute(
                        "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
                        (student_id, subject, mark_value)
                    )
                    conn.commit()
                    message = f"Marks ({mark_value}/100) for '{subject}' saved successfully!"
            except ValueError:
                error = "Invalid marks entered. Please enter a whole number between 0 and 100."

    student_list = conn.execute("SELECT * FROM students ORDER BY id ASC").fetchall()
    marks_records = conn.execute("""
        SELECT m.id, m.subject, m.marks, s.name, s.roll, s.class
        FROM marks m
        JOIN students s ON m.student_id = s.id
        ORDER BY m.id DESC
    """).fetchall()
    conn.close()

    return render_template(
        "marks.html",
        students=student_list,
        marks_records=marks_records,
        message=message,
        error=error
    )


# F. Performance Reports
@app.route("/report")
@login_required
def report():
    conn = get_db()
    student_list = conn.execute("SELECT * FROM students ORDER BY id ASC").fetchall()

    reports = []

    for student in student_list:
        sid = student["id"]

        # Total attendance days recorded for this student
        total = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id = ?",
            (sid,)
        ).fetchone()[0]

        # Number of days marked as 'Present'
        present = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Present'",
            (sid,)
        ).fetchone()[0]

        # Attendance Percentage = (Number of Present Days / Total Attendance Days) * 100
        percentage = (present / total * 100) if total > 0 else 0

        # Average internal marks
        average = conn.execute(
            "SELECT AVG(marks) FROM marks WHERE student_id = ?",
            (sid,)
        ).fetchone()[0]

        reports.append({
            "name": student["name"],
            "roll": student["roll"],
            "class": student["class"],
            "present_days": present,
            "total_days": total,
            "attendance": round(percentage, 2),
            "average": round(average, 2) if average is not None else 0
        })

    conn.close()
    return render_template("report.html", reports=reports)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
