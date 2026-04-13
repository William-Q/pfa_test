# PennyWise — Local-First Personal Finance App

PennyWise is a local-first personal finance starter app you can run on your own machine using Docker.
It is designed for privacy, fast local development, and an easy onboarding flow.

## Tech Stack

- **Backend API:** FastAPI (Python)
- **Frontend UI:** Streamlit (Python)
- **Database:** PostgreSQL
- **Containerization & orchestration:** Docker + Docker Compose

## Project Structure

```text
.
├── app/                  # FastAPI application package
├── backend/              # Backend Dockerfile + requirements
├── frontend/             # Streamlit app + Dockerfile
├── docker-compose.yml    # Multi-service orchestration
├── .env.sample           # Optional environment variable template
└── README.md
```

## Prerequisites

Install the following on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

> Note: Newer Docker installs include Compose as `docker compose`.

## Setup Steps

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd pfa_test
   ```

2. **Create an environment file (optional but recommended)**

   ```bash
   cp .env.sample .env
   ```

   Edit `.env` if you want to override defaults (DB credentials, app settings, etc.).

3. **Build and start all services**

   ```bash
   docker compose up --build
   ```

4. **Run in detached mode (optional)**

   ```bash
   docker compose up --build -d
   ```

5. **Stop services**

   ```bash
   docker compose down
   ```

6. **Stop and remove DB volume (reset local data)**

   ```bash
   docker compose down -v
   ```

## Running with Docker Compose

The main command to run the full app stack:

```bash
docker compose up --build
```

Useful Compose commands:

```bash
# Show service status
docker compose ps

# View logs for all services
docker compose logs -f

# View logs for a single service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Restart a service
docker compose restart backend
```

## Services and Ports

When the stack is up, these services are available:

- **Frontend (`frontend`)**
  - **Container role:** Streamlit user interface
  - **Local URL:** `http://localhost:8501`
  - **Container port:** `8501`
  - **Purpose:** Interactive dashboard/UI for entering and viewing finance data.

- **Backend (`backend`)**
  - **Container role:** FastAPI REST API
  - **Local URL:** `http://localhost:8000`
  - **Container port:** `8000`
  - **Useful endpoints:**
    - OpenAPI docs: `http://localhost:8000/docs`
    - Readiness check: `http://localhost:8000/api/v1/health/ready`
  - **Purpose:** Business logic + API layer used by the frontend.

- **Database (`db`)**
  - **Container role:** PostgreSQL database
  - **Port exposure:** Managed by Docker Compose for local app use
  - **Data persistence:** Stored in a named Docker volume (`postgres_data`)
  - **Purpose:** Persistent storage for transactions, categories, budgets, etc.

## Networking and Data Persistence

- All services share a Docker network (`app_net`), so containers can communicate by service name.
  - Example: frontend can call backend at `http://backend:8000` inside the network.
- PostgreSQL data persists across restarts using the named volume `postgres_data`.

## Quick Access URLs

- **Streamlit app:** `http://localhost:8501`
- **FastAPI docs:** `http://localhost:8000/docs`
- **Health check:** `http://localhost:8000/api/v1/health/ready`

---

If you want, I can also add a **Troubleshooting** section (common Docker, port, and DB connection issues).
