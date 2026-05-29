# ITUM Medical Centre

A **Flask-based medical clinic management system** for the Institute of Technology University of Moratuwa (ITUM). Students can register, book appointments with doctors, manage their appointments, and leave feedback. Staff have an admin dashboard for oversight.

## Features

- **User Registration & Login** — Session-based auth with password hashing
- **Appointment Booking** — Choose from doctors, pick a date/time, with double-booking prevention
- **Appointment Management** — View upcoming/past appointments, cancel if needed
- **Feedback System** — Rate doctors (1–5) with comments; view average ratings
- **Admin Dashboard** — Stats, user management (search), appointment list with filters
- **Role-Based Access** — Student, Doctor, and Admin roles with different permissions

## Tech Stack

- **Backend:** Python Flask (modular Blueprints)
- **Database:** SQLite (auto-seeded with starter data)
- **Frontend:** Bootstrap 5, custom CSS, Jinja2 templates
- **Testing:** pytest (900+ line test suite)

## Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/dulaedu0912/Itum_medical_centre
   cd itum_medical_centre
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open** http://127.0.0.1:5000

## Pre-Seeded Accounts

| Name | Email | Password | Role |
|---|---|---|---|
| System Admin | admin@itum.lk | admin123 | admin |
| Test Student | student@itum.lk | student123 | student |
| Dr. Priya Mendis | priya@itum.lk | doctor123 | doctor |
| Dr. Kasun Silva | kasun@itum.lk | doctor123 | doctor |
| Dr. Nimal Perera | nimal@itum.lk | doctor123 | doctor |

## Project Structure

```
itum-medical-final/
├── app.py                  # Entry point
├── db.py                   # Database setup & seeding
├── requirements.txt        # Dependencies
├── routes/                 # Flask Blueprints
│   ├── register.py
│   ├── auth.py
│   ├── profile.py
│   ├── book.py
│   ├── appointments.py
│   ├── feedback.py
│   └── admin.py
├── templates/              # Jinja2 HTML templates
├── static/
│   └── style.css           # Custom styles
└── test_all.py             # Test suite
```

## Running Tests

```bash
pytest test_all.py -v
```
