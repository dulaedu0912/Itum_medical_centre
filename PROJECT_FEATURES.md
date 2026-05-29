# ITUM Medical Centre — Project Overview

A **Flask-based medical clinic management web application** for the Institute of Technology University of Moratuwa (ITUM). Uses **SQLite** as the database and **Bootstrap 5** for the UI.

---

## Core Features

| Feature | Description | Routes |
|---|---|---|
| **User Registration** | Students can create accounts with name, email, password, phone. Validates email format, password length, password match, and duplicate emails. Auto-logs in after registration. AJAX endpoint to check email availability. | `POST /auth/register`, `GET /auth/check-email` |
| **Login / Logout** | Email + password authentication using Werkzeug password hashing. Session-based. Redirects already-logged-in users away from login page. | `POST /auth/login`, `GET /auth/logout` |
| **Profile Management** | View profile, edit name/email/phone (with duplicate email check), change password (requires old password, validates new password length & confirmation). | `GET/POST /auth/profile`, `/profile/edit`, `/profile/change-password` |
| **Book Appointments** | Students can book with 3 seeded doctors. Validates: doctor selection, date not in past, time required, no double-booking (same doctor/date/time). Shows confirmation page. | `GET/POST /appointments/book` |
| **View Appointments** | Students see their appointments with filters: upcoming (future, non-cancelled), past (past dates or cancelled), or all. | `GET /appointments/` |
| **Cancel Appointments** | Students can cancel their own appointments. Ownership verified — cannot cancel another student's appointment. Already-cancelled appointments handled gracefully. | `GET/POST /appointments/cancel/<id>` |
| **Feedback System** | Students rate doctors (1-5) with comments. Validates: doctor selected, rating in range, comment required. View own feedback history plus average ratings per doctor across all students. | `GET/POST /feedback/give`, `GET /feedback/` |
| **Admin Dashboard** | Staff-only (admin/doctor). Shows stats: total users, doctors, appointments, counts by status (pending/completed/cancelled), and a full appointment list with student & doctor names. | `GET /admin/` |
| **Admin — User Management** | Staff-only. Lists all users with search by name or email. | `GET /admin/users` |
| **Admin — Appointment Management** | Staff-only. Lists all appointments with status filter (all/pending/completed/cancelled). | `GET /admin/appointments` |

## Role-Based Access

| Role | Capabilities |
|---|---|
| **Student** | Register, manage profile, book/view/cancel appointments, give feedback |
| **Doctor** | Everything a student can do + access admin dashboard (view-only) |
| **Admin** | Full access: dashboard, user list/search, appointment list/filter |

## Pre-Seeded Accounts (auto-created on first run)

| Name | Email | Password | Role |
|---|---|---|---|
| System Admin | admin@itum.lk | admin123 | admin |
| Test Student | student@itum.lk | student123 | student |
| Dr. Priya Mendis | priya@itum.lk | doctor123 | doctor (General Medicine) |
| Dr. Kasun Silva | kasun@itum.lk | doctor123 | doctor (General Medicine) |
| Dr. Nimal Perera | nimal@itum.lk | doctor123 | doctor (Ophthalmology) |

## Database Schema (4 tables)

- **users** — `id`, `full_name`, `email`, `password_hash`, `phone`, `role` (student/admin/doctor), `created_at`
- **doctors** — `id`, `name`, `specialization`, `department`, `consultation_fee`, `created_at`
- **appointments** — `id`, `student_id`, `doctor_id`, `appointment_date`, `appointment_time`, `reason`, `status` (pending/completed/cancelled), `created_at`
- **feedback** — `id`, `student_id`, `doctor_id`, `appointment_id`, `rating` (1-5), `comment`, `created_at`

## Technical Stack

- **Backend:** Python Flask (single `app.py` entrypoint with modular Blueprints in `routes/`)
- **Database:** SQLite (`clinic.db`) with 4 tables and auto-seeded starter data
- **Frontend:** Bootstrap 5 (CDN), custom CSS (`static/style.css`), 16 Jinja2 templates
- **Testing:** pytest (944-line comprehensive test suite covering all routes, validation, edge cases, and a full end-to-end user journey)
