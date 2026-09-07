from flask import Flask, render_template, request, redirect, url_for, flash, g, has_request_context, jsonify
from datetime import datetime
import os
import pymysql
import random
from dotenv import load_dotenv
from pymysql.err import IntegrityError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development-only-secret')

# Connecting to the database
conn = pymysql.connect(
    host=os.environ.get('DB_HOST', 'localhost'),
    port=int(os.environ.get('DB_PORT', '3306')),
    user=os.environ.get('DB_USER', 'hos_db'),
    password=os.environ.get('DB_PASSWORD', ''),
    database=os.environ.get('DB_NAME', 'hospital_db'),
    cursorclass=pymysql.cursors.DictCursor
)

# Makes each variable passing through each template render global
@app.context_processor
def inject_globals():
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM Patient')
        patients = cursor.fetchall()
        cursor.execute('SELECT EmploymentNumber FROM Physician')
        physicians = cursor.fetchall()
        cursor.execute('SELECT * FROM Illness')
        illnesses = cursor.fetchall()
        cursor.execute('SELECT * FROM Nurse')
        nurses = cursor.fetchall()
        cursor.execute('SELECT * FROM Employee')
        employees = cursor.fetchall()
        cursor.execute('SELECT * FROM Clinic')
        clinics = cursor.fetchall()
        cursor.execute('SELECT * FROM Surgeon')
        surgeons = cursor.fetchall()
        cursor.execute('SELECT * FROM Consultation')
        consultations_all = cursor.fetchall()

    return dict(
        patients=patients,
        physicians=physicians,
        illnesses=illnesses,
        nurse=nurses,
        events=g.events,
        employees=employees,
        clinics=clinics,
        surgeons=surgeons,
        consultations_all=consultations_all
    )

# Ensuring that the calendars is updated globally to all routes.
@app.before_request
def fetch_calendar_data():
    if not has_request_context():
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT c.ConsultationID, c.startTime, c.endTime, c.ConsultationDate, 
                       c.Notes, p.Name AS PatientName, e.Name AS PhysicianName
                FROM Consultation c
                JOIN Patient p ON c.PatientNumber = p.PatientNumber
                JOIN Employee e ON c.EmploymentNumber = e.EmploymentNumber
            ''')
            consultations = cursor.fetchall()

        events = []
        for consultation in consultations:
            try:
                start_time = datetime.strptime(
                    f"{consultation['ConsultationDate']} {consultation['startTime']}",
                    "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                end_time = datetime.strptime(
                    f"{consultation['ConsultationDate']} {consultation['endTime']}",
                    "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                events.append({
                    'title': f"Consultation with {consultation['PatientName']} - {consultation['PhysicianName']}",
                    'start': start_time,
                    'end': end_time,
                    'description': consultation['Notes']
                })
            except Exception as time_error:
                print("Datetime parsing error:", time_error)
        g.events = events

    except Exception as e:
        print("Error loading consultations:", e)
        g.events = []

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT s.EmploymentNumber, s.ClinicID, s.ScheduleDate, s.BeginTime, s.EndTime, 
                       e.Name AS PhysicianName, c.Address AS ClinicLoca
                FROM Schedule s
                JOIN Employee e ON s.EmploymentNumber = e.EmploymentNumber
                JOIN Clinic c ON s.ClinicID = c.ClinicID
            ''')
            schedules = cursor.fetchall()

        shift_events = []
        for schedule in schedules:
            try:
                start_time = datetime.strptime(
                    f"{schedule['ScheduleDate']} {schedule['BeginTime']}",
                    "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                end_time = datetime.strptime(
                    f"{schedule['ScheduleDate']} {schedule['EndTime']}",
                    "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                shift_events.append({
                    'title': f"Shift: {schedule['PhysicianName']} at {schedule['ClinicLoca']}",
                    'start': start_time,
                    'end': end_time,
                    'description': f"Shift at {schedule['ClinicLoca']} for {schedule['PhysicianName']}"
                })
            except Exception as time_error:
                print("Datetime parsing error in shifts:", time_error)

        g.shift_events = shift_events

    except Exception as e:
        print("Error loading shifts:", e)
        g.shift_events = []

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT s.SurgeryDate, s.StartTime, s.EndTime, e.Name AS SurgeonName
                FROM Surgery s
                JOIN Employee e ON s.SurgeonEmploymentNumber = e.EmploymentNumber
            ''')
            surgeries = cursor.fetchall()

        surgery_events = []
        for row in surgeries:
            try:
                start_time = datetime.strptime(
                    f"{row['SurgeryDate']} {row['StartTime']}", "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                end_time = datetime.strptime(
                    f"{row['SurgeryDate']} {row['EndTime']}", "%Y-%m-%d %H:%M:%S"
                ).isoformat()
                surgery_events.append({
                    'title': f"Surgery - {row['SurgeonName']}",
                    'start': start_time,
                    'end': end_time,
                    'description': f"Surgery by {row['SurgeonName']}"
                })
            except Exception as time_error:
                print("Datetime parsing error in surgeries:", time_error)

        g.surgery_events = surgery_events

    except Exception as e:
        print("Error loading surgeries:", e)
        g.surgery_events = []


# Route for InPatient
@app.route('/In_Patient')
def In_Patient():
    with conn.cursor() as cursor:
        # Fetch patients
        cursor.execute("SELECT * FROM Patient")
        patients = cursor.fetchall()

        # InPatient assignments
        cursor.execute("""
            SELECT i.PatientNumber, i.RoomNumber, b.BedLabel, i.DateOfAdmission, e.Name AS NurseName
            FROM InPatient i
            LEFT JOIN Employee e ON i.EmploymentNumber = e.EmploymentNumber
            LEFT JOIN bed b ON i.BedID = b.BedID
        """)
        inpatient_assignments = cursor.fetchall()

        # Doctor assignments
        cursor.execute("""
            SELECT p.PatientNumber, p.Name AS PatientName, e.Name AS DoctorName
            FROM Patient p
            LEFT JOIN Employee e ON p.EmploymentNumber = e.EmploymentNumber
        """)
        doctor_assignments = cursor.fetchall()

        # Nurse assignments
        cursor.execute("""
            SELECT i.PatientNumber, i.RoomNumber, e.Name AS NurseName
            FROM InPatient i
            LEFT JOIN Employee e ON i.EmploymentNumber = e.EmploymentNumber
        """)
        nurse_assignments = cursor.fetchall()

        # Available rooms
        cursor.execute("""
            SELECT DISTINCT r.RoomNumber
            FROM room r
            JOIN bed b ON r.RoomNumber = b.RoomNumber
            WHERE b.Availability = 'Available'
        """)
        available_rooms = cursor.fetchall()

        # Available beds
        cursor.execute("""
            SELECT DISTINCT BedID, RoomNumber, BedLabel
            FROM bed
            WHERE Availability = 'Available'
        """)
        available_beds = cursor.fetchall()

        # Nurse list
        cursor.execute("""
            SELECT EmploymentNumber
            FROM Employee
            WHERE Position = 'Nurse'
        """)
        nurses = cursor.fetchall()

        cursor.execute("SELECT * FROM OperationTheater")
        operation_theaters = cursor.fetchall()

        cursor.execute("SELECT * FROM SurgeryType")
        surgery_types = cursor.fetchall()

        cursor.execute("""
          SELECT s.SurgeryDate, s.StartTime, s.EndTime, e.Name AS SurgeonName
          FROM Surgery s
          JOIN employee e ON s.SurgeonEmploymentNumber = e.EmploymentNumber
        """)
        rows = cursor.fetchall()

        surgery_events = []
        for row in rows:
          if row['SurgeryDate'] and row['StartTime'] and row['EndTime']:
            surgery_events.append({
              "title": f"Surgery - {row['SurgeonName']}",
              "start": f"{row['SurgeryDate']}T{row['StartTime']}",
              "end": f"{row['SurgeryDate']}T{row['EndTime']}",
            })

    return render_template("InPatient_Management.html",
                           patients=patients,
                           inpatient_assignments=inpatient_assignments,
                           doctor_assignments=doctor_assignments,
                           nurse_assignments=nurse_assignments,
                           available_rooms=available_rooms,
                           available_beds=available_beds,
                           nurses=nurses,
                           operation_theaters=operation_theaters,
                           surgery_types=surgery_types,
                           surgery_events=surgery_events)

# Route for Patient Management Page
@app.route('/Patient')
def Patient():
    return render_template('PatientManagement.html', events=g.events or [])


# Route for Medical Management Page
@app.route('/Medical')
def Medical():
    with conn.cursor() as cursor:
        # Fetch shift data
        cursor.execute("""
            SELECT s.ScheduleDate, s.BeginTime, s.EndTime, e.Name AS FullName
            FROM schedule s
            JOIN employee e ON s.EmploymentNumber = e.EmploymentNumber
        """)
        schedule_data = cursor.fetchall()

        # Fetch dropdown data
        cursor.execute("SELECT * FROM employee")
        employees = cursor.fetchall()

        cursor.execute("SELECT * FROM clinic")
        clinics = cursor.fetchall()

    # Build shift events with deduplication
    shift_events = []
    seen = set()

    for row in schedule_data:
        key = (
            str(row['ScheduleDate']),
            str(row['BeginTime']),
            str(row['EndTime']),
            row['FullName']
        )

        if key in seen:
            continue
        seen.add(key)

        start_time = f"{row['ScheduleDate']}T{row['BeginTime']}"
        end_time = f"{row['ScheduleDate']}T{row['EndTime']}"
        title = f"Shift: {row['FullName']}"

        shift_events.append({
            "title": title,
            "start": start_time,
            "end": end_time
        })

    print("Total shift events sent to template:", len(shift_events))

    print("Final shift_events:")
    for event in shift_events:
       print(event)
    return render_template(
        "MedicalManagement.html",
        shift_events=g.get("shift_events", []),
        employees=employees,
        clinics=clinics,
        searchResults=None,
    )

# Home Route to Portal Page
@app.route('/')
def home():
    return render_template("PortalPage.html")

# Adding the Patient functionality
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        patient_number = request.form['PNum']
        full_name = request.form['Name']
        address = f"{request.form.get('Street', '')} Apt {request.form.get('Apt', '')} {request.form.get('City', '')}, {request.form.get('State', '')} {request.form.get('Zip', '')}"
        telephone_number = request.form['TelephoneNumber']
        ssn = request.form['SSN']
        gender = request.form['Gender']
        dob = request.form['DOB']
        blood_type = request.form['BloodType']
        employment_number = request.form['DoctorID']
        illness = request.form['Illness']
        action = request.form['action']
        with conn.cursor() as cursor:

            if action == 'update':
                sql = '''
                UPDATE PATIENT
                SET Name = %s,
                Address = %s,
                TelephoneNumber = %s,
                SSN = %s,
                Gender = %s,
                DOB = %s,
                BloodType = %s,
                EmploymentNumber = %s,
                Illness = %s
                WHERE PatientNumber = %s
                '''
                cursor.execute(sql, (full_name, address, telephone_number, ssn, gender, dob, blood_type, employment_number, illness, patient_number))
                flash("Patient updated successfully!")

            elif action == 'submit':
                sql = '''
                    INSERT INTO Patient (Name, Address, TelephoneNumber, SSN, Gender, DOB, BloodType, EmploymentNumber, Illness)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(sql, (full_name, address, telephone_number, ssn, gender, dob, blood_type, employment_number, illness))
                flash("Patient added successfully!")
            conn.commit()
    return render_template("PatientManagement.html")


# Schedule Consultation functionality
@app.route('/schedule_patient', methods=['GET', 'POST'])
def schedule_patients():
    if request.method == 'POST':
        consultationID = random.randint(1, 1000000)
        patient_number = request.form['PNum']
        physician_ID = request.form['DoctorID']
        day = request.form['scheduleDay']
        notes = request.form['scheduleReason']
        startTime = request.form['startTime']
        endTime = request.form['endTime']
        action = request.form['action']

        try:
            with conn.cursor() as cursor:
                if action == "submit":
                    sql2 = '''
                    SELECT c.EmploymentNumber, c.startTime, c.endTime, c.ConsultationDate
                    FROM Consultation c
                    WHERE c.EmploymentNumber = %s
                    AND c.startTime >= %s
                    AND c.endTime <= %s
                    AND c.ConsultationDate = %s
                        '''
                    cursor.execute(sql2, (physician_ID, startTime, endTime, day))
                    checkResults = cursor.fetchall()
                    print(checkResults)
                    if not checkResults:
                        sql = '''
                        INSERT INTO Consultation (ConsultationID, PatientNumber, EmploymentNumber, ConsultationDate, Notes, startTime, endTime)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    '''
                        cursor.execute(sql, (consultationID, patient_number, physician_ID, day, notes, startTime, endTime))
                        flash("Consultation scheduled successfully!")
                    else:
                        flash("Duplicate consultation found. Cannot add to calendar.")
                elif action == "remove":

                    sql_delete = '''
                        DELETE 
                        FROM Consultation
                        WHERE PatientNumber = %s
                        AND EmploymentNumber = %s
                        AND ConsultationDate = %s
                        AND startTime = %s
                        AND endTime = %s
                        '''
                    cursor.execute(sql_delete, (patient_number, physician_ID, day, startTime, endTime))
                    flash("Unable to remove consultation.")
        except IntegrityError as e:
            flash(f"Integrity error: {str(e)}", "error") 
        conn.commit()
        return render_template("PatientManagement.html")


# Check the illness of a Patient
@app.route('/check_Illness', methods=['POST'])
def check_illness():
    patient_id = request.form.get('patient_id')

    with conn.cursor() as cursor:
        sql = '''
            SELECT c.ConsultationID, c.ConsultationDate, c.Notes, 
                   i.Name AS IllnessName, i.Description, i.Severity, 
                   p.PatientNumber, p.Name AS PatientName
            FROM Consultation c
            LEFT JOIN Diagnoses d ON c.ConsultationID = d.ConsultationID
            LEFT JOIN Illness i ON d.IllnessCode = i.IllnessCode
            LEFT JOIN Patient p ON c.PatientNumber = p.PatientNumber
            WHERE c.PatientNumber = %s
        '''
        cursor.execute(sql, (patient_id,))
        consultation_data = cursor.fetchall()
    
    return render_template('PatientManagement.html', consultations=consultation_data)

# Assign a diagnosis
@app.route('/assign_diagnosis', methods=['POST'])
def assign_diagnosis():
    consultation_id = request.form['consultation_id']
    illness_code = request.form['illness_code']

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Diagnoses (ConsultationID, IllnessCode)
            VALUES (%s, %s)
        """, (consultation_id, illness_code))
        conn.commit()
        flash("Diagnosis assigned successfully!", "success")

    return redirect(url_for('Patient'))


# Add an illness
@app.route('/add_illness', methods=['POST'])
def add_illness():
    name = request.form.get('Name').strip()
    description = request.form.get('Description').strip()
    severity = request.form.get('Severity')

    if not name or not description or not severity:
        flash("All fields are required.", "danger")
        return redirect(url_for('Patient'))

    with conn.cursor() as cursor:
        # Check for duplicate illness by name only
        cursor.execute("""
            SELECT IllnessCode FROM Illness
            WHERE Name = %s
        """, (name,))
        existing = cursor.fetchone()

        if existing:
            flash("Illness already exists.", "warning")
        else:
            cursor.execute("""
                INSERT INTO Illness (Name, Description, Severity)
                VALUES (%s, %s, %s)
            """, (name, description, severity))
            conn.commit()
            flash("Illness added successfully!", "success")

    return redirect(url_for('Patient'))

# InPatient Route
@app.route('/InPatient')
def InPatient():
    return render_template("InPatient_Management.html")

# Medical Management Page
@app.route('/MedicalManagement')
def MedicalManagement():
    return render_template("MedicalManagement.html")

# Add Staff Functionality
@app.route('/Add_Staff', methods=['GET', 'POST'])
def Add_Staff():
    if request.method == 'POST':
        EmploymentNumber = request.form['DoctorID']
        Name = request.form['Name']
        address = f"{request.form.get('Street', '')} Apt {request.form.get('Apt', '')} {request.form.get('City', '')}, {request.form.get('State', '')} {request.form.get('Zip', '')}"
        TelephoneNumber = request.form['TelephoneNumber']
        SSN = request.form['SSN']
        Gender = request.form['Gender']
        Position = request.form['Position']
        clinicID = request.form['ClinicID']
        action = request.form['action']



        with conn.cursor() as cursor:


            # If action is update, we will update the employee table, delete the current position record if necessary, and insert new position to the respective table
            if action == 'update':
                sql_checkposition = '''
                SELECT Position 
                FROM Employee 
                WHERE EmploymentNumber = %s
                '''
                cursor.execute(sql_checkposition, (EmploymentNumber,))
                oldPosition = cursor.fetchone()

                if oldPosition == None:
                    flash("Employee not found in the database.")
                    return render_template("MedicalManagement.html")
                else:

                    theOldPosition = oldPosition['Position'].lower();
                    sql = '''
                        UPDATE Employee
                        SET Name = %s,
                        Address = %s,
                        TelephoneNumber = %s,
                        SSN = %s,
                        Gender = %s,
                        Position = %s,
                        ClinicID = %s
                        WHERE EmploymentNumber = %s

                        '''

                    cursor.execute(sql, (Name, address, TelephoneNumber, SSN, Gender, Position, clinicID, EmploymentNumber))

                    positionlow = Position.lower()

                    if theOldPosition != positionlow:
    # Remove old position entry if Position has changed
                       if theOldPosition == 'physician':
                          cursor.execute("DELETE FROM Physician WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       elif theOldPosition == 'nurse':
                          cursor.execute("DELETE FROM Nurse WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       elif theOldPosition == 'surgeon':
                          cursor.execute("DELETE FROM Surgeon WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       elif theOldPosition == 'support staff':
                          cursor.execute("DELETE FROM SupportStaff WHERE EmploymentNumber = %s", (EmploymentNumber,))

                    # Upsert (Update or Insert) into the new role-specific table
                    if positionlow == 'physician':
                       Specialty = request.form['Specialty']
                       Salary = request.form['Salary']
                       cursor.execute("SELECT 1 FROM Physician WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       exists = cursor.fetchone()
                       if exists:
                          sql = '''
                             UPDATE Physician
                             SET Specialty = %s, Salary = %s
                             WHERE EmploymentNumber = %s
                          '''
                          cursor.execute(sql, (Specialty, Salary, EmploymentNumber))
                       else:
                          sql = '''
                             INSERT INTO Physician (EmploymentNumber, Specialty, Salary)
                             VALUES (%s, %s, %s)
                          '''
                          cursor.execute(sql, (EmploymentNumber, Specialty, Salary))

                    elif positionlow == 'nurse':
                       YOE = request.form['YOE']
                       Grade = request.form['Grade']
                       Salary = request.form['Salary']
                       cursor.execute("SELECT 1 FROM Nurse WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       exists = cursor.fetchone()
                       if exists:
                          sql = '''
                             UPDATE Nurse
                             SET YearsOfExperience = %s, Grade = %s, Salary = %s
                             WHERE EmploymentNumber = %s
                          '''
                          cursor.execute(sql, (YOE, Grade, Salary, EmploymentNumber))
                       else:
                          sql = '''
                             INSERT INTO Nurse (EmploymentNumber, YearsOfExperience, Grade, Salary)
                             VALUES (%s, %s, %s, %s)
                          '''
                          cursor.execute(sql, (EmploymentNumber, YOE, Grade, Salary))

                    elif positionlow == 'surgeon':
                       Specialty = request.form['Specialty']
                       Contract = request.form['Contract']
                       cursor.execute("SELECT 1 FROM Surgeon WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       exists = cursor.fetchone()
                       if exists:
                          sql = '''
                             UPDATE Surgeon
                             SET Specialty = %s, Contract = %s
                             WHERE EmploymentNumber = %s
                          '''
                          cursor.execute(sql, (Specialty, Contract, EmploymentNumber))
                       else:
                          sql = '''
                             INSERT INTO Surgeon (EmploymentNumber, Specialty, Contract)
                             VALUES (%s, %s, %s)
                          '''
                          cursor.execute(sql, (EmploymentNumber, Specialty, Contract))

                    elif positionlow == 'support staff':
                       Salary = request.form['Salary']
                       cursor.execute("SELECT 1 FROM SupportStaff WHERE EmploymentNumber = %s", (EmploymentNumber,))
                       exists = cursor.fetchone()
                       if exists:
                          sql = '''
                             UPDATE SupportStaff
                             SET Salary = %s
                             WHERE EmploymentNumber = %s
                          '''
                          cursor.execute(sql, (Salary, EmploymentNumber))
                       else:
                          sql = '''
                             INSERT INTO SupportStaff (EmploymentNumber, Salary)
                             VALUES (%s, %s)
                          '''
                          cursor.execute(sql, (EmploymentNumber, Salary))          
            
            # If action is to submit, add a new employee record with assigned Employment Number to respective table
            elif action == 'submit':
                sql = '''
                    INSERT INTO Employee (Name, Address, TelephoneNumber, SSN, Gender, Position, ClinicID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(sql, (Name, address, TelephoneNumber, SSN, Gender, Position, clinicID))

                new_empno = cursor.lastrowid
                positionlow = Position.lower()

                if positionlow == "physician":
                    Specialty = request.form['Specialty']
                    Salary = request.form['Salary']
                    sql_phys = '''
                        INSERT INTO Physician (EmploymentNumber, Specialty, Salary)
                        VALUES (%s, %s, %s)
                    '''
                    cursor.execute(sql_phys, (new_empno, Specialty, Salary))

                elif positionlow == 'nurse':
                    Salary = request.form['Salary']
                    YOE = request.form['YOE']
                    Grade = request.form['Grade']
                    sql_nurse = '''
                        INSERT INTO Nurse (EmploymentNumber, YearsOfExperience, Grade, Salary)
                        VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(sql_nurse, (new_empno, YOE, Grade, Salary))

                elif positionlow == "surgeon":
                    Specialty = request.form['Specialty']
                    Contract = request.form['Contract']
                    sql_surgeon = '''
                        INSERT INTO Surgeon (EmploymentNumber, Specialty, Contract)
                        VALUES (%s, %s, %s)
                    '''
                    cursor.execute(sql_surgeon, (new_empno, Specialty, Contract))

                elif positionlow == "support staff":
                    Salary = request.form['Salary']
                    sql_support_staff = '''
                        INSERT INTO SupportStaff (EmploymentNumber, Salary)
                        VALUES (%s, %s)
                    '''
                    cursor.execute(sql_support_staff, (new_empno, Salary))

            conn.commit()
            if action == 'update':
               flash("Staff updated successfully!", "success")
            else:
               flash("Staff added successfully!", "success")
    return render_template("MedicalManagement.html")

# Removing Staff Functionality
@app.route('/Remove_Staff', methods=['POST'])
def RemoveStaff():
    Emp_No = request.form['DoctorID']

    with conn.cursor() as cursor:
        # Get position of employee
        cursor.execute("SELECT Position FROM Employee WHERE EmploymentNumber = %s", (Emp_No,))
        result = cursor.fetchone()

        if result is None:
            flash("Staff member not found.")
            return render_template("MedicalManagement.html")

        position = result['Position'].lower()

        # Delete dependent entries based on position
        if position == 'physician':
            cursor.execute("DELETE FROM Consultation WHERE EmploymentNumber = %s", (Emp_No,))
            cursor.execute("DELETE FROM Surgery WHERE SurgeonEmploymentNumber = %s", (Emp_No,))
            cursor.execute("DELETE FROM Surgery WHERE PatientNumber IN (SELECT PatientNumber FROM Patient WHERE EmploymentNumber = %s)", (Emp_No,))
            cursor.execute("DELETE FROM Patient WHERE EmploymentNumber = %s", (Emp_No,))
            cursor.execute("DELETE FROM Physician WHERE EmploymentNumber = %s", (Emp_No,))

        elif position == 'nurse':
            cursor.execute("DELETE FROM InPatient WHERE EmploymentNumber = %s", (Emp_No,))
            cursor.execute("DELETE FROM Nurse WHERE EmploymentNumber = %s", (Emp_No,))

        elif position == 'surgeon':
            cursor.execute("DELETE FROM Surgery WHERE SurgeonEmploymentNumber = %s", (Emp_No,))
            cursor.execute("DELETE FROM Surgeon WHERE EmploymentNumber = %s", (Emp_No,))

        elif position == 'support staff':
            cursor.execute("DELETE FROM SupportStaff WHERE EmploymentNumber = %s", (Emp_No,))

        # Always attempt to clean up any surgeries/patients linked to this Emp_No
        cursor.execute("DELETE FROM Surgery WHERE PatientNumber IN (SELECT PatientNumber FROM Patient WHERE EmploymentNumber = %s)", (Emp_No,))
        cursor.execute("DELETE FROM Patient WHERE EmploymentNumber = %s", (Emp_No,))

        # Finally delete from Employee table
        cursor.execute("DELETE FROM Employee WHERE EmploymentNumber = %s", (Emp_No,))

    conn.commit()
    flash("Staff member and related records removed successfully.")
    return render_template("MedicalManagement.html")

# Schedule Shift Route
@app.route('/Schedule_Shift', methods=['POST'])
def ScheduleShift():
    ClinicID = request.form['ClinicID']
    DoctorID = request.form['DoctorID']
    Dayofweek = request.form['Day']
    BeginTime = request.form['BeginTime']
    EndTime = request.form['EndTime']
    action = request.form['action']
    with conn.cursor() as cursor:
        try:

            # If button is submit, Insert new Shift
            if action == "submit":
                # Insert shift into 'shift' table if it doesn't exist
                cursor.execute("""
                    INSERT IGNORE INTO shift (ClinicID, ShiftDate, BeginTime, EndTime)
                    VALUES (%s, %s, %s, %s)
                """, (ClinicID, Dayofweek, BeginTime, EndTime))

                # Check for scheduling conflict
                cursor.execute('''
                    SELECT * FROM Schedule
                    WHERE EmploymentNumber = %s AND ScheduleDate = %s
                    AND ((BeginTime <= %s AND EndTime > %s)
                    OR (BeginTime < %s AND EndTime >= %s)
                    OR (BeginTime >= %s AND EndTime <= %s))
                ''', (DoctorID, Dayofweek, EndTime, BeginTime, BeginTime, EndTime, BeginTime, EndTime))

                if cursor.fetchone():
                    flash("Scheduling conflict - time slot unavailable.", "error")
                else:
                    cursor.execute('''
                        INSERT INTO Schedule (EmploymentNumber, ClinicID, ScheduleDate, BeginTime, EndTime)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (DoctorID, ClinicID, Dayofweek, BeginTime, EndTime))
                    flash("Shift scheduled successfully!", "success")
            elif action == "remove":
                sql_delete = '''
                    DELETE
                    FROM Schedule
                    WHERE EmploymentNumber = %s
                    AND ScheduleDate = %s
                    AND BeginTime = %s
                    AND EndTime = %s
                    '''
                cursor.execute(sql_delete, (DoctorID, Dayofweek, BeginTime, EndTime))
            conn.commit()

        except IntegrityError as e:
            flash(f"Integrity error: {str(e)}", "error")

    return redirect(url_for('Medical'))

# Checking Room Availability Functionality
@app.route('/Room_Availability', methods=['POST'])
def Room_Availability():
    room_type_filter = request.form.get("room_type")
    room_count = 0

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT r.RoomNumber) AS AvailableCount
            FROM room r
            JOIN bed b ON r.RoomNumber = b.RoomNumber
            WHERE b.Availability = 'Available'
              AND r.RoomType = %s
        """, (room_type_filter,))
        result = cursor.fetchone()
        if result:
            room_count = result['AvailableCount']

    flash(f"Found {room_count} available {room_type_filter} room(s).", "success")
    return redirect(url_for('In_Patient'))

# Adding a clinic Functionality
@app.route('/Add_Clinic', methods=['POST'])
def add_clinic():
    name = request.form['clinic_name']
    address = request.form['clinic_address']
    with conn.cursor() as cursor:
        sql = '''
            INSERT INTO Clinic (Name, Address)
            VALUES (%s, %s)
        '''
        cursor.execute(sql, (name, address))
        conn.commit()
    flash('Clinic added successfully!', 'success')
    return render_template("MedicalManagement.html")


# Assign Patients to a Room Functionality
@app.route('/AssignPatientRooms', methods=['POST'])
def assign_patient_rooms():
    patient_id = request.form.get('patient_number')
    room_number = request.form.get('RoomNumber')
    bed_id = request.form.get('BedID')
    wing = request.form.get('Wing') or None
    unit = request.form.get('NursingUnit') or None
    admission_date = request.form.get('admission_date')
    nurse_id = request.form.get('NurseID')

    if not patient_id or not room_number or not bed_id or not admission_date or not nurse_id:
        flash("All required fields must be filled to assign a patient.", "error")
        return redirect(url_for('In_Patient'))

    conn.ping(reconnect=True)  # ensure connection is active
    with conn.cursor() as cursor:
        # Check if bed is available
        cursor.execute("SELECT * FROM bed WHERE BedID = %s AND Availability = 'Available'", (bed_id,))
        bed = cursor.fetchone()

        if not bed:
            flash("The selected bed is either unavailable or does not exist.", "error")
            return redirect(url_for('In_Patient'))

        # Prevent multiple patients in the same room and bed
        cursor.execute("SELECT * FROM InPatient WHERE PatientNumber = %s", (patient_id,))         
        already_assigned = cursor.fetchone()

        if already_assigned:
           flash("This patient is already assigned to a room and bed.", "error")
           return redirect(url_for('In_Patient'))

        # All clear: assign patient
        cursor.execute("""
            INSERT INTO InPatient (PatientNumber, RoomNumber, BedID, Wing, NursingUnit, DateOfAdmission, EmploymentNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, room_number, bed_id, wing, unit, admission_date, nurse_id))

        cursor.execute("UPDATE bed SET Availability = 'Occupied' WHERE BedID = %s", (bed_id,))
        conn.commit()

        flash("Patient assigned successfully!", "success")
        return redirect(url_for('In_Patient'))

# Remove Patient Rooms Functionality
@app.route('/RemovePatientRooms', methods=['POST'])
def remove_patient_from_room():
    patient_id = request.form.get('patient_number')

    if not patient_id:
        flash("No patient selected for removal.", "error")
        return redirect(url_for('In_Patient'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT BedID FROM InPatient WHERE PatientNumber = %s", (patient_id,))
        result = cursor.fetchone()

        if result:
            bed_id = result['BedID']
            cursor.execute("DELETE FROM InPatient WHERE PatientNumber = %s", (patient_id,))
            cursor.execute("UPDATE bed SET Availability = 'Available' WHERE BedID = %s", (bed_id,))
            conn.commit()
            flash("Patient removed from room/bed successfully.", "success")
        else:
            flash("No assignment found for the selected patient.", "warning")

    return redirect(url_for('In_Patient'))

# Assign/Remove doctor to a patient Functionality
@app.route('/ManageDoctors', methods=['POST'])
def manage_doctors():
    patient_id = request.form.get('patient_number')
    doctor_id = request.form.get('DoctorID')
    action = request.form.get('action')

    with conn.cursor() as cursor:
        if action == "assign":
            sql = '''
                UPDATE Patient
                SET EmploymentNumber = %s
                WHERE PatientNumber = %s
            '''
            cursor.execute(sql, (doctor_id, patient_id))
            flash("Doctor assigned to patient successfully.", "success")

        elif action == "remove":
            sql = '''
                UPDATE Patient
                SET EmploymentNumber = NULL
                WHERE PatientNumber = %s AND EmploymentNumber = %s
            '''
            cursor.execute(sql, (patient_id, doctor_id))
            flash("Doctor removed from patient successfully.", "success")

        conn.commit()

    return redirect(url_for('In_Patient'))

# Diagnose Illness Functionality
@app.route('/DiagnoseIllness', methods=['POST'])
def diagnose_illness():
    consultation_id = request.form.get('consultation_id')
    illness_name = request.form.get('illness_name').strip()
    description = request.form.get('description').strip()
    severity = request.form.get('severity')

    with conn.cursor() as cursor:
        # Check if an illness with the same name AND description already exists
        cursor.execute("""
            SELECT IllnessCode FROM Illness
            WHERE Name = %s AND Description = %s
        """, (illness_name, description))
        existing_illness = cursor.fetchone()

        if existing_illness:
            illness_code = existing_illness['IllnessCode']
        else:
            # Insert new illness entry
            cursor.execute("""
                INSERT INTO Illness (Name, Description, Severity)
                VALUES (%s, %s, %s)
            """, (illness_name, description, severity))
            illness_code = cursor.lastrowid

        # Insert diagnosis (if not already diagnosed)
        cursor.execute("""
            SELECT 1 FROM Diagnoses WHERE ConsultationID = %s AND IllnessCode = %s
        """, (consultation_id, illness_code))
        already_exists = cursor.fetchone()

        if not already_exists:
            cursor.execute("""
                INSERT INTO Diagnoses (ConsultationID, IllnessCode)
                VALUES (%s, %s)
            """, (consultation_id, illness_code))
            conn.commit()
            flash("Illness diagnosed and recorded successfully!", "success")
        else:
            flash("This diagnosis already exists for the consultation.", "warning")

    return redirect(url_for('Patient'))

# Assign/Remove a nurse to a patient Functionality
@app.route('/ManageNurses', methods=['POST'])
def manage_nurses():
    patient_id = request.form.get('patient_number')
    nurse_id = request.form.get('NurseID')
    action = request.form.get('action')

    with conn.cursor() as cursor:
        if action == "assign":
            sql = '''
                UPDATE InPatient
                SET EmploymentNumber = %s
                WHERE PatientNumber = %s
            '''
            cursor.execute(sql, (nurse_id, patient_id))
            flash("Nurse assigned to patient successfully.", "success")

        elif action == "remove":
            sql = '''
                UPDATE InPatient
                SET EmploymentNumber = NULL
                WHERE PatientNumber = %s AND EmploymentNumber = %s
            '''
            cursor.execute(sql, (patient_id, nurse_id))
            flash("Nurse removed from patient successfully.", "success")

        conn.commit()

    return redirect(url_for('In_Patient'))


# View Surgeries via room
@app.route('/view_surgeries_by_room', methods=['POST'])
def view_surgeries_by_room():
    surgery_date = request.form['surgery_date']

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT s.SurgeryID, s.SurgeryDate, s.StartTime, s.EndTime,
                   s.PatientNumber, s.SurgeonEmploymentNumber,
                   s.TheaterID, s.SurgeryCode, e.Name AS SurgeonName
            FROM Surgery s
            JOIN employee e ON s.SurgeonEmploymentNumber = e.EmploymentNumber
            WHERE s.SurgeryDate = %s
        """, (surgery_date,))
        surgeries = cursor.fetchall()

        cursor.execute("SELECT * FROM OperationTheater")
        operation_theaters = cursor.fetchall()

        cursor.execute("SELECT * FROM SurgeryType")
        surgery_types = cursor.fetchall()

    surgery_events = []
    for row in surgeries:
        if row['SurgeryDate'] and row['StartTime'] and row['EndTime']:
            surgery_events.append({
                "title": f"Surgery - {row['SurgeonName']}",
                "start": f"{row['SurgeryDate']}T{row['StartTime']}",
                "end": f"{row['SurgeryDate']}T{row['EndTime']}"
            })

    return render_template(
        "InPatient_Management.html",
        surgeries_by_room=surgeries,
        surgery_events=surgery_events,
        operation_theaters=operation_theaters,
        surgery_types=surgery_types
    )


# View Surgeries by Surgeon
@app.route('/view_surgeries_by_surgeon', methods=['POST'])
def view_surgeries_by_surgeon():
    surgery_date = request.form.get('surgery_date')

    with conn.cursor() as cursor:
        cursor.execute(''' 
            SELECT s.SurgeryID, s.SurgeryDate, s.SurgeonEmploymentNumber, e.Name AS SurgeonName, 
                   s.StartTime, s.EndTime, p.Name AS PatientName, r.Location AS RoomLocation
            FROM Surgery s
            JOIN Surgeon sr ON s.SurgeonEmploymentNumber = sr.EmploymentNumber
            JOIN Employee e ON sr.EmploymentNumber = e.EmploymentNumber
            JOIN Patient p ON s.PatientNumber = p.PatientNumber
            JOIN OperationTheater r ON s.TheaterID = r.TheaterID
            WHERE s.SurgeryDate = %s
        ''', (surgery_date,))
        
        surgeries = cursor.fetchall()
 
        cursor.execute("SELECT * FROM OperationTheater")
        operation_theaters = cursor.fetchall()

        cursor.execute("SELECT * FROM SurgeryType")
        surgery_types = cursor.fetchall()
    
    surgery_events = []
    for row in surgeries:
      if row['SurgeryDate'] and row['StartTime'] and row['EndTime']:
        surgery_events.append({
            "title": f"Surgery - {row['SurgeonName']}",
            "start": f"{row['SurgeryDate']}T{row['StartTime']}",
            "end": f"{row['SurgeryDate']}T{row['EndTime']}"
        })

    return render_template('InPatient_Management.html', 
        surgeries_by_surgeon=surgeries,
        surgery_events=surgery_events,
        operation_theaters=operation_theaters,
        surgery_types=surgery_types)

# Book Surgery Functionality
@app.route('/book_surgery', methods=['POST'])
def book_surgery():
    print("Form Data Received:", request.form)

    surgery_date = request.form.get('surgery_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    patient_number = request.form.get('patient_number')
    surgeon_id = request.form.get('DoctorID')
    theater_id = request.form.get('theater_id')
    surgery_code = request.form.get('surgery_code')

    print("Booking surgery with:")
    print("Date:", surgery_date)
    print("Start Time:", start_time)
    print("End Time:", end_time)
    print("Patient:", patient_number)
    print("Surgeon:", surgeon_id)
    print("Theater:", theater_id)
    print("Code:", surgery_code)

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT * FROM Surgery
                WHERE PatientNumber = %s
                  AND SurgeryDate = %s
                  AND (
                      (%s >= StartTime AND %s < EndTime)
                      OR (%s > StartTime AND %s <= EndTime)
                      OR (%s <= StartTime AND %s >= EndTime)
                  )
            ''', (
                patient_number, surgery_date,
                start_time, start_time,
                end_time, end_time,
                start_time, end_time
            ))

            conflict = cursor.fetchone()
            if conflict:
                flash("This patient already has a surgery scheduled that overlaps with the selected time.", "danger")
                return redirect(url_for('In_Patient'))

            cursor.execute('''
                SELECT * FROM Surgery
                WHERE SurgeonEmploymentNumber = %s
                  AND SurgeryDate = %s
                  AND (
                      (%s >= StartTime AND %s < EndTime)
                      OR (%s > StartTime AND %s <= EndTime)
                      OR (%s <= StartTime AND %s >= EndTime)
                  )
            ''', (
                surgeon_id, surgery_date,
                start_time, start_time,
                end_time, end_time,
                start_time, end_time
            ))

            surgeon_conflict = cursor.fetchone()
            if surgeon_conflict:
                flash("This surgeon is already scheduled for another surgery during this time.", "danger")
                return redirect(url_for('In_Patient'))

            sql = '''
                INSERT INTO Surgery (SurgeryDate, StartTime, EndTime, PatientNumber,
                                     SurgeonEmploymentNumber, TheaterID, SurgeryCode)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, (
                surgery_date, start_time, end_time, patient_number,
                surgeon_id, theater_id, surgery_code
            ))
            conn.commit()
            flash("Surgery successfully booked!", "success")

    except Exception as e:
        flash(f"Error scheduling surgery: {str(e)}", "danger")
        print("Error inserting surgery:", e)

    return redirect(url_for('In_Patient'))

# View Surgeries By Patient Functionality
@app.route('/view_surgeries_by_patient', methods=['GET'])
def view_surgeries_by_patient():
    patient_number = request.args.get('patient_number')

    with conn.cursor() as cursor:
        sql = '''
            SELECT s.SurgeryID, s.SurgeryDate, s.StartTime, s.EndTime,
                   s.TheaterID AS TheaterLocation,
                   e.Name AS SurgeonName,
                   s.SurgeryCode
            FROM Surgery s
            JOIN Employee e ON s.SurgeonEmploymentNumber = e.EmploymentNumber
            WHERE s.PatientNumber = %s
        '''
        cursor.execute(sql, (patient_number,))
        surgeries_by_patient = cursor.fetchall()
 
        cursor.execute("SELECT * FROM OperationTheater")
        operation_theaters = cursor.fetchall()

        cursor.execute("SELECT * FROM SurgeryType")
        surgery_types = cursor.fetchall()

    surgery_events = []
    for row in surgeries_by_patient:
      if row['SurgeryDate'] and row['StartTime'] and row['EndTime']:
        surgery_events.append({
            "title": f"Surgery - {row['SurgeonName']}",
            "start": f"{row['SurgeryDate']}T{row['StartTime']}",
            "end": f"{row['SurgeryDate']}T{row['EndTime']}"
        })

    flash(f"Viewing surgeries for patient number {patient_number}", "success")

    return render_template('InPatient_Management.html',
                           surgeries_by_patient=surgeries_by_patient,
                           surgery_events=surgery_events,
                           operation_theaters=operation_theaters,
                           surgery_types=surgery_types)
    

# Search for Staff Member Functionality
@app.route('/search_staff', methods=['GET'])
def search_staff():
    query = request.args.get('query')

    with conn.cursor() as cursor:
        # Search matching employees
        cursor.execute("""
            SELECT * FROM employee
            WHERE Name LIKE %s
        """, (f"%{query}%",))
        search_results = cursor.fetchall()

        # Fetch all employees for dropdown menus
        cursor.execute("SELECT * FROM employee")
        employees = cursor.fetchall()

        # Fetch all clinics for dropdown menus
        cursor.execute("SELECT * FROM clinic")
        clinics = cursor.fetchall()

        # Fetch all scheduled shifts
        cursor.execute("""
            SELECT s.ScheduleDate, s.BeginTime, s.EndTime, e.Name AS FullName
            FROM schedule s
            JOIN employee e ON s.EmploymentNumber = e.EmploymentNumber
        """)
        schedule_data = cursor.fetchall()

    # Build the shift_events list for the calendar
    shift_events = []
    seen = set()

    for row in schedule_data:
        key = (
            str(row['ScheduleDate']),
            str(row['BeginTime']),
            str(row['EndTime']),
            row['FullName']
        )
        if key in seen:
            continue
        seen.add(key)

        shift_events.append({
            "title": f"Shift: {row['FullName']}",
            "start": f"{row['ScheduleDate']}T{row['BeginTime']}",
            "end": f"{row['ScheduleDate']}T{row['EndTime']}"
        })

    # Optional: debug output
    print("Final shift_events:")
    print(type(shift_events))
    if shift_events:
        print(type(shift_events[0]))
        print(shift_events[0])

    return render_template(
        "MedicalManagement.html",
        employees=employees,
        clinics=clinics,
        searchResults=search_results,
        shift_events=shift_events
    )

# Searching the patients Functionality
@app.route('/search_patient', methods=['GET'])
def SearchPatient():
    namequery = request.args.get('query')


    if not namequery:
        flash("Please enter in a Patient's name.")
        return render_template("MedicalManagement.html")
    
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:

        sql_query = '''
        SELECT * FROM Patient
        WHERE Name LIKE %s
                    '''
        cursor.execute(sql_query, (namequery,))

        searchResults = cursor.fetchall()
            

        return render_template('PatientManagement.html', searchResults=searchResults)

# Retrieving the Rooms Availability
@app.route("/get_rooms/<room_type>")
def get_rooms(room_type):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT r.RoomNumber
            FROM room r
            JOIN bed b ON r.RoomNumber = b.RoomNumber
            WHERE r.RoomType = %s AND b.Availability = 'Available'
        """, (room_type,))
        rooms = cursor.fetchall()
    return jsonify(rooms)


# Retrieving Bed Availability
@app.route("/get_beds/<room_number>")
def get_beds(room_number):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT BedID, BedLabel
            FROM bed
            WHERE RoomNumber = %s AND Availability = 'Available'
        """, (room_number,))
        beds = cursor.fetchall()
    return jsonify(beds)

# Delete a Surgery Functionality
@app.route('/delete_surgery', methods=['POST'])
def delete_surgery():
    surgery_id = request.form['surgery_id']
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Surgery WHERE SurgeryID = %s", (surgery_id,))
            conn.commit()
        flash("Surgery deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting surgery: {str(e)}", "danger")
    return redirect(url_for('In_Patient'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() == 'true')
