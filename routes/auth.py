from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_logged_in_user():
    """Helper function to get the currently logged-in user from database."""
    user_id = session.get('user_id')
    if user_id is None:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to home
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        error = None
        if user is None:
            error = 'No account found with this email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error:
            return render_template('login.html', error=error, email=email)

        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['role'] = user['role']
        flash('Welcome back, ' + user['full_name'] + '!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', error=None)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
def profile():
    user = get_logged_in_user()
    if user is None:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=user)