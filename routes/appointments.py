from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from datetime import date

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments_bp.route('/')
def my_appointments():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    filter_by = request.args.get('filter', 'upcoming')
    db = get_db()

    base_query = """SELECT a.*, d.name as doctor_name
                    FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.id
                    WHERE a.student_id = ?"""

    today = str(date.today())

    if filter_by == 'upcoming':
        query = base_query + " AND a.appointment_date >= ? AND a.status != 'cancelled' ORDER BY a.appointment_date ASC, a.appointment_time ASC"
        params = (student_id, today)
    elif filter_by == 'past':
        query = base_query + " AND (a.appointment_date < ? OR a.status = 'cancelled') ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        params = (student_id, today)
    else:
        query = base_query + " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        params = (student_id,)

    appointments = db.execute(query, params).fetchall()

    return render_template('appointments.html', appointments=appointments,
                           current_filter=filter_by)


@appointments_bp.route('/cancel/<int:appt_id>', methods=['GET', 'POST'])
def cancel(appt_id):
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    db = get_db()

    # Verify this appointment belongs to the logged-in user
    appt = db.execute(
        """SELECT a.*, d.name as doctor_name
           FROM appointments a JOIN doctors d ON a.doctor_id = d.id
           WHERE a.id = ? AND a.student_id = ?""",
        (appt_id, student_id)
    ).fetchone()

    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.my_appointments'))

    if appt['status'] == 'cancelled':
        flash('This appointment is already cancelled.', 'warning')
        return redirect(url_for('appointments.my_appointments'))

    if request.method == 'POST':
        db.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
            (appt_id,)
        )
        db.commit()
        flash('Appointment cancelled successfully.', 'success')
        return redirect(url_for('appointments.my_appointments'))

    return render_template('cancel.html', appt=appt)