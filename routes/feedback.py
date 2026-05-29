from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')


@feedback_bp.route('/give', methods=['GET', 'POST'])
def give_feedback():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    db = get_db()
    doctors = db.execute("SELECT * FROM doctors ORDER BY name").fetchall()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        student_id = session['user_id']

        errors = []

        if not doctor_id:
            errors.append('Please select a doctor.')

        if not rating:
            errors.append('Please select a rating.')
        else:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    errors.append('Rating must be between 1 and 5.')
            except ValueError:
                errors.append('Invalid rating value.')

        if not comment:
            errors.append('Please write a comment.')

        if doctor_id:
            doctor = db.execute(
                "SELECT id FROM doctors WHERE id = ?", (doctor_id,)
            ).fetchone()
            if not doctor:
                errors.append('Selected doctor not found.')

        if not errors:
            db.execute(
                "INSERT INTO feedback (student_id, doctor_id, rating, comment) VALUES (?, ?, ?, ?)",
                (student_id, doctor_id, rating, comment)
            )
            db.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('feedback.my_feedback'))

        return render_template('feedback_form.html', doctors=doctors,
                               errors=errors, form_data=request.form)

    return render_template('feedback_form.html', doctors=doctors, errors=None)


@feedback_bp.route('/')
def my_feedback():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    db = get_db()

    # Student's own feedback with doctor names
    feedbacks = db.execute(
        """SELECT f.*, d.name as doctor_name
           FROM feedback f
           JOIN doctors d ON f.doctor_id = d.id
           WHERE f.student_id = ?
           ORDER BY f.created_at DESC""",
        (student_id,)
    ).fetchall()

    # Average ratings per doctor (for all students)
    averages = db.execute(
        """SELECT d.name,
                  ROUND(AVG(f.rating), 1) as avg_rating,
                  COUNT(f.id) as review_count
           FROM feedback f
           JOIN doctors d ON f.doctor_id = d.id
           GROUP BY f.doctor_id
           ORDER BY avg_rating DESC"""
    ).fetchall()

    return render_template('feedback_list.html', feedbacks=feedbacks,
                           averages=averages)