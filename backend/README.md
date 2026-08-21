# SportIQ AI Talent Platform — Backend

Enterprise-grade sports analytics and talent identification backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

---

## Tech Stack
* **Language:** Python 3.12+
* **Framework:** FastAPI (ASGI)
* **ORM:** SQLAlchemy 2.0
* **Database:** PostgreSQL (with SQLite support for local dev/testing)
* **Migrations:** Alembic
* **Security:** OAuth2 Password Bearer, JWT, Passlib (bcrypt)
* **Data Science / AI:** Scikit-learn, Pandas, NumPy

---

## Directory Structure
```text
backend/
├── app/
│   ├── ai/            # AI Talent scoring, preprocessing & predictions
│   ├── core/          # Configuration, security, permissions & settings
│   ├── database/      # Session management & declarative base
│   ├── models/        # SQLAlchemy ORM models (7 core tables)
│   ├── routes/        # Versioned API endpoints (/api/v1/...)
│   ├── schemas/       # Pydantic validation & response schemas
│   ├── services/      # Business logic & repository services
│   └── main.py        # Application bootstrap & middleware
├── alembic/           # Database migration revisions
├── tests/             # Pytest test suite
├── .env               # Environment configuration
├── requirements.txt   # Dependencies list
└── server.py          # Development server runner
```

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy `.env.example` to `.env` and configure your database connection string:
```bash
cp .env.example .env
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation is accessible at `http://localhost:8000/docs`.
