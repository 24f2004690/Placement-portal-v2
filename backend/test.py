from app import app, db
from models import User, Student, Company, PlacementDrive, Application
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt = Bcrypt(app)

def seed_database():
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # NOTE: Make sure you've run your init_db.py to create the tables first!

        # ---------------------------------------------------------
        # 1. SEED STUDENTS
        # ---------------------------------------------------------
        print("Creating 5 Students...")
        students = []
        for i in range(1, 6):
            # Create User account for student
            user = User(
                username=f"student{i}",
                email=f"student{i}@test.com", 
                password_hash=bcrypt.generate_password_hash(f"student{i}").decode('utf-8'), 
                role='student'
            )
            db.session.add(user)
            db.session.flush() # Flush to assign an ID to the user before linking

            # Create Student Profile
            student = Student(
                user_id=user.id,
                full_name=f"Test Student {i}",
                branch="Computer Science" if i % 2 == 0 else "Information Technology",
                cgpa=7.0 + (i * 0.5), # Creates CGPAs from 7.5 to 9.5,
                experience=f"Interned at Company {i} for 3 months.",
                phone=f"987654321{i}"
            )
            db.session.add(student)
            students.append(student)

        # ---------------------------------------------------------
        # 2. SEED COMPANIES
        # ---------------------------------------------------------
        print("Creating 5 Companies...")
        companies = []
        for i in range(1, 6):
            # Create User account for company
            user = User(
                username=f"company{i}",
                email=f"company{i}@test.com", 
                password_hash=bcrypt.generate_password_hash(f"company{i}").decode('utf-8'), 
                role='company'
            )
            db.session.add(user)
            db.session.flush()

            # Create Company Profile
            company = Company(
                user_id=user.id,
                name=f"Tech Corp {i}",
                is_approved=True # Auto-approve for testing
            )
            db.session.add(company)
            companies.append(company)
            
        db.session.commit()

        # ---------------------------------------------------------
        # 3. SEED PLACEMENT DRIVES
        # ---------------------------------------------------------
        print("Creating 5 Placement Drives...")
        drives = []
        for i, company in enumerate(companies, start=1):
            # Set deadline 10 to 50 days in the future
            future_date = (datetime.now() + timedelta(days=i*10)).strftime('%Y-%m-%d')
            
            drive = PlacementDrive(
                company_id=company.id,
                job_title=f"Software Engineer Role {i}",
                job_description=f"We are looking for passionate developers to join {company.name}. Competitive salary and benefits.",
                eligibility_criteria="B.Tech CS/IT, No active backlogs.",
                application_deadline=future_date,
                status='Approved'
            )
            db.session.add(drive)
            drives.append(drive)

        db.session.commit()

        # ---------------------------------------------------------
        # 4. SEED APPLICATIONS
        # ---------------------------------------------------------
        print("Creating 5 Applications...")
        # We will cycle through statuses to give you a variety to look at
        statuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
        
        for i in range(5):
            app_status = statuses[i]
            
            # If the status is 'Interview Scheduled', give it a date 2 days from now
            interview_dt = None
            if app_status == 'Interview Scheduled':
                interview_dt = datetime.now() + timedelta(days=2) 
                
            application = Application(
                student_id=students[i].id,
                drive_id=drives[i].id,
                status=app_status,
                remarks=f"System auto-generated remark for Student {i+1}.",
                interview_date=interview_dt  # Testing our new database column!
            )
            db.session.add(application)

        db.session.commit()
        print("✅ Database successfully seeded!")
        print("-" * 40)
        print("🔑 TEST CREDENTIALS:")
        print("Students : student1@test.com  -> student5@test.com  | Pass: student1 -> student5")
        print("Companies: company1@test.com  -> company5@test.com  | Pass: company1 -> company5")
        print("-" * 40)

if __name__ == '__main__':
    seed_database()