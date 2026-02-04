# College Information Portal - Setup Guide

Django-based web application for managing college operations including student/teacher management, attendance tracking, assignments, exam routines, and notifications.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to project directory
cd "/home/neupane/Downloads/college-information-portal-main (3)/college-information-portal-main"

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required Packages:**
- Django>=5.0,<6.0
- django-widget-tweaks>=1.5.0
- Pillow>=10.0.0
- python-dotenv==1.2.1

### 3. Configure Environment Variables

Update the `.env` file with your email credentials:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Gmail App Password Setup:**
1. Go to Google Account Settings → Security
2. Enable 2-Step Verification
3. Go to App Passwords → Generate new password
4. Copy the 16-character password to `.env`

### 4. Database Setup

**For fresh installation (first time setup):**

```bash
# Initialize database with default admin user
python init_db.py
```

**Default Admin Credentials:**
- Email: `admin@shankerdev.edu`
- Password: `adminpassword123`

**For existing database:**

```bash
# Apply any pending migrations
python manage.py migrate
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run server on port 8080
python manage.py runserver 8080
```

**Access the application:**
- Local: http://127.0.0.1:8080
- Admin Panel: http://127.0.0.1:8080/admin

## Troubleshooting

**Database Locked Error:**
```bash
pkill -f runserver
python manage.py runserver 8080
```

**Static Files Not Loading:**
```bash
python manage.py collectstatic --clear --noinput
```

**Email Not Sending:**
- Verify Gmail App Password in `.env`
- Ensure 2-Step Verification is enabled on Gmail

**Migration Errors:**
```bash
python manage.py migrate --fake-initial
```

