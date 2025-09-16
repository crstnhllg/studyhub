# StudyHub

A FastAPI-based backend for managing study groups, subjects, memberships, and study sessions with role-based access control.

---

## Features

- User registration and authentication (JWT-based).
- Create, read, update, and delete study groups.
- Role-based memberships: Creator, Admin, Member.
- Manage subjects within study groups.
- Create, update, and view study sessions.
- Partial updates with Pydantic models.
- Secure password handling with bcrypt.

---

## Tech Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** JWT + OAuth2
- **Password Hashing:** bcrypt
- **Validation:** Pydantic

---

## Setup

1. Clone the repo:

```bash
git clone https://github.com/crstnhllg/studyhub.git
cd studyhub 
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Set environment variables:

```
KEY=<your_jwt_secret_key>
URL=<your_database_url>
```

4. Run the app:

```
uvicorn main:app --reload
```

API docs available at: http://127.0.0.1:8000/docs
