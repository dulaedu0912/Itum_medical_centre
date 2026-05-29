from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from datetime import date

book_bp = Blueprint('book', __name__, url_prefix='/appointments')


@book_bp.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        flash('Please log in to book an appointment.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    doctors = db.execute("SELECT * FROM doctors ORDER BY name").fetchall()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appt_date = request.form.get('date')
        appt_time = request.form.get('time')
        reason = request.form.get('reason', '').strip()
        student_id = session['user_id']

        errors = []

        # Validate: doctor selected
        if not doctor_id:
            errors.append('Please select a doctor.')

        # Validate: date provided
        if not appt_date:
            errors.append('Please select a date.')

        # Validate: date is not in the past
        if appt_date and appt_date < str(date.today()):
            errors.append('Cannot book an appointment in the past.')

        # Validate: time provided
        if not appt_time:
            errors.append('Please select a time.')

        # Validate: doctor exists
        if doctor_id:
            doctor = db.execute(
                "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
            ).fetchone()
            if not doctor:
                errors.append('Selected doctor not found.')

        # Validate: no double-booking (same doctor, same date, same time)
        if doctor_id and appt_date and appt_time and not errors:
            existing = db.execute(
                """SELECT id FROM appointments
                   WHERE doctor_id = ? AND appointment_date = ?
                   AND appointment_time = ? AND status != 'cancelled'""",
                (doctor_id, appt_date, appt_time)
            ).fetchone()
            if existing:
                errors.append('This time slot is already booked.')

        if not errors:
            db.execute(
                """INSERT INTO appointments
                   (student_id, doctor_id, appointment_date, appointment_time, reason, status)
                   VALUES (?, ?, ?, ?, ?, 'pending')""",
                (student_id, doctor_id, appt_date, appt_time, reason)
            )
            db.commit()

            cursor = db.execute("SELECT last_insert_rowid() as id")
            appt_id = cursor.fetchone()['id']

            booking = db.execute(
                """SELECT a.*, u.full_name as student_name, d.name as doctor_name
                   FROM appointments a
                   JOIN users u ON a.student_id = u.id
                   JOIN doctors d ON a.doctor_id = d.id
                   WHERE a.id = ?""",
                (appt_id,)
            ).fetchone()

            flash('Appointment booked successfully!', 'success')
            return render_template('booking_confirmation.html', booking=booking)

        return render_template('book.html', doctors=doctors, errors=errors,
                               form_data=request.form)

    return render_template('book.html', doctors=doctors, errors=None)