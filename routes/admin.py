from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def staff_required():
    """Check if the current user is an admin or doctor."""
    role = session.get('role')
    if role not in ('admin', 'doctor'):
        flash('Staff access required.', 'danger')
        return redirect(url_for('index'))
    return None


@admin_bp.route('/')
def dashboard():
    redirect_response = staff_required()
    if redirect_response:
        return redirect_response

    db = get_db()

    total_users = db.execute(
        "SELECT COUNT(*) as count FROM users"
    ).fetchone()['count']

    total_doctors = db.execute(
        "SELECT COUNT(*) as count FROM doctors"
    ).fetchone()['count']

    total_appointments = db.execute(
        "SELECT COUNT(*) as count FROM appointments"
    ).fetchone()['count']

    statuses = ['pending', 'completed', 'cancelled']
    status_counts = {}
    for status in statuses:
        count = db.execute(
            "SELECT COUNT(*) as c FROM appointments WHERE status = ?",
            (status,)
        ).fetchone()['c']
        status_counts[status] = count

    all_appointments = db.execute(
        """SELECT a.*, u.full_name as student_name, d.name as doctor_name
           FROM appointments a
           JOIN users u ON a.student_id = u.id
           JOIN doctors d ON a.doctor_id = d.id
           ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
    ).fetchall()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_doctors=total_doctors,
                           total_appointments=total_appointments,
                           status_counts=status_counts,
                           all_appointments=all_appointments)


@admin_bp.route('/users')
def manage_users():
    redirect_response = staff_required()
    if redirect_response:
        return redirect_response

    search = request.args.get('search', '').strip()
    db = get_db()

    if search:
        users = db.execute(
            """SELECT * FROM users
               WHERE full_name LIKE ? OR email LIKE ?
               ORDER BY created_at DESC""",
            ('%' + search + '%', '%' + search + '%')
        ).fetchall()
    else:
        users = db.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()

    return render_template('admin_users.html', users=users, search=search)


@admin_bp.route('/appointments')
def manage_appointments():
    redirect_response = staff_required()
    if redirect_response:
        return redirect_response

    status_filter = request.args.get('status', 'all')
    db = get_db()

    if status_filter == 'all':
        appointments = db.execute(
            """SELECT a.*, u.full_name as student_name, d.name as doctor_name
               FROM appointments a
               JOIN users u ON a.student_id = u.id
               JOIN doctors d ON a.doctor_id = d.id
               ORDER BY a.appointment_date DESC"""
        ).fetchall()
    else:
        appointments = db.execute(
            """SELECT a.*, u.full_name as student_name, d.name as doctor_name
               FROM appointments a
               JOIN users u ON a.student_id = u.id
               JOIN doctors d ON a.doctor_id = d.id
               WHERE a.status = ?
               ORDER BY a.appointment_date DESC""",
            (status_filter,)
        ).fetchall()

    return render_template('admin_appointments.html',
                           appointments=appointments,
                           status_filter=status_filter)