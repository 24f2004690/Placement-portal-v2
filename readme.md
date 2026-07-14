# Campus Placement Management System (CPMS)

A full-stack, asynchronous web application designed to streamline the campus placement process for Students, Recruiters, and University Admins.

Built with a **Vue 3** frontend and a **Flask** backend, this project leverages **Redis** and **Celery** for advanced caching, background job processing, and automated email scheduling.

## Key Features

* **Role-Based Access Control (RBAC):** Distinct dashboards and permissions for Admins, Companies, and Students using JWT Authentication.
* **Lightning Fast API:** Heavy database queries (like student directories) are cached in memory using **Redis**, dropping response times from ~50ms to ~2ms.
* **Asynchronous Tasks:** CSV data exports are handed off to a **Celery** background worker, allowing the UI to remain responsive while polling for the download link.
* **Automated Email Reminders:** A Celery Beat scheduler automatically emails students about placement drives closing within 24 hours.
* **Automated Reporting:** Generates and emails a beautifully formatted HTML activity report to Admins on the 1st of every month.
* **Bulletproof Session Security:** Custom global fetch interceptors and JWT lookup loaders ensure deleted users or expired sessions are instantly and securely logged out.

## Tech Stack

**Frontend:**
* Vue 3 (Composition API) & Vue Router
* Bootstrap 5 & Bootstrap Icons
* Chart.js & vue-chartjs (Data Visualization)

**Backend:**
* Python 3 / Flask
* Flask-SQLAlchemy (ORM) & SQLite
* Flask-JWT-Extended (Authentication)
* Flask-Caching & Redis (Cache & Message Broker)
* Flask-Mail (SMTP Emails)
* Celery & Celery Beat (Background Jobs & Cron Scheduling)

---

## Local Setup & "How to Run" Guide

Because this project uses **Celery** and **Redis**, the backend is designed to run in a dual-environment setup on Windows: the main API runs on Windows, while the background workers run in **WSL (Windows Subsystem for Linux)**.

To run this application, you will need **three separate terminal windows** open simultaneously.

### Prerequisites

* **Node.js** (v16+)
* **Python** (3.8+)
* **WSL (Ubuntu)** installed on Windows (or a native Linux/Mac environment)
* **Redis Server** installed inside your WSL/Linux environment

### Step 1: Clone and Configure Environment

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/cpms.git
   cd cpms
   ```

2. Navigate to the `backend` folder and create a `.env` file:

   ```bash
   cd backend
   touch .env
   ```

3. Add the following variables to your `.env` file:

   ```env
   MAIL_USERNAME=your_gmail@gmail.com
   MAIL_PASSWORD=your_16_char_google_app_password
   JWT_SECRET_KEY=your_super_secret_jwt_key
   ```

   > **Note:** You must generate an App Password from your Google Account Security settings to use the email features.

4. Initialize the database:
   run python `init_db.py` in the backend folder to create admin and initialize the database

   > **Note:** Change the credentials for admin accordingly.

### Step 2: Terminal 1 — Run the Vue Frontend

Open a standard command prompt or PowerShell window.

```bash
cd cpms/frontend
npm install
npm run dev
```

Leave this terminal running. The frontend will be accessible at `http://localhost:5173` (or the port Vite assigns).

### Step 3: Terminal 2 — Run the Flask API (Windows)

Open a second standard command prompt or PowerShell window.

```bash
cd cpms/backend
python -m venv venv

# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt

# Run the Flask server
python app.py
```

Leave this terminal running. The backend API will be accessible at `http://127.0.0.1:5000`.

### Step 4: Terminal 3 — Run Redis and Celery Workers (WSL / Linux)

Celery does not officially support Windows, so the workers must run in Linux/WSL to function properly.

1. Open your **WSL / Ubuntu terminal**.

2. Navigate to the backend folder of your project (WSL maps your C: drive to `/mnt/c/`):

   ```bash
   cd /mnt/c/path/to/your/cpms/backend
   ```

3. Start the Redis server:

   ```bash
   sudo service redis-server start
   ```

4. Create a Linux-specific virtual environment and install dependencies:

   ```bash
   python3 -m venv venv_wsl
   source venv_wsl/bin/activate
   pip install -r requirements.txt
   ```

5. Start the Celery worker and Beat scheduler together:

   ```bash
   celery -A app.celery worker -B --loglevel=info
   ```

Leave this terminal running. You should see logs indicating Celery has connected to Redis and is ready to accept tasks.

### Step 5: Access the App

With all three terminals running, open your browser and navigate to the frontend URL (usually `http://localhost:5173`). Register an Admin account to begin setting up placement drives!

---

## License

This project is licensed under the MIT License. Feel free to use it!