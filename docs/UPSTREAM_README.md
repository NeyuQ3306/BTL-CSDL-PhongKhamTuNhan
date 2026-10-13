# Hospital Database Management System

A relational hospital-management application built with MySQL, Python, and Flask. The project connects a normalized healthcare database to a browser-based interface for managing patients, employees, consultations, shifts, inpatient rooms, diagnoses, and surgeries.

> Academic group project for CS 631: Data Management and System Design. Built by me and Richard Tashjian. I contributed to database design, SQL development, application functionality, interface development, validation, and documentation. Richard had a larger role in data cleaning and function testing.

## Project highlights

- Designed a relational schema with primary keys, foreign keys, composite keys, and relationship tables.
- Built Flask workflows for patient and employee records, medical operations, and inpatient management.
- Added consultation, staff-shift, and surgery scheduling with conflict checks.
- Implemented room and bed availability tracking.
- Used parameterized SQL queries for user-provided values.
- Presented consultation and staffing schedules through calendar views.

## Core functionality

| Area | Examples |
|---|---|
| Patient management | Add, update, search, assign physicians, record diagnoses |
| Staff management | Add, update, remove, search, assign roles and clinics |
| Scheduling | Book consultations, staff shifts, and surgeries; detect conflicts |
| Inpatient management | View availability and assign or release rooms and beds |
| Database integrity | Primary keys, foreign keys, composite keys, and uniqueness constraints |

## Technology

- Python
- Flask
- MySQL
- PyMySQL
- HTML and CSS
- FullCalendar

## Repository structure

```text
.
├── app.py                 # Flask routes and database operations
├── hospital_db.sql        # MySQL schema
├── requirements.txt       # Python dependencies
├── .env.example           # Local configuration template
├── static/
│   └── styles.css
└── templates/             # Flask/Jinja interface templates
```

## Run locally

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the database

Run `hospital_db.sql` in MySQL Workbench or from the command line:

```bash
mysql -u root -p < hospital_db.sql
```

The script creates the `hospital_db` database and its table structure. It does not include real patient data.

### 4. Configure local credentials

Copy `.env.example` to `.env` and replace the placeholder values. The application loads this local file automatically. Never commit `.env`.

### 5. Start the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Design notes

The data model separates people, clinical activity, staffing, facilities, and medical reference data. Junction tables represent many-to-many relationships such as patient allergies, diagnosed illnesses, medication interactions, and employee skills. Scheduling and inpatient workflows apply application-level checks before database updates.

## Scope and limitations

This is an academic prototype, not a production clinical system. It has no authentication or authorization layer and must only be used with fictional demonstration data. A production healthcare application would additionally require role-based access, encryption, audit logging, stronger transaction handling, automated tests, and regulatory review.
