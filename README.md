# PennyWise

Dockerized starter stack for a personal finance app with:
- **FastAPI** backend (`http://localhost:8000`)
- **Streamlit** frontend (`http://localhost:8501`)
- **PostgreSQL** database with persisted volume data

## Included setup

- `docker-compose.yml` with three services: `frontend`, `backend`, and `db`
- `backend/Dockerfile` for FastAPI + Uvicorn
- `frontend/Dockerfile` for Streamlit
- Named Postgres volume (`postgres_data`) for persistence
- Shared network (`app_net`) so the frontend can call the backend using `http://backend:8000`

## Run

From the repo root:

```bash
docker compose up --build
```

Then open:
- Frontend: `http://localhost:8501`
- Backend docs: `http://localhost:8000/docs`
- Backend health endpoint: `http://localhost:8000/api/v1/health/ready`

## Troubleshooting (Windows / Docker Desktop)

If you see an error like:

`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`

it means the Docker daemon is not running (or Docker Desktop is not in Linux container mode).

1. Start **Docker Desktop** and wait until it shows "Engine running".
2. Ensure it is using **Linux containers**.
3. Verify connectivity:
   ```bash
   docker version
   docker info
   ```
4. Retry:
   ```bash
   docker compose up --build
   ```

## Optional environment overrides

The compose file is runnable with defaults, but you can override values by creating a `.env` file (use `.env.sample` as a template).
