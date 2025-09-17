### `backend/README.md`
```md
# SplitApp API — Quick Start

## 1) Create venv & install
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .

## 2) Run
uvicorn app.main:app --reload --port 8000

## 3) Try it
- Open docs: http://localhost:8000/docs
- Register -> Login -> Authorize (top-right in Swagger)
- Create a group
- Add an expense with splits
- Get /groups/{id}/balances and /settlements

### Notes
- Default DB: SQLite (file `splitapp.db`). Set `DATABASE_URL` to PostgreSQL for prod, e.g. `postgresql+asyncpg://user:pass@host/db`.
- Set `JWT_SECRET` in env for security.
```
