from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, User
import os

app = Flask(__name__)

# --- CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cpms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

def init_database():
    with app.app_context():
        # 1. Create all tables based on models.py
        db.create_all()
        print(f">>> Database connected at: {os.path.join(basedir, 'cpms.db')}")

        # 2. Create Default Admin (Institute Placement Cell)
        admin_email = "24f2004690@ds.study.iitm.ac.in"
        existing_admin = User.query.filter_by(email=admin_email).first()

        if not existing_admin:
            hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
            new_admin = User(
                username="placement_admin",
                email=admin_email,
                password_hash=hashed_pw,
                role="admin"
                # The Admin does not need a corresponding Company or Student profile
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f">>> Admin created successfully!")
            print(f">>> Login: {admin_email} | Pass: admin123")
        else:
            print(">>> Admin user already exists.")

if __name__ == "__main__":
    init_database()