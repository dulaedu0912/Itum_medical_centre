from flask import Flask, render_template
from db import init_db

from routes.register import register_bp
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.book import book_bp
from routes.appointments import appointments_bp
from routes.feedback import feedback_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = 'itum_clinic_super_secret_key_2026'

app.register_blueprint(register_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(book_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(admin_bp)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)