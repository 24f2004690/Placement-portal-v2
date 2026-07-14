from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_caching import Cache
from celery import Celery
import csv
import time
from flask_mail import Mail, Message
from flask import render_template
from celery.schedules import crontab

from models import db, User, Company, Student, PlacementDrive, Application

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Cache Config
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 60 # Default cache expiry is 60 seconds

# Configure Celery
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

# Initialize Celery using the updated keys
celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)

cache = Cache(app)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cpms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'cpms-super-secret-key-change-this' # Change for production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# EMAIL CONFIGURATION
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tiblue1729@gmail.com'
app.config['MAIL_PASSWORD'] = 'mdmcaqsbmxmpqbby'
app.config['MAIL_DEFAULT_SENDER'] = 'tiblue1729@gmail.com'

mail = Mail(app)

# Configure an uploads folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # if the folder doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensions
CORS(app) 
db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return "CPMS API is Running!"

# ==========================================
# 1. AUTHENTICATION (Login & Register)
# ==========================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('email') # Can handle either email or username if needed
    password = data.get('password')

    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        
        real_name = user.username 
        company_id = None
        student_id = None

        # Check approval status for companies
        if user.role == 'company' and user.company_profile:
            if not user.company_profile.is_approved:
                return jsonify({"error": "Your company account is pending Admin approval."}), 403
            if user.company_profile.is_blacklisted:
                return jsonify({"error": "Your company account has been suspended."}), 403
            real_name = user.company_profile.name
            company_id = user.company_profile.id
            
        elif user.role == 'student' and user.student_profile:
            if user.student_profile.is_blacklisted:
                return jsonify({"error": "Your account has been suspended."}), 403
            real_name = user.student_profile.full_name
            student_id = user.student_profile.id
            
        elif user.role == 'admin':
            real_name = "Administrator"

        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "role": user.role,
            "username": user.username,
            "name": real_name,
            "id": user.id,
            "company_id": company_id,
            "student_id": student_id
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    required_fields = ['name', 'username', 'email', 'password']
    for field in required_fields:
        if not data.get(field): return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        return jsonify({"error": "Email or Username already exists"}), 400
    
    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password_hash=hashed_pw, role='student')
        db.session.add(new_user)
        db.session.flush() 

        new_student = Student(
            user_id=new_user.id, 
            full_name=data['name'], 
            phone=data.get('phone'), 
            dob=data.get('dob'),
            branch=data.get('branch'),
            cgpa=data.get('cgpa')
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    required_fields = ['name', 'username', 'email', 'password', 'hr_contact']
    for field in required_fields:
        if not data.get(field): return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        return jsonify({"error": "Email or Username already exists"}), 400
    
    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password_hash=hashed_pw, role='company')
        db.session.add(new_user)
        db.session.flush() 

        # Note: is_approved defaults to False in the model
        new_company = Company(
            user_id=new_user.id,
            name=data['name'],
            hr_contact=data['hr_contact'],
            website=data.get('website')
        )
        db.session.add(new_company)
        db.session.commit()
        return jsonify({"message": "Company registered successfully. Pending Admin approval."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# --- SESSION VERIFICATION ---
@app.route('/api/verify_session', methods=['GET'])
@jwt_required()
def verify_session():
    # If the token is expired or the user lookup loader fails (user deleted), 
    # this will automatically abort with a 401 before reaching this return statement.
    return jsonify({"status": "valid"}), 200

# ==========================================
# 2. ADMIN ROUTES
# ==========================================


# ----ADMIN SEARCH ROUTE

@app.route('/api/admin/global_search', methods=['GET'])
@jwt_required()
def admin_global_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2: return jsonify({})
    search_term = f"%{query}%"

    students = Student.query.filter((Student.full_name.ilike(search_term)) | (Student.branch.ilike(search_term))).limit(5).all()
    companies = Company.query.filter(Company.name.ilike(search_term)).limit(5).all()
    drives = PlacementDrive.query.join(Company).filter((PlacementDrive.job_title.ilike(search_term)) | (Company.name.ilike(search_term))).limit(5).all()

    return jsonify({
        "Students": [{"id": s.id, "title": s.full_name, "subtitle": s.branch, "route": "/admin/students"} for s in students],
        "Companies": [{"id": c.id, "title": c.name, "subtitle": "Registered Company", "route": "/admin/companies"} for c in companies],
        "Placement Drives": [{"id": d.id, "title": d.job_title, "subtitle": d.company.name, "route": "/admin/drives"} for d in drives]
    }), 200


@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    # Fetching counts for the dashboard
    return jsonify({
        "students": Student.query.count(),
        "companies": Company.query.count(),
        "pending_companies": Company.query.filter_by(is_approved=False).count(),
        "active_drives": PlacementDrive.query.filter_by(status='Approved').count()
    }), 200

@app.route('/api/admin/companies', methods=['GET'])
@jwt_required()
def get_admin_companies():
    companies = Company.query.all()
    result = [{
        "id": c.id,
        "name": c.name,
        "email": c.user.email,
        "hr_contact": c.hr_contact,
        "website": c.website,
        "is_approved": c.is_approved,
        "is_blacklisted": c.is_blacklisted
    } for c in companies]
    return jsonify(result), 200

@app.route('/api/admin/approve_company/<int:id>', methods=['PUT'])
@jwt_required()
def approve_company(id):
    company = Company.query.get_or_404(id)
    company.is_approved = True
    db.session.commit()
    return jsonify({"message": f"{company.name} has been approved."}), 200

@app.route('/api/admin/blacklist_company/<int:id>', methods=['PUT'])
@jwt_required()
def toggle_blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    status = "Blacklisted" if company.is_blacklisted else "Restored"
    return jsonify({"message": f"Company {status} successfully"}), 200

@app.route('/api/admin/drives', methods=['GET'])
@jwt_required()
def get_all_drives():
    drives = PlacementDrive.query.all()
    result = [{
        "id": d.id,
        "company": d.company.name,
        "job_title": d.job_title,
        "desc": d.job_description,               
        "eligibility": d.eligibility_criteria,
        "deadline": d.application_deadline,
        "status": d.status
    } for d in drives]
    return jsonify(result), 200

@app.route('/api/admin/approve_drive/<int:id>', methods=['PUT'])
@jwt_required()
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    return jsonify({"message": "Drive approved successfully."}), 200

@app.route('/api/admin/reject_drive/<int:id>', methods=['PUT'])
@jwt_required()
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Rejected'
    db.session.commit()
    return jsonify({"message": "Drive has been rejected."}), 200

# --- ADMIN: STUDENT DIRECTORY ---
@app.route('/api/admin/students', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def get_admin_students():
    students = Student.query.all()
    result = [{
        "id": s.id,
        "full_name": s.full_name,
        "email": s.user.email,
        "phone": s.phone,
        "branch": s.branch,
        "cgpa": s.cgpa,
        "is_blacklisted": s.is_blacklisted
    } for s in students]
    return jsonify(result), 200

# --- ADMIN: TOGGLE STUDENT BLACKLIST ---
@app.route('/api/admin/blacklist_student/<int:id>', methods=['PUT'])
@jwt_required()
def toggle_student_blacklist(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    status = "Blacklisted" if student.is_blacklisted else "Restored"
    return jsonify({"message": f"Student {status} successfully"}), 200


# --- ADMIN: ANALYTICS & REPORTS ---
@app.route('/api/admin/analytics', methods=['GET'])
@jwt_required()
def get_admin_analytics():
    # 1. Application Funnel Data
    funnel_query = db.session.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    funnel_dict = {status: count for status, count in funnel_query}
    
    # 2. Selections by Branch
    branch_query = db.session.query(Student.branch, func.count(Application.id))\
        .join(Application, Student.id == Application.student_id)\
        .filter(Application.status == 'Selected')\
        .group_by(Student.branch).all()
    branch_dict = {branch: count for branch, count in branch_query}
    
    # 3. Drive Posting Trends (Mocked timeline for charting)
    # In a production app, this would group by month/week.
    drives_query = db.session.query(func.date(PlacementDrive.created_at), func.count(PlacementDrive.id))\
        .group_by(func.date(PlacementDrive.created_at)).all()
    trends_list = [{"date": d[0], "count": d[1]} for d in drives_query]
    
    return jsonify({
        "funnel": funnel_dict,
        "branches": branch_dict,
        "trends": trends_list
    }), 200

# ==========================================
# 3. RECRUITER (COMPANY) ROUTES
# ==========================================

# -----RECRUITER SEARCH ROUTE

@app.route('/api/recruiter/global_search', methods=['GET'])
@jwt_required()
def recruiter_global_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2: return jsonify({})
    search_term = f"%{query}%"
    
    user = User.query.get(get_jwt_identity())
    company = user.company_profile

    drives = PlacementDrive.query.filter(PlacementDrive.company_id == company.id, PlacementDrive.job_title.ilike(search_term)).limit(5).all()
    
    # Only search students who applied to this company's drives
    apps = Application.query.join(Student).join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id,
        ((Student.full_name.ilike(search_term)) | (Student.branch.ilike(search_term)))
    ).limit(5).all()

    return jsonify({
        "My Drives": [{"id": d.id, "title": d.job_title, "subtitle": f"Status: {d.status}", "route": "/manage-drives"} for d in drives],
        "Applicants": [{"id": a.id, "title": a.student.full_name, "subtitle": a.student.branch, "route": "/drive-applications"} for a in apps]
    }), 200


@app.route('/api/recruiter/drives', methods=['GET', 'POST'])
@jwt_required()
def handle_recruiter_drives():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'company':
        return jsonify({"error": "Unauthorized"}), 403
        
    company = user.company_profile

    # --- GET: View all posted drives ---
    if request.method == 'GET':
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        result = [{
            "id": d.id,
            "title": d.job_title,
            "desc": d.job_description,
            "eligibility": d.eligibility_criteria,
            "deadline": d.application_deadline,
            "status": d.status
        } for d in drives]
        
        # Sort newest first
        result.sort(key=lambda x: x['id'], reverse=True)
        return jsonify(result), 200
        
    # --- POST: Create a new drive ---
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_drive = PlacementDrive(
                company_id=company.id,
                job_title=data.get('title'),
                job_description=data.get('desc'),
                eligibility_criteria=data.get('eligibility'),
                application_deadline=data.get('deadline'),
                status='Pending' # Always pending Admin approval initially
            )
            db.session.add(new_drive)
            db.session.commit()
            return jsonify({"message": "Drive posted successfully! Waiting for Admin approval."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route('/api/recruiter/drives/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modify_recruiter_drive(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    company = user.company_profile
    
    drive = PlacementDrive.query.get_or_404(id)
    
    # Security Check: Ensure this company owns this drive
    if drive.company_id != company.id:
        return jsonify({"error": "Unauthorized"}), 403

    # --- PUT: Update drive details ---
    if request.method == 'PUT':
        data = request.get_json()
        try:
            drive.job_title = data.get('title', drive.job_title)
            drive.job_description = data.get('desc', drive.job_description)
            drive.eligibility_criteria = data.get('eligibility', drive.eligibility_criteria)
            drive.application_deadline = data.get('deadline', drive.application_deadline)
            
            # If a drive is edited, you can optionally reset its status to 'Pending' here
            # drive.status = 'Pending' 
            
            db.session.commit()
            return jsonify({"message": "Drive updated successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- DELETE: Remove drive ---
    if request.method == 'DELETE':
       # Check if there are applications
        existing_apps = Application.query.filter_by(drive_id=id).count()
        if existing_apps > 0:
           return jsonify({"error": "Cannot delete a drive that has active student applications. Please close the drive instead."}), 400

        try:
            db.session.delete(drive)
            db.session.commit()
            return jsonify({"message": "Drive deleted successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
# --- RECRUITER: MANAGE APPLICATIONS ---
@app.route('/api/recruiter/applications', methods=['GET'])
@jwt_required()
def get_recruiter_applications():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    company = user.company_profile

    # Fetch all applications linked to drives owned by this company
    applications = db.session.query(Application).join(PlacementDrive).filter(PlacementDrive.company_id == company.id).all()
    
    result = [{
        "id": app.id,
        "student_name": app.student.full_name,
        "branch": app.student.branch,
        "cgpa": app.student.cgpa,
        "drive_title": app.drive.job_title,
        "resume_file": app.resume_file,
        "applied_on": app.application_date.strftime('%Y-%m-%d'),
        "status": app.status,
        "remarks": app.remarks,
        "interview_date": app.interview_date.isoformat() if app.interview_date else None
    } for app in applications]
    
    # Sort by newest applications first
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result), 200

@app.route('/api/recruiter/applications/<int:id>', methods=['PUT'])
@jwt_required()
def update_application_status(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    company = user.company_profile
    app_record = Application.query.get_or_404(id)
    
    if app_record.drive.company_id != company.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    try:
        app_record.status = data.get('status', app_record.status)
        # Store remarks purely as remarks now!
        app_record.remarks = data.get('remarks', '')
        
        # Handle the new interview_date column natively
        if app_record.status == 'Interview Scheduled' and data.get('interview_date'):
            date_str = data.get('interview_date')
            time_str = data.get('interview_time', '00:00')
            # Combine them into a proper Python DateTime object
            app_record.interview_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            # Clear it if the status changes to something else
            app_record.interview_date = None 

        db.session.commit()
        return jsonify({"message": "Application status updated!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. STUDENT ROUTES
# ==========================================

# ---- STUDENT SEARCH ROUTE
@app.route('/api/student/global_search', methods=['GET'])
@jwt_required()
def student_global_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2: return jsonify({})
    search_term = f"%{query}%"
    
    user = User.query.get(get_jwt_identity())
    student = user.student_profile

    drives = PlacementDrive.query.join(Company).filter(
        PlacementDrive.status == 'Approved',
        ((PlacementDrive.job_title.ilike(search_term)) | (Company.name.ilike(search_term)))
    ).limit(5).all()
    
    apps = Application.query.join(PlacementDrive).join(Company).filter(
        Application.student_id == student.id,
        Company.name.ilike(search_term)
    ).limit(5).all()

    return jsonify({
        "Active Opportunities": [{"id": d.id, "title": d.job_title, "subtitle": d.company.name, "route": "/student-dashboard"} for d in drives],
        "My Applications": [{"id": a.id, "title": a.drive.company.name, "subtitle": f"Status: {a.status}", "route": "/student-applications"} for a in apps]
    }), 200

from datetime import datetime

# --- STUDENT: PROFILE ---
@app.route('/api/student/profile', methods=['GET', 'PUT'])
@jwt_required()
def student_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    student = user.student_profile

    if request.method == 'GET':
        return jsonify({
            "full_name": student.full_name,
            "username": user.username,
            "email": user.email,
            "phone": student.phone,
            "dob": student.dob,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "experience": student.experience,
            "resume_file": student.resume_file
        }), 200

    if request.method == 'PUT':
        data = request.get_json()
        
        # Update fields directly
        student.full_name = data.get('full_name', student.full_name)
        student.phone = data.get('phone', student.phone)
        student.branch = data.get('branch', student.branch)
        student.cgpa = data.get('cgpa', student.cgpa)
        student.dob = data.get('dob', student.dob) # Save directly as string
        student.experience = data.get('experience', student.experience)
                
        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200

# --- STUDENT: UPLOAD RESUME ---
@app.route('/api/student/upload_resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    # Keep it simple: only allow PDFs
    if file and file.filename.endswith('.pdf'):
        # Secure the filename and make it unique using the user's ID
        filename = secure_filename(f"student_{get_jwt_identity()}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Save the filename in the database
        user = User.query.get(get_jwt_identity())
        user.student_profile.resume_file = filename
        db.session.commit()
        
        return jsonify({"message": "Resume uploaded successfully!", "resume_file": filename}), 200
        
    return jsonify({"message": "Only PDF files are allowed."}), 400

# --- ROUTE TO VIEW FILES ---
@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/student/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=120)
def get_student_drives():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    student = user.student_profile
    
    # Students should only see 'Approved' drives
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    result = []
    
    for d in drives:
        # 1. Skip drives where the deadline has passed
        if d.application_deadline < today_str:
            continue
            
        # 2. Check if the current student has already applied
        has_applied = Application.query.filter_by(student_id=student.id, drive_id=d.id).first() is not None
        
        result.append({
            "id": d.id,
            "company": d.company.name,
            "title": d.job_title,
            "desc": d.job_description,
            "eligibility": d.eligibility_criteria,
            "deadline": d.application_deadline,
            "has_applied": has_applied # Send this flag to the frontend
        })
    
    # Sort by newest
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result), 200

@app.route('/api/student/apply', methods=['POST'])
@jwt_required()
def student_apply():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'student':
        return jsonify({"error": "Unauthorized"}), 403
        
    student = user.student_profile
    
    # 1. Ensure they actually have a resume before applying!
    if not student.resume_file:
        return jsonify({"error": "Please upload your resume in the Profile section before applying."}), 400

    data = request.get_json()
    drive_id = data.get('drive_id')

    if not drive_id:
        return jsonify({"error": "Drive ID is required."}), 400

    # Prevent duplicate applications
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({"error": "You have already applied for this placement drive."}), 400

    try:
        new_app = Application(
            student_id=student.id,
            drive_id=drive_id,
            status='Applied',
            resume_file=student.resume_file
        )
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"message": "Application submitted successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/student/applications', methods=['GET'])
@jwt_required()
def get_student_applications():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    student = user.student_profile
    
    applications = Application.query.filter_by(student_id=student.id).all()
    
    result = [{
        "id": app.id,
        "company": app.drive.company.name,
        "title": app.drive.job_title,
        "date": app.application_date.strftime('%b %d, %Y'),
        "status": app.status,
        "remarks": app.remarks,
        "interview_date": app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else None
    } for app in applications]
    
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result), 200


# ==========================================
# ASYNC TASKS (CELERY)
# ==========================================

@celery.task(bind=True)
def export_csv_task(self, user_id):
    # Celery runs outside the main thread, so it needs an app context to access the database
    with app.app_context():
        user = User.query.get(user_id)
        student = user.student_profile
        
        filename = f"applications_export_std_{student.id}_{int(time.time())}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Artificial delay to demonstrate async background processing
        time.sleep(3) 
        
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied On'])
            
            for app_record in student.applications:
                writer.writerow([
                    student.id,
                    app_record.drive.company.name,
                    app_record.drive.job_title,
                    app_record.status,
                    app_record.application_date.strftime('%Y-%m-%d') if app_record.application_date else 'N/A'
                ])
                
        return {'status': 'Completed', 'filename': filename}
    
@celery.task(bind=True, name='app.send_daily_reminders')
def send_daily_reminders(self):
    with app.app_context():
        # Calculate tomorrow's date string (matching your DB format)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # FIXED: Use PlacementDrive and application_deadline
        closing_drives = PlacementDrive.query.filter_by(application_deadline=tomorrow, status='Approved').all()
        
        if not closing_drives:
            return "No drives closing tomorrow."

        # Get all active students
        students = Student.query.filter_by(is_blacklisted=False).all()
        student_emails = [student.user.email for student in students if student.user.email]
        
        if not student_emails:
            return "No students to email."

        # FIXED: Use job_title instead of title, and maybe include the company name!
        drive_titles = ", ".join([f"{d.company.name} ({d.job_title})" for d in closing_drives])
        
        # Compose the email
        msg = Message(
            subject="Action Required: Placement Drives Closing Tomorrow!",
            bcc=student_emails # Use BCC to protect student privacy
        )
        msg.body = f"""
        Hello Student,
        
        This is a friendly reminder from the CPMS Placement Cell. 
        
        The application deadline for the following placement drive(s) is tomorrow ({tomorrow}):
        {drive_titles}
        
        Please log in to your dashboard to complete your applications before the deadline.
        
        Best regards,
        Placement Cell
        """
        
        try:
            mail.send(msg)
            return f"Sent reminders to {len(student_emails)} students for {len(closing_drives)} drives."
        except Exception as e:
            return f"Failed to send email: {str(e)}"
        
@celery.task(bind=True, name='app.send_monthly_admin_report')
def send_monthly_admin_report(self):
    with app.app_context():
        # 1. Gather Statistics from the database
        total_drives = PlacementDrive.query.count()
        active_drives = PlacementDrive.query.filter_by(status='Approved').count()
        total_applications = Application.query.count()
        total_selected = Application.query.filter_by(status='Selected').count()
        
        current_month_year = datetime.now().strftime('%B %Y')

        # 2. Get all Admin emails
        admins = User.query.filter_by(role='admin').all()
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if not admin_emails:
            return "No admin emails found. Skipping report."

        # 3. Render the HTML Template
        html_body = render_template(
            'monthly_report.html',
            current_month_year=current_month_year,
            total_drives=total_drives,
            active_drives=active_drives,
            total_applications=total_applications,
            total_selected=total_selected
        )

        # 4. Send the Email
        msg = Message(
            subject=f"CPMS: Monthly Placement Activity Report - {current_month_year}",
            recipients=admin_emails
        )
        msg.html = html_body 
        
        try:
            mail.send(msg)
            return f"Successfully sent monthly report to {len(admin_emails)} admins."
        except Exception as e:
            return f"Failed to send report: {str(e)}"

# --- ROUTE TO TRIGGER EXPORT ---
@app.route('/api/student/export_applications', methods=['POST'])
@jwt_required()
def trigger_export():
    user_id = get_jwt_identity()
    # Send task to the Celery queue asynchronously
    task = export_csv_task.delay(user_id)
    return jsonify({"task_id": task.id}), 202

# --- ROUTE TO CHECK STATUS ---
@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = export_csv_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({"state": task.state, "status": "Pending..."})
    elif task.state != 'FAILURE':
        return jsonify({"state": task.state, "result": task.info})
    else:
        return jsonify({"state": task.state, "status": str(task.info)})
    
# ==========================================
# CELERY BEAT SCHEDULE
# ==========================================
# This tells Celery what to run and when to run it
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.send_daily_reminders',
        'schedule': crontab(), 
    },
    'send-monthly-admin-report': {
        'task': 'app.send_monthly_admin_report',
        # Runs on the 1st day of every month at 8:00 AM
        #'schedule': crontab(day_of_month='1', hour=8, minute=0),
        'schedule': crontab(), 
    }
}
celery.conf.timezone = 'Asia/Kolkata'


# ==========================================
# ERROR HANDLERS
# ==========================================

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Signature validation failed", "error": error}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request does not contain an access token.", "error": error}), 401

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"] 
    return User.query.get(identity) 

@jwt.user_lookup_error_loader
def custom_user_lookup_error(_jwt_header, _jwt_data):
    return jsonify({"error": "Account no longer exists. Please log in again."}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)