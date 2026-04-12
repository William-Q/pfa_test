# PennyWise

A production-ready starter structure for a **personal finance app** with:
- **FastAPI** backend
- **Streamlit** frontend
- **PostgreSQL** database
- **Docker Compose** orchestration

## Project Structure

```text
.
├── backend/                 # FastAPI service
├── frontend/                # Streamlit UI service
├── tests/                   # Test suite placeholders
├── docker-compose.yml       # Multi-service local/prod-like setup
└── .env.sample              # Environment variable template
```

## Quick Start

1. Copy environment template:
   ```bash
   cp .env.sample .env
   ```
2. Build and run services:
   ```bash
   docker compose up --build
   ```
3. Open:
   - API docs: `http://localhost:${BACKEND_PORT:-8000}/docs`
   - UI: `http://localhost:${FRONTEND_PORT:-8501}`

## Notes

- Replace placeholder modules with real domain logic (accounts, budgets, transactions, goals).
- Add migrations (Alembic) and secret management before production deployment.
