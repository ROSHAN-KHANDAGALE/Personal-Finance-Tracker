# Personal Finance Planner API

A backend REST API for managing **users, transactions, debts, and financial planning**.  
Built using **FastAPI**, **SQLAlchemy**, and **PostgreSQL** with a modular structure.

---

## 🚀 Features

- User management
- Income & expense tracking
- Debt tracking
- Financial planning logic
- PostgreSQL database with UUID-based models
- Clean modular architecture
- Ready for frontend or mobile app integration

---

## 🧱 Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Pydantic
- Uvicorn

---

## 📂 Project Structure

```
app/
│
├── db/
│   ├── base.py
│   ├── database.py
│   ├── models.py
│   ├── session.py
│
├── schemas/
│   ├── user.py
│   ├── transactions.py
│   ├── debts.py
│   └── planner.py
│
├── routes/
│   ├── user.py
│   ├── transactions.py
│   ├── debts.py
│   └── planner.py
│
├── services/
│   ├── debt_simulator.py
│   ├── planner_service.py
│   ├── savings_planner.py
|
├── .env
├── .gitignore
├── main.py
├── config.py
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd finance-planner
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Configuration

Create a PostgreSQL database and update your connection string:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/<db-name>
```

---

## ▶️ Run the Application

```bash
uvicorn app.main:app --reload
```

Server will start at:
```
http://127.0.0.1:8000
```

---

## 📘 API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## ⚠️ Important Notes

- Users **must exist before** creating transactions or debts.
- Foreign key errors occur if `user_id` does not exist.

---

## 🧪 Example Flow

1. Create User → `/users/`
2. Add Transactions → `/transactions/`
3. Add Debts → `/debts/`
4. Generate Plan → `/planner/`

---

## 🛠️ Future Enhancements

1. Authentication (JWT)
2. Monthly reports
3. Budget alerts
4. Frontend dashboard
5. AI-based financial advice

---

## 🤝 Contribution

Feel free to fork, improve, and raise PRs.

---
