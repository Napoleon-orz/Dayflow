# Dayflow — HR Management Backend

Dayflow is an HR management system backend built with Flask and SQLAlchemy, backed by a MySQL database. It handles employee authentication, profiles, attendance, leave requests, payroll, and notifications.

## Tech Stack

- **Framework:** Flask
- **ORM:** Flask-SQLAlchemy
- **Database:** MySQL
- **Auth:** JWT (PyJWT) + Flask-Bcrypt for password hashing
- **Environment config:** python-dotenv

## Project Structure

Backend/
├── src/
│ ├── attendance/ # Attendance model & routes
│ ├── auth/ # Auth controller, routes, decorators (protect, require_admin)
│ ├── leave/ # Leave request model & routes
│ ├── models/
│ │ ├── user.py # User model
│ │ └── employee.py # Employee-related model
│ ├── notification/ # Notification model & routes
│ ├── payroll/ # Payroll model & routes
│ ├── profile/ # Profile model & routes
│ ├── reports/ # Report logging model & routes
│ ├── init.py # App factory (create_app)
│ ├── config.py # App configuration (reads .env)
│ └── extensions.py # Shared extensions: db, bcrypt
├── .env # Environment variables (not committed)
├── run.py # App entry point
├── seed_data.py # Populates DB with sample data
└── README.md


## Setup

### 1. Clone and create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # on Linux/Mac
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in `Backend/`:

SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:3306/<db_name>
JWT_SECRET=your-jwt-secret
PORT=5000


### 4. Create the database tables

Tables are created automatically when running the seed script, or manually via:

```python
from src import create_app
from src.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
```

### 5. Seed sample data (optional)

Populates the database with sample users, profiles, attendance, leave, payroll, and notification records:

```bash
python seed_data.py
```

Default password for all seeded users: `Password@123`

### 6. Run the server

```bash
python run.py
```

Server runs on `http://localhost:5000` by default.

## User Roles

Roles are auto-derived from email address at signup:
- Emails containing `odooadmin` → `admin`
- Emails containing `odoo` (but not `odooadmin`) → `employee`

## API Overview

| Module        | Base Route         | Notes                                  |
|---------------|---------------------|-----------------------------------------|
| Auth          | `/api/auth`          | Signup, login, JWT issuance             |
| Profile       | `/api/profile`        | Own profile (self) + admin access to any employee's profile |
| Attendance    | `/api/attendance`      | Check-in/out records                    |
| Leave         | `/api/leave`            | Leave requests + admin approval          |
| Payroll       | `/api/payroll`           | Salary records per pay period            |
| Notifications | `/api/notification`       | User notifications                        |
| Reports       | `/api/reports`             | Generated report logs                     |

All protected routes require:

Authorization: Bearer <token>


## License

Internal project — license TBD.
