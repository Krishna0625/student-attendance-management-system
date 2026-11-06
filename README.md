# Project 3: Student Attendance and Academic Performance Management System

A simple, beginner-friendly web application built with **Python**, **Flask**, **SQLite**, **HTML**, and **CSS**. Designed for college internal practical examinations and viva demonstrations.

---

## 1. Features

- **Faculty Login & Session Protection**:
  - Secure login using Flask sessions.
  - Protected routes (`@login_required`) prevent unauthorized access to pages.
  - Default Faculty Credentials:
    - **Username:** `admin`
    - **Password:** `admin123`
- **Dashboard**:
  - Displays the total number of registered students.
  - Provides quick navigation cards to all modules.
- **Student Management**:
  - Register students with **Name**, **Roll Number**, and **Class**.
  - Prevents duplicate roll numbers (`UNIQUE` constraint + error handling).
  - Displays all registered students in a clean table.
- **Attendance Management**:
  - Select any registered student from a dropdown, choose a date, and mark **Present** or **Absent**.
  - Prevents duplicate attendance entries for the same student on the same date (automatically updates the existing record if submitted again).
  - Displays recorded attendance history in a table.
- **Internal Marks Management**:
  - Select a student, enter the subject name, and enter internal marks (`0–100`).
  - Validates marks range (`0–100`) and displays all entered marks in a table.
- **Performance Reports**:
  - Calculates **Total Attendance Percentage**:
    $$\text{Attendance Percentage} = \left(\frac{\text{Number of Present Days}}{\text{Total Attendance Days}}\right) \times 100$$
  - Calculates **Average Internal Marks** across entered subjects.
  - Safely handles students with zero attendance records or zero marks entered without errors.

---

## 2. Project Folder Structure

```text
Project-3-Student-Management/
├── app.py                  # Main Flask backend application and database logic
├── requirements.txt        # Python package dependencies
├── database.db             # SQLite database (created automatically on startup)
├── README.md               # Project documentation and setup instructions
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared admin layout (sidebar, top navbar, notifications)
│   ├── login.html          # Split-screen faculty login page
│   ├── dashboard.html      # Main admin dashboard with live SQLite stats
│   ├── students.html       # Student registration and searchable directory
│   ├── attendance.html     # Attendance marking, today's summary, and history
│   ├── marks.html          # Internal marks entry and grade band table
│   └── report.html         # Attendance progress bars and academic report page
└── static/
    ├── style.css           # Common University Portal stylesheet (Navy & White theme)
    └── script.js           # Vanilla JS for live clock, search filter, and UI controls
```

---

## 3. How to Run the Application (Windows PowerShell)

Run the following commands inside the project folder (`Project-3-Student-Management`):

1. **Create virtual environment:**
   ```powershell
   py -3.13 -m venv venv
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install packages:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python app.py
   ```

5. **Open in browser:**
   ```text
   http://127.0.0.1:5000
   ```

---

## 4. Database Tables (SQLite)

1. **`students`**: `id` (Primary Key), `name`, `roll` (Unique), `class`
2. **`attendance`**: `id` (Primary Key), `student_id` (Foreign Key), `date`, `status` (`UNIQUE(student_id, date)`)
3. **`marks`**: `id` (Primary Key), `student_id` (Foreign Key), `subject`, `marks`
DevOps integration started: Git and GitHub configured successfully.Testing automatic Jenkins build
