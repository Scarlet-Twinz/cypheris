# Cypheris

**Decode Your Security.**

Cypheris is a security intelligence and infrastructure visibility platform designed to turn telemetry, security events, sensor data, integrations, and AI-assisted analysis into an operational security command layer.

The platform is organized around **Cypheris Core**, the security platform powered by **PNSTAP™**, with **Cypheris Sentinel** providing the command-center experience and **LYROMI** providing the AI intelligence layer.

## Platform

### Cypheris Core
The platform foundation for organization workspaces, authentication, security telemetry, alerts, sensors, integrations, auditability, and operational security data.

### Cypheris Sentinel
The web command center for security visibility. The dashboard consumes authenticated API telemetry and presents workspace-scoped security activity, alerts, network-flow information, sensor state, and operational indicators.

### PNSTAP™
The telemetry and processing foundation around which Cypheris collects and exposes network/security signals.

### LYROMI
Cypheris' AI intelligence layer. LYROMI is integrated into the backend as a service-oriented reasoning and analysis system and can use a local Ollama model for development deployments.

## Core capabilities

- Organization/workspace creation and isolation
- Password hashing and JWT-based authentication
- Workspace-scoped dashboard telemetry
- Security alerts and activity feeds
- Network-flow telemetry
- Sensor enrollment and heartbeat tracking
- Cloud/security API integration records
- PostgreSQL persistence and indexed security data
- AI-assisted LYROMI analysis
- React/Vite command-center interface
- Cesium-ready visualization components
- Docker-based API, frontend, and PostgreSQL stack

## Architecture

```text
                         +----------------------+
                         |   Cypheris Sentinel  |
                         | React + Vite + UI    |
                         +----------+-----------+
                                    |
                           Bearer-authenticated API
                                    |
                         +----------v-----------+
                         |   FastAPI / Core API |
                         | Auth | Dashboard     |
                         | Sensors | Integrations|
                         +----+-----------+-----+
                              |           |
                       +------v---+   +---v------+
                       |PostgreSQL|   |  LYROMI  |
                       | security |   | AI layer |
                       | telemetry|   | Ollama   |
                       +----------+   +----------+
                              ^
                              |
                         PNSTAP telemetry
```

## Repository layout

```text
pnstap-platform/
├── analytics-hub-python/     # FastAPI backend and LYROMI services
├── dashboard-ui-react/       # React/Vite security command center
├── database/                 # PostgreSQL schema and data definitions
├── deployment/docker/        # Dockerfiles, Compose stack and nginx config
├── docs/                     # Architecture and product documentation
├── assets/                   # Platform assets
├── scripts/                  # Operational scripts
└── ingestion-engine-cpp/     # Telemetry ingestion layer
```

## Technology stack

| Layer | Technology |
|---|---|
| Web application | React, Vite, React Router |
| Visualization | Recharts, Cesium |
| API | Python, FastAPI, Pydantic |
| Authentication | JWT, bcrypt/Passlib |
| Database | PostgreSQL |
| AI | LYROMI + local Ollama integration |
| Containers | Docker, Docker Compose |
| Web serving | Nginx |
| Source control | Git, GitHub |

## Local development

### 1. Backend

```bash
cd analytics-hub-python/src
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and provide a strong `SECRET_KEY` and PostgreSQL credentials.

Run the API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API health check:

```text
GET /health
```

### 2. Database

Create a PostgreSQL database named `pnstap` and run:

```bash
psql -U postgres -d pnstap -f database/init.sql
```

The initialization script is reset-oriented and drops the Cypheris application tables before recreating them. Do not use it against data that must be preserved.

### 3. Frontend

```bash
cd dashboard-ui-react
npm ci
```

Create `.env` from `.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then:

```bash
npm run dev
```

## Docker

The Compose stack provides PostgreSQL, the FastAPI service, and the React/Nginx frontend.

```bash
cd deployment/docker
docker compose up --build
```

Set `SECRET_KEY` in the environment before starting the stack. For deployments behind a reverse proxy, set `VITE_API_BASE_URL` and `CORS_ORIGINS` to the appropriate public origins.

## API surface

| Endpoint | Purpose | Access |
|---|---|---|
| `GET /health` | Service health | Public |
| `GET /database` | Database connectivity check | Public |
| `POST /auth/signup` | Create organization + administrator | Public |
| `POST /auth/login` | Authenticate a user | Public |
| `GET /api/dashboard/` | Workspace security telemetry | Bearer token |
| `POST /api/lyromi/chat` | LYROMI intelligence request | Bearer token |
| `/api/sensors/*` | Sensor enrollment and telemetry lifecycle | Mixed: user/sensor credentials |
| `/api/integrations/*` | Cloud/security integration lifecycle | Authenticated platform access |

## Security model

Cypheris treats the authenticated `company_id` in the signed access token as the workspace boundary for dashboard data. The frontend sends the bearer token with protected API requests, while the backend validates the token before serving protected dashboard and LYROMI operations.

Secrets and local environment files are excluded from source control. Public configuration is represented through `.env.example` files.

This repository contains the platform implementation and infrastructure needed for development and deployment. Production operation still requires environment-specific controls such as secret management, TLS termination, network policy, monitoring, backups, database migration strategy, rate limiting, and an appropriate deployment environment.

## Product direction

Cypheris is designed to grow into a broader security operations platform with richer threat intelligence, deeper telemetry ingestion, security analytics, automated investigation workflows, organization controls, expanded integrations, reporting, and commercial workspace capabilities.

The roadmap is intentionally separated from claims about already-implemented functionality: the repository documents what the current code actually provides while leaving room for the platform to evolve.

## Engineering principles

- **Workspace isolation:** security data belongs to an authenticated organization context.
- **Configuration over hard-coding:** service URLs and deployment settings come from environment configuration.
- **Observable infrastructure:** telemetry, alerts, sensors, and activity are first-class platform data.
- **Security by default:** credentials are hashed, protected endpoints require authentication, and secrets stay out of source control.
- **Product-first architecture:** Cypheris is structured as a platform that can evolve independently of a single demo or UI screen.

## License

No open-source license has been declared for this repository yet. Until a license is added, default copyright protections apply.
