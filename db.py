import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'clinic.db')


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Create all 4 tables

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            department TEXT,
            consultation_fee REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    """)
    conn.commit()

    # Seed data (only runs once — when doctors table is empty)
    count = conn.execute("SELECT COUNT(*) as c FROM doctors").fetchone()['c']
    if count == 0:
        doctors = [
            {"name": "Dr. Priya Mendis", "specialization": "General Practitioner",
             "department": "General Medicine", "consultation_fee": 500},
            {"name": "Dr. Kasun Silva", "specialization": "General Practitioner",
             "department": "General Medicine", "consultation_fee": 500},
            {"name": "Dr. Nimal Perera", "specialization": "Eye Specialist",
             "department": "Ophthalmology", "consultation_fee": 1000},
        ]
        for doc in doctors:
            conn.execute(
                "INSERT INTO doctors (name, specialization, department, consultation_fee) VALUES (?, ?, ?, ?)",
                (doc["name"], doc["specialization"], doc["department"], doc["consultation_fee"])
            )

        admin_hash = generate_password_hash("admin123")
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
            ("System Admin", "admin@itum.lk", admin_hash, "0112345678", "admin")
        )

        doctor_users = [
            ("Dr. Priya Mendis", "priya@itum.lk", "doctor123"),
            ("Dr. Kasun Silva", "kasun@itum.lk", "doctor123"),
            ("Dr. Nimal Perera", "nimal@itum.lk", "doctor123"),
        ]
        for name, email, pw in doctor_users:
            doc_hash = generate_password_hash(pw)
            conn.execute(
                "INSERT INTO users (full_name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
                (name, email, doc_hash, "0112345678", "doctor")
            )

        student_hash = generate_password_hash("student123")
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
            ("Test Student", "student@itum.lk", student_hash, "0771234567", "student")
        )

        conn.commit()
        print("Database seeded with doctors, admin, doctor logins, and test student.")

    conn.close()
    print("Database initialized successfully.")