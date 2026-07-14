from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ==========================================
# 1. CORE AUTHENTICATION
# ==========================================
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'company', 'student'
    
    # Relationships
    company_profile = db.relationship('Company', back_populates='user', uselist=False, cascade="all, delete")
    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete")

# ==========================================
# 2. PROFILES
# ==========================================
class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(150), nullable=True)
    
    # Admin Controls
    is_approved = db.Column(db.Boolean, default=False) 
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='company_profile')
    drives = db.relationship('PlacementDrive', back_populates='company', cascade="all, delete-orphan")

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.String(20), nullable=True) 
    branch = db.Column(db.String(50), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    experience = db.Column(db.String(200), nullable=True)
    resume_file = db.Column(db.String(255), nullable=True)
    
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='student_profile')
    applications = db.relationship('Application', back_populates='student', cascade="all, delete-orphan")

# ==========================================
# 3. OPERATIONS
# ==========================================
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=True) # e.g. "B.Tech CS, CGPA > 7.0"
    application_deadline = db.Column(db.String(20), nullable=False)
   

    
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    resume_file = db.Column(db.String(255), nullable=True)
    
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied') # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    remarks = db.Column(db.Text, nullable=True) # Interviewer feedback
    interview_date = db.Column(db.DateTime, nullable=True)

    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')