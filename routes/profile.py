from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


def login_required():
    """Simple helper to check if user is logged in."""
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))
    return None


@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    redirect_response = login_required()
    if redirect_response:
        return redirect_response

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (session['user_id'],)
    ).fetchone()

    if request.method == 'POST':
        name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form.get('phone', '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if '@' not in email or '.' not in email:
            errors.append('Invalid email address.')

        # Check if email is taken by another user
        existing = db.execute(
            "SELECT id FROM users WHERE email = ? AND id != ?",
            (email, session['user_id'])
        ).fetchone()
        if existing:
            errors.append('This email is already in use by another account.')

        if not errors:
            db.execute(
                "UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?",
                (name, email, phone, session['user_id'])
            )
            db.commit()
            session['user_name'] = name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))

        return render_template('profile_edit.html', user={
            'full_name': name, 'email': email, 'phone': phone
        }, errors=errors)

    return render_template('profile_edit.html', user=user, errors=None)


@profile_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    redirect_response = login_required()
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (session['user_id'],)
        ).fetchone()

        old_pw = request.form['old_password']
        new_pw = request.form['new_password']
        confirm = request.form['confirm_password']

        errors = []
        if not check_password_hash(user['password_hash'], old_pw):
            errors.append('Current password is incorrect.')
        if new_pw != confirm:
            errors.append('New passwords do not match.')
        if len(new_pw) < 6:
            errors.append('New password must be at least 6 characters.')

        if not errors:
            new_hash = generate_password_hash(new_pw)
            db.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, session['user_id'])
            )
            db.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))

        return render_template('change_password.html', errors=errors)

    return render_template('change_password.html', errors=None)