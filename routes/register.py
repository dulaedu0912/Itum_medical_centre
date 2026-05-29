from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register', __name__, url_prefix='/auth')


@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm_password']
        phone = request.form.get('phone', '').strip()

        errors = []

        if not name or not email or not password:
            errors.append('Full name, email, and password are required.')

        if '@' not in email or '.' not in email:
            errors.append('Please enter a valid email address.')

        if password != confirm:
            errors.append('Passwords do not match.')

        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if not errors:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                errors.append('An account with this email already exists.')

        if not errors:
            pw_hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (full_name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                (name, email, pw_hash, phone)
            )
            db.commit()

            user = db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['role'] = user['role']

            flash('Registration successful! Welcome.', 'success')
            return redirect(url_for('index'))

        return render_template('register.html', errors=errors,
                               name=name, email=email, phone=phone)

    return render_template('register.html', errors=None)


# Also add a check-email route for Member 2's extra credit
@register_bp.route('/check-email')
def check_email():
    email = request.args.get('email', '').strip().lower()
    if not email:
        return {'available': False}
    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    return {'available': existing is None}