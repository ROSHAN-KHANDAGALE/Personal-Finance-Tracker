# Personal Expense Tracker & Financial Planner API

A production-ready backend REST API for **personal finance tracking**, **debt management**, **budgeting**, and **financial planning**. Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL** using clean architecture and user-based data isolation.

---

## Features

| Area | Description |
|------|-------------|
| **Users** | User management (CRUD). All data is scoped per user. |
| **Transactions** | Track income & expenses with date, category, amount, payment mode. |
| **Debts** | Fixed EMI and flexible debts with priority; track remaining amount and payments. |
| **Financial Summary** | Total income, living expenses (excl. Loan/EMI/Debt), mandatory EMI, free cash. |
| **Debt Simulator** | Month-by-month debt clearance simulation (fixed EMI first, then flexible by priority; max 120 months). |
| **Savings Planner** | Target amount + monthly saving power (free cash + total EMI) → months required. |
| **Budgets** | Monthly budgets with category limits; budget vs actual reports. |
| **Recurring Transactions** | Scheduled income/expense templates (daily, weekly, monthly, yearly) with manual scheduler run. |
| **Shared Wallets** | Create wallets, add members with roles; multi-currency support (base currency per wallet). |

---

## Tech Stack

- **Python** 3.10+
- **FastAPI** – REST API
- **SQLAlchemy** – ORM (PostgreSQL)
- **PostgreSQL** – Database
- **Pydantic** – Validation & schemas
- **Uvicorn** – ASGI server
- **python-dotenv** – Environment config

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # DATABASE_URL from env
│   ├── main.py                # FastAPI app, router registration
│   ├── dependencies.py        # get_current_user, get_current_user_id (X-User-Id)
│   │
│   ├── db/
│   │   ├── base.py            # SQLAlchemy Base, naming convention
│   │   ├── database.py        # Engine
│   │   ├── session.py        # SessionLocal, get_db
│   │   └── models.py          # User, Wallet, Transaction, Debt, Payment,
│   │                          # RecurringTransaction, Budget, BudgetCategory, WalletMember
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── debt.py
│   │   ├── planner.py        # FinancialSummary, DebtPlanResponse, etc.
│   │   ├── budget.py
│   │   ├── recurring.py
│   │   └── wallet.py
│   │
│   ├── routes/
│   │   ├── user.py            # /users
│   │   ├── transactions.py    # /transactions
│   │   ├── debts.py           # /debts
│   │   ├── planner.py         # /planner (summary, debt-plan, savings-plan, overview)
│   │   ├── budgets.py         # /budgets
│   │   ├── recurring.py       # /recurring + POST /recurring/run
│   │   └── wallets.py         # /wallets + members
│   │
│   └── services/
│       ├── planner_service.py    # Financial summary, run_financial_planner
│       ├── debt_simulator.py     # simulate_debt_clearance
│       ├── savings_planner.py    # calculate_savings_plan
│       ├── budget_service.py     # Budget CRUD, budget vs actual
│       ├── recurring_service.py  # Recurring CRUD, run_recurring_scheduler
│       └── wallet_service.py    # Wallet CRUD, membership
│
├── requirements.txt
├── .env                        # DATABASE_URL (not committed)
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd "Expense Tracker/backend"
```

### 2. Virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` in the `backend` folder:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
```

### 5. Run the application

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

- API: **http://127.0.0.1:8000**
- Swagger UI: **http://127.0.0.1:8000/docs**
- ReDoc: **http://127.0.0.1:8000/redoc**

---

## Authentication (current)

Until JWT is implemented, the API uses a header-based user context:

- **Header:** `X-User-Id: <valid-user-uuid>`
- All user-scoped endpoints require this header.
- Invalid or missing UUID → 400; unknown user → 404.

Create a user first via `POST /users/`, then use the returned `id` as `X-User-Id` for all other requests.

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Users** | | |
| GET | `/users/` | List users |
| GET | `/users/{user_id}` | Get user |
| POST | `/users/` | Create user |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |
| **Transactions** | | |
| GET | `/transactions/` | List current user's transactions |
| GET | `/transactions/{id}` | Get transaction |
| POST | `/transactions/` | Create transaction |
| PUT | `/transactions/{id}` | Update transaction |
| DELETE | `/transactions/{id}` | Delete transaction |
| **Debts** | | |
| GET | `/debts/` | List current user's debts |
| GET | `/debts/{id}` | Get debt |
| POST | `/debts/` | Create debt |
| PUT | `/debts/{id}` | Update debt |
| DELETE | `/debts/{id}` | Delete debt |
| **Planner** | | |
| GET | `/planner/summary` | Financial summary (income, expenses, EMI, free cash) |
| GET | `/planner/debt-plan` | Debt clearance simulation (monthly breakdown) |
| GET | `/planner/savings-plan?target_amount=` | Months to reach savings target |
| GET | `/planner/overview` | Summary + debt plan combined |
| **Budgets** | | |
| GET | `/budgets/` | List budgets |
| GET | `/budgets/{id}` | Get budget with budget vs actual |
| POST | `/budgets/` | Create budget (name, year, month, categories) |
| PUT | `/budgets/{id}` | Update budget |
| DELETE | `/budgets/{id}` | Delete budget |
| **Recurring** | | |
| GET | `/recurring/` | List recurring transactions |
| GET | `/recurring/{id}` | Get recurring transaction |
| POST | `/recurring/` | Create recurring transaction |
| PUT | `/recurring/{id}` | Update recurring transaction |
| DELETE | `/recurring/{id}` | Delete recurring transaction |
| POST | `/recurring/run` | Run scheduler (materialize due recurrences) |
| **Wallets** | | |
| GET | `/wallets/` | List wallets user belongs to |
| GET | `/wallets/{id}` | Get wallet + current user role |
| POST | `/wallets/` | Create wallet (caller = owner) |
| PUT | `/wallets/{id}` | Update wallet (owner only) |
| DELETE | `/wallets/{id}` | Delete wallet (owner only) |
| POST | `/wallets/{id}/members?member_user_id=&role=` | Add/update member (owner only) |
| DELETE | `/wallets/{id}/members/{member_user_id}` | Remove member (owner only) |

---

## Core Business Logic

- **Financial summary**
  - **Total income:** Sum of transactions with `type == "Income"`.
  - **Living expenses:** Sum of expenses excluding categories `Loan`, `EMI`, `Debt`.
  - **Mandatory EMI:** Sum of `emi_amount` for debts where `is_flexible == False`.
  - **Free cash:** `Income − Living expenses − Mandatory EMI`.

- **Debt simulator**
  - Fixed EMI paid first each month; remaining free cash goes to flexible debts by priority.
  - Stops when all debts are cleared or after 120 months.
  - Returns full monthly breakdown.

- **Savings planner**
  - **Monthly saving power:** `free_cash + total_emi` (all EMIs).
  - **Months required:** `ceil(target_amount / monthly_saving_power)`.

---

## Example Flow

1. **Create user**
   ```http
   POST /users/
   Content-Type: application/json
   { "email": "user@example.com", "password_hash": "***", "name": "Jane" }
   ```
   Use the response `id` as `X-User-Id` in subsequent requests.

2. **Add income and expenses**
   ```http
   POST /transactions/
   X-User-Id: <user-uuid>
   { "date": "2026-02-01", "type": "Income", "category": "Salary", "amount": 80000 }
   POST /transactions/
   { "date": "2026-02-05", "type": "Expense", "category": "Groceries", "amount": 5000 }
   ```

3. **Add debts**
   ```http
   POST /debts/
   X-User-Id: <user-uuid>
   { "creditor_name": "Home Loan", "total_amount": 5000000, "remaining_amount": 4800000,
     "emi_amount": 45000, "is_flexible": false, "priority": 1 }
   ```

4. **Get plan**
   ```http
   GET /planner/summary          → income, expenses, EMI, free_cash
   GET /planner/debt-plan       → monthly clearance breakdown
   GET /planner/savings-plan?target_amount=500000
   ```

5. **Optional: budget and recurring**
   ```http
   POST /budgets/
   { "name": "Feb 2026", "year": 2026, "month": 2,
     "categories": [ { "category": "Groceries", "limit_amount": 8000 } ] }
   POST /recurring/
   { "type": "Expense", "category": "Rent", "amount": 20000,
     "frequency": "monthly", "start_date": "2026-02-01" }
   POST /recurring/run   # Materialize due recurrences into transactions
   ```

---

## Design Notes

- **Clean architecture:** Routes are thin; business logic lives in services.
- **User isolation:** All financial data is filtered by `user_id` from `X-User-Id`.
- **UUIDs:** Generated server-side; used for all primary and foreign keys.
- **No hardcoded user IDs:** User context comes from dependencies only.
- **Pydantic:** Request/response schemas align with DB models where applicable.
- **Wallets:** Optional `wallet_id` on transactions, debts, budgets, recurring; ready for wallet-scoped features later.

---

## Future Enhancements

- JWT (or OAuth2) authentication replacing `X-User-Id`.
- Wallet-scoped queries when `X-Wallet-Id` or similar is provided.
- FX rates and conversion for multi-currency wallets.
- Background job (e.g. Celery) for automatic recurring scheduler.
- Alerts (budget threshold, EMI due, low free cash).
- Export (CSV/PDF) and reporting.

---

## License & Contribution

Use and extend as needed for your project. Contributions welcome via fork and pull request.
