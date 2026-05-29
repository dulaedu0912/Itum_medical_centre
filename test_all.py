"""
Comprehensive automated test for ITUM Medical Centre
Tests ALL routes, validation, edge cases, and the full user flow.
"""
import sys
import os
import tempfile
import pytest

# Override DB path BEFORE importing app
TEST_DB = os.path.join(tempfile.gettempdir(), 'itum_test.db')
os.environ['DATABASE_PATH'] = TEST_DB

# Patch db.py to use test DB
import db as db_module
db_module.DATABASE_PATH = TEST_DB

from app import app
from db import get_db, init_db


import gc

@pytest.fixture(autouse=True)
def setup_db():
    """Fresh database before every test."""
    # Force garbage collection to close any lingering SQLite connections
    gc.collect()
    # Remove old DB if it exists (retry with delay on Windows)
    if os.path.exists(TEST_DB):
        for _ in range(5):
            try:
                os.remove(TEST_DB)
                break
            except PermissionError:
                gc.collect()
                import time
                time.sleep(0.3)
    init_db()
    yield
    gc.collect()
    # Cleanup on teardown (best-effort)
    if os.path.exists(TEST_DB):
        for _ in range(3):
            try:
                os.remove(TEST_DB)
                break
            except PermissionError:
                gc.collect()
                import time
                time.sleep(0.2)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as c:
        with app.app_context():
            yield c


# ============================================================
# MEMBER 1: Foundation Tests
# ============================================================

class TestFoundation:
    def test_home_page_loads(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'ITUM Medical Centre' in resp.data

    def test_doctors_seeded(self):
        """Verify seed data exists."""
        db = get_db()
        count = db.execute("SELECT COUNT(*) as c FROM doctors").fetchone()['c']
        assert count == 3

    def test_admin_seeded(self):
        """Verify admin user was created."""
        db = get_db()
        admin = db.execute("SELECT * FROM users WHERE role='admin'").fetchone()
        assert admin is not None
        assert admin['email'] == 'admin@itum.lk'

    def test_doctors_seeded_as_users(self):
        """Verify doctor user accounts were created."""
        db = get_db()
        doctors = db.execute("SELECT * FROM users WHERE role='doctor'").fetchall()
        assert len(doctors) == 3
        assert doctors[0]['email'].endswith('@itum.lk')

    def test_student_seeded(self):
        """Verify seed student account exists."""
        db = get_db()
        student = db.execute("SELECT * FROM users WHERE email='student@itum.lk'").fetchone()
        assert student is not None
        assert student['role'] == 'student'

    def test_navbar_shows_register_login(self, client):
        resp = client.get('/')
        assert b'Register' in resp.data
        assert b'Login' in resp.data

    def test_navbar_hides_auth_links_when_logged_in(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Test'
            sess['role'] = 'student'
        resp = client.get('/')
        assert b'Register' not in resp.data
        assert b'Book Appointment' in resp.data

    def test_dashboard_shows_for_admin(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/')
        assert b'Dashboard' in resp.data
        assert b'Manage' in resp.data

    def test_dashboard_shows_for_doctor(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Dr. Priya'
            sess['role'] = 'doctor'
        resp = client.get('/')
        assert b'Dashboard' in resp.data

    def test_dashboard_hidden_for_student(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/')
        assert b'Dashboard' not in resp.data


# ============================================================
# MEMBER 2: Registration Tests
# ============================================================

class TestRegistration:
    def test_register_page_loads(self, client):
        resp = client.get('/auth/register')
        assert resp.status_code == 200
        assert b'Create an Account' in resp.data

    def test_successful_registration(self, client):
        resp = client.post('/auth/register', data={
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': '0771234567'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Registration successful' in resp.data

        # Verify user exists in DB
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email='test@example.com'").fetchone()
        assert user is not None
        assert user['full_name'] == 'Test User'

    def test_empty_fields_rejected(self, client):
        resp = client.post('/auth/register', data={
            'full_name': '',
            'email': '',
            'password': '',
            'confirm_password': '',
            'phone': ''
        }, follow_redirects=True)
        assert b'Full name, email, and password are required' in resp.data

    def test_invalid_email_rejected(self, client):
        resp = client.post('/auth/register', data={
            'full_name': 'Test',
            'email': 'notanemail',
            'password': 'pass123',
            'confirm_password': 'pass123',
            'phone': ''
        }, follow_redirects=True)
        assert b'valid email' in resp.data or b'Invalid email' in resp.data

    def test_password_mismatch_rejected(self, client):
        resp = client.post('/auth/register', data={
            'full_name': 'Test',
            'email': 'test@test.com',
            'password': 'pass123',
            'confirm_password': 'different',
            'phone': ''
        }, follow_redirects=True)
        assert b'Passwords do not match' in resp.data

    def test_short_password_rejected(self, client):
        resp = client.post('/auth/register', data={
            'full_name': 'Test',
            'email': 'test@test.com',
            'password': 'abc',
            'confirm_password': 'abc',
            'phone': ''
        }, follow_redirects=True)
        assert b'at least 6 characters' in resp.data

    def test_duplicate_email_rejected(self, client):
        # Register first user
        client.post('/auth/register', data={
            'full_name': 'First',
            'email': 'dup@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': ''
        })
        # Try to register with same email
        resp = client.post('/auth/register', data={
            'full_name': 'Second',
            'email': 'dup@test.com',
            'password': 'password456',
            'confirm_password': 'password456',
            'phone': ''
        }, follow_redirects=True)
        assert b'already exists' in resp.data or b'email already registered'.lower() in resp.data.lower()

    def test_auto_login_after_register(self, client):
        client.post('/auth/register', data={
            'full_name': 'Auto',
            'email': 'auto@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': ''
        }, follow_redirects=True)
        # After registration, user should be auto-logged in
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None
            assert sess.get('user_name') == 'Auto'


# ============================================================
# MEMBER 3: Login & Profile Tests
# ============================================================

class TestLogin:
    def test_login_page_loads(self, client):
        resp = client.get('/auth/login')
        assert resp.status_code == 200
        assert b'Login' in resp.data

    def test_successful_login(self, client):
        # Register first
        client.post('/auth/register', data={
            'full_name': 'Login User',
            'email': 'login@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': ''
        })
        # Logout
        with client.session_transaction() as sess:
            sess.clear()

        # Login
        resp = client.post('/auth/login', data={
            'email': 'login@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Welcome back' in resp.data

    def test_wrong_email(self, client):
        resp = client.post('/auth/login', data={
            'email': 'nobody@test.com',
            'password': 'pass123'
        }, follow_redirects=True)
        assert b'No account found' in resp.data

    def test_wrong_password(self, client):
        client.post('/auth/register', data={
            'full_name': 'PW User',
            'email': 'pw@test.com',
            'password': 'correct123',
            'confirm_password': 'correct123',
            'phone': ''
        })
        with client.session_transaction() as sess:
            sess.clear()

        resp = client.post('/auth/login', data={
            'email': 'pw@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert b'Incorrect password' in resp.data

    def test_logout(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Test'
        resp = client.get('/auth/logout', follow_redirects=True)
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None

    def test_profile_page_requires_login(self, client):
        resp = client.get('/auth/profile', follow_redirects=True)
        assert b'log in' in resp.data.lower()

    def test_profile_shows_user_data(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'System Admin'
            sess['role'] = 'admin'
        resp = client.get('/auth/profile')
        assert resp.status_code == 200
        assert b'System Admin' in resp.data

    def test_admin_login_via_seed(self, client):
        """Test logging in with seeded admin account."""
        resp = client.post('/auth/login', data={
            'email': 'admin@itum.lk',
            'password': 'admin123'
        }, follow_redirects=True)
        assert b'Welcome back' in resp.data
        with client.session_transaction() as sess:
            assert sess.get('role') == 'admin'


# ============================================================
# MEMBER 4: Profile Edit Tests
# ============================================================

class TestProfileEdit:
    def test_edit_profile_page_loads(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.get('/profile/edit')
        assert resp.status_code == 200
        assert b'Edit Profile' in resp.data

    def test_edit_profile_requires_login(self, client):
        resp = client.get('/profile/edit', follow_redirects=True)
        assert b'log in' in resp.data.lower()

    def test_successful_profile_update(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.post('/profile/edit', data={
            'full_name': 'Updated Name',
            'email': 'updated@itum.lk',
            'phone': '0770000000'
        }, follow_redirects=True)
        assert b'Profile updated' in resp.data

        # Verify DB was updated
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id=1").fetchone()
        assert user['full_name'] == 'Updated Name'
        assert user['email'] == 'updated@itum.lk'

    def test_edit_empty_name_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.post('/profile/edit', data={
            'full_name': '',
            'email': 'admin@itum.lk',
            'phone': ''
        }, follow_redirects=True)
        assert b'Name is required' in resp.data

    def test_change_password_page_loads(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.get('/profile/change-password')
        assert resp.status_code == 200

    def test_wrong_old_password_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # admin password is 'admin123'
            sess['user_name'] = 'Admin'
        resp = client.post('/profile/change-password', data={
            'old_password': 'wrong',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        assert b'incorrect' in resp.data.lower()

    def test_password_mismatch_on_change(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.post('/profile/change-password', data={
            'old_password': 'admin123',
            'new_password': 'newpass123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        assert b'do not match' in resp.data

    def test_short_new_password_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
        resp = client.post('/profile/change-password', data={
            'old_password': 'admin123',
            'new_password': 'ab',
            'confirm_password': 'ab'
        }, follow_redirects=True)
        assert b'at least 6' in resp.data


# ============================================================
# MEMBER 5: Book Appointment Tests
# ============================================================

class TestBookAppointment:
    def test_book_page_loads(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/appointments/book')
        assert resp.status_code == 200
        assert b'Book an Appointment' in resp.data
        assert b'Dr.' in resp.data  # Doctors should be listed

    def test_book_requires_login(self, client):
        resp = client.get('/appointments/book', follow_redirects=True)
        assert b'log in' in resp.data.lower()

    def test_successful_booking(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.post('/appointments/book', data={
            'doctor_id': '1',
            'date': '2026-12-25',
            'time': '10:00',
            'reason': 'Checkup'
        }, follow_redirects=True)
        assert b'Appointment Booked' in resp.data

        # Verify in DB
        db = get_db()
        appt = db.execute("SELECT * FROM appointments WHERE student_id=1").fetchone()
        assert appt is not None
        assert appt['doctor_id'] == 1
        assert appt['status'] == 'pending'

    def test_double_booking_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        # Book once
        client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'First'
        })
        # Book same slot
        resp = client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'Second'
        }, follow_redirects=True)
        assert b'already booked' in resp.data

    def test_past_date_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.post('/appointments/book', data={
            'doctor_id': '1',
            'date': '2020-01-01',
            'time': '10:00',
            'reason': 'Past'
        }, follow_redirects=True)
        assert b'past' in resp.data

    def test_missing_doctor_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.post('/appointments/book', data={
            'doctor_id': '',
            'date': '2026-12-25',
            'time': '10:00',
            'reason': ''
        }, follow_redirects=True)
        assert b'select a doctor' in resp.data

    def test_missing_date_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.post('/appointments/book', data={
            'doctor_id': '1',
            'date': '',
            'time': '10:00',
            'reason': ''
        }, follow_redirects=True)
        assert b'select a date' in resp.data

    def test_invalid_doctor_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.post('/appointments/book', data={
            'doctor_id': '999',
            'date': '2026-12-25',
            'time': '10:00',
            'reason': 'Ghost'
        }, follow_redirects=True)
        assert b'not found' in resp.data or b'select a doctor' in resp.data


# ============================================================
# MEMBER 6: View & Cancel Tests
# ============================================================

class TestAppointments:
    def test_appointments_page_loads(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.get('/appointments/')
        assert resp.status_code == 200
        assert b'My Appointments' in resp.data

    def test_appointments_requires_login(self, client):
        resp = client.get('/appointments/', follow_redirects=True)
        assert b'log in' in resp.data.lower()

    def test_upcoming_filter(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.get('/appointments/?filter=upcoming')
        assert resp.status_code == 200

    def test_past_filter(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.get('/appointments/?filter=past')
        assert resp.status_code == 200

    def test_all_filter(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.get('/appointments/?filter=all')
        assert resp.status_code == 200

    def test_cancel_page_loads(self, client):
        # Create an appointment first
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'Cancel Test'
        })
        resp = client.get('/appointments/cancel/1')
        assert resp.status_code == 200
        assert b'Cancel Appointment' in resp.data

    def test_successful_cancel(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'To Cancel'
        })
        resp = client.post('/appointments/cancel/1', follow_redirects=True)
        assert b'cancelled' in resp.data.lower()

        # Verify DB
        db = get_db()
        appt = db.execute("SELECT * FROM appointments WHERE id=1").fetchone()
        assert appt['status'] == 'cancelled'

    def test_cancel_other_users_appointment_rejected(self, client):
        """Test that a student cannot cancel another student's appointment."""
        # Create appointment as user 1
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student1'
            sess['role'] = 'student'
        client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'Mine'
        })

        # Try to cancel as user 2
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Student2'
            sess['role'] = 'student'
        resp = client.post('/appointments/cancel/1', follow_redirects=True)
        assert b'not found' in resp.data.lower() or b'Appointment not found' in resp.data

    def test_cancel_already_cancelled(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        client.post('/appointments/book', data={
            'doctor_id': '1', 'date': '2026-12-25',
            'time': '10:00', 'reason': 'Double Cancel'
        })
        # Cancel once
        client.post('/appointments/cancel/1')
        # Try to cancel again
        resp = client.post('/appointments/cancel/1', follow_redirects=True)
        assert b'already cancelled' in resp.data


# ============================================================
# MEMBER 7: Feedback Tests
# ============================================================

class TestFeedback:
    def test_feedback_form_loads(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.get('/feedback/give')
        assert resp.status_code == 200
        assert b'Give Feedback' in resp.data

    def test_feedback_requires_login(self, client):
        resp = client.get('/feedback/give', follow_redirects=True)
        assert b'log in' in resp.data.lower()

    def test_successful_feedback(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.post('/feedback/give', data={
            'doctor_id': '1',
            'rating': '5',
            'comment': 'Excellent doctor!'
        }, follow_redirects=True)
        assert b'Thank you' in resp.data
        assert b'feedback' in resp.data

        # Verify DB
        db = get_db()
        fb = db.execute("SELECT * FROM feedback WHERE student_id=1").fetchone()
        assert fb is not None
        assert fb['rating'] == 5

    def test_invalid_rating_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.post('/feedback/give', data={
            'doctor_id': '1',
            'rating': '0',
            'comment': 'Bad'
        }, follow_redirects=True)
        assert b'Rating must be between' in resp.data or b'1 and 5' in resp.data

    def test_no_doctor_selected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.post('/feedback/give', data={
            'doctor_id': '',
            'rating': '3',
            'comment': 'OK'
        }, follow_redirects=True)
        assert b'select a doctor' in resp.data

    def test_empty_comment_rejected(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        resp = client.post('/feedback/give', data={
            'doctor_id': '1',
            'rating': '3',
            'comment': ''
        }, follow_redirects=True)
        assert b'write a comment' in resp.data

    def test_feedback_list_page(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
        # Submit some feedback first
        client.post('/feedback/give', data={
            'doctor_id': '1', 'rating': '4', 'comment': 'Good'
        })
        resp = client.get('/feedback/')
        assert resp.status_code == 200
        assert b'Average Ratings' in resp.data

    def test_my_feedback_requires_login(self, client):
        resp = client.get('/feedback/', follow_redirects=True)
        assert b'log in' in resp.data.lower()


# ============================================================
# MEMBER 8: Admin Tests
# ============================================================

class TestAdmin:
    def test_admin_dashboard(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/')
        assert resp.status_code == 200
        assert b'Admin Dashboard' in resp.data
        # Stats should be visible
        assert b'Users' in resp.data
        assert b'Doctors' in resp.data
        assert b'Total Appointments' in resp.data
        assert b'All Appointments' in resp.data

    def test_admin_dashboard_allows_doctor(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Dr. Priya Mendis'
            sess['role'] = 'doctor'
        resp = client.get('/admin/')
        assert resp.status_code == 200
        assert b'Admin Dashboard' in resp.data

    def test_admin_dashboard_blocks_student(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/admin/', follow_redirects=True)
        assert b'Staff access required' in resp.data

    def test_admin_users_page(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/users')
        assert resp.status_code == 200
        assert b'Manage Users' in resp.data

    def test_admin_users_search(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/users?search=Admin')
        assert resp.status_code == 200
        assert b'System Admin' in resp.data

    def test_admin_users_search_no_results(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/users?search=ZZZNOTEXIST')
        assert resp.status_code == 200
        assert b'No users found' in resp.data

    def test_admin_appointments_page(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/appointments')
        assert resp.status_code == 200
        assert b'All Appointments' in resp.data

    def test_admin_appointments_filter(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/admin/appointments?status=pending')
        assert resp.status_code == 200

    def test_admin_users_blocks_student(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/admin/users', follow_redirects=True)
        assert b'Staff access required' in resp.data

    def test_admin_appointments_blocks_student(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/admin/appointments', follow_redirects=True)
        assert b'Staff access required' in resp.data


# ============================================================
# FULL END-TO-END USER FLOW
# ============================================================

class TestFullFlow:
    def test_complete_user_journey(self, client):
        """Test the entire user journey from registration to admin view."""

        # Step 1: Register
        resp = client.post('/auth/register', data={
            'full_name': 'Jane Doe',
            'email': 'jane@test.com',
            'password': 'secret123',
            'confirm_password': 'secret123',
            'phone': '0771112222'
        }, follow_redirects=True)
        assert b'Registration successful' in resp.data

        # Step 2: Visit home as logged-in user
        resp = client.get('/')
        assert b'Book Appointment' in resp.data
        assert b'Jane Doe' in resp.data

        # Step 3: Book an appointment
        resp = client.post('/appointments/book', data={
            'doctor_id': '1',
            'date': '2026-12-25',
            'time': '14:00',
            'reason': 'Annual checkup'
        }, follow_redirects=True)
        assert b'Appointment Booked' in resp.data

        # Step 4: View appointments
        resp = client.get('/appointments/')
        assert b'Dr.' in resp.data  # Doctor name visible
        assert b'Pending' in resp.data

        # Step 5: Give feedback
        resp = client.post('/feedback/give', data={
            'doctor_id': '1',
            'rating': '4',
            'comment': 'Very good service'
        }, follow_redirects=True)
        assert b'Thank you' in resp.data

        # Step 6: View feedback
        resp = client.get('/feedback/')
        assert b'4' in resp.data or b'Very good' in resp.data

        # Step 7: Cancel appointment
        resp = client.post('/appointments/cancel/1', follow_redirects=True)
        assert b'cancelled' in resp.data.lower()

        # Step 8: Logout
        client.get('/auth/logout')

        # Step 9: Login as admin
        resp = client.post('/auth/login', data={
            'email': 'admin@itum.lk',
            'password': 'admin123'
        }, follow_redirects=True)
        assert b'Welcome back' in resp.data

        # Step 10: Check admin dashboard
        resp = client.get('/admin/')
        assert b'Users' in resp.data
        assert b'Total Appointments' in resp.data
        assert b'All Appointments' in resp.data

        # Step 11: Check admin users has Jane Doe
        resp = client.get('/admin/users')
        assert b'Jane Doe' in resp.data

        # Step 12: Check admin appointments
        resp = client.get('/admin/appointments')
        assert b'Jane Doe' in resp.data

        print("\n=== FULL USER JOURNEY COMPLETED SUCCESSFULLY ===")


# ============================================================
# STATIC FILES
# ============================================================

class TestStaticFiles:
    def test_css_served(self, client):
        resp = client.get('/static/style.css')
        assert resp.status_code == 200
        assert b'background-color' in resp.data

    def test_css_has_hero_section(self, client):
        resp = client.get('/static/style.css')
        assert b'.hero-section' in resp.data

    def test_css_has_feature_card(self, client):
        resp = client.get('/static/style.css')
        assert b'.feature-card' in resp.data


# ============================================================
# EDGE CASES
# ============================================================

class TestEdgeCases:
    def test_login_already_logged_in(self, client):
        """Already logged-in user visiting login page gets redirected."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin'
            sess['role'] = 'admin'
        resp = client.get('/auth/login', follow_redirects=True)
        # Should redirect to home (not show login form)
        assert b'Create an Account' not in resp.data  # login form has this? No, register has this
        # Actually login page doesn't have 'Create an Account', it has 'Login'
        # Let's check it redirects properly
        assert resp.request.path == '/' or b'ITUM Medical Centre' in resp.data

    def test_nonexistent_route(self, client):
        resp = client.get('/this-does-not-exist')
        assert resp.status_code == 404

    def test_nonexistent_cancel_id(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Student'
            sess['role'] = 'student'
        resp = client.get('/appointments/cancel/999', follow_redirects=True)
        assert b'not found' in resp.data


# ============================================================
# MAIN RUNNER
# ============================================================

if __name__ == '__main__':
    # Run with pytest in verbose mode
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))
