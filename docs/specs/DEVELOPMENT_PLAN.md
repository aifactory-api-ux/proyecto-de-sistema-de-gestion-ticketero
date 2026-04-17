# DEVELOPMENT PLAN: PROYECTO DE SISTEMA DE GESTION TICKETERO

## 1. ARCHITECTURE OVERVIEW

**System Components:**
- **Backend (FastAPI, Python 3.11):**
  - REST API for ticket management (create, list, status, update)
  - Telegram bot integration for notifications and status queries
  - SQLite database for persistence
  - Structured logging, healthcheck, environment validation
- **Frontend (HTML5, CSS3, JS, Bootstrap 5):**
  - Static web app for ticket creation, status viewing, and operator panel
  - Vanilla JS state management (window.tickets, window.currentTicket, etc.)
  - Bootstrap-based responsive UI
- **Infrastructure:**
  - Dockerized backend and frontend
  - docker-compose for orchestration, healthchecks, and environment management
  - .env.example for all required environment variables

**Folder Structure:**
```
project-root/
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── telegram_bot.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tickets.py
│   │   └── telegram.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── utils.py
│   └── start.sh
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── main.js
│   ├── styles.css
│   └── start.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── run.sh
├── README.md
└── docs/
    └── architecture.md
```

**Data Contracts:**  
- All backend models in `backend/shared/models.py` (Pydantic)
- All frontend types in `frontend/types.ts` (for future expansion)

**API Endpoints:**  
- `/api/tickets` (POST, GET)
- `/api/tickets/{ticket_id}/status` (GET)
- `/api/tickets/{ticket_id}` (PATCH)
- `/api/telegram/status` (POST)
- `/api/telegram/notify` (POST)

**Frontend State:**  
- `window.tickets`, `window.currentTicket`, `window.loading`, `window.error`
- Functions: `createTicket`, `getAllTickets`, `getTicketStatus`
- Components: TicketForm, TicketStatus, TicketList, ErrorAlert

**Ports:**  
- Backend: 8001  
- Frontend: 8080

## 2. ACCEPTANCE CRITERIA

1. Users can create a ticket via the web interface and receive their ticket number and position in the queue.
2. Operators can view all tickets, activate the next ticket, and mark tickets as attended via the operator panel.
3. Users with a Telegram ID receive notifications when their ticket is assigned or updated.
4. The Telegram bot can respond to status queries and send notifications via webhook.
5. All services run via Docker Compose, with healthchecks and environment validation, and are accessible at the documented URLs.
6. All endpoints validate input, return correct status codes, and never expose internal errors or stack traces.

---

## TEAM SCOPE (MANDATORY — PARSED BY THE PIPELINE)

- **Role:** role-tl (technical_lead)
- **Role:** role-be (backend_developer)
- **Role:** role-fe (frontend_developer)
- **Role:** role-devops (devops_support)

---

## 3. EXECUTABLE ITEMS

---

### ITEM 1: Foundation — shared models, DB schema, config, utilities

**Goal:**  
Establish all shared code and contracts for the project.  
- Define all Pydantic models (data contracts) in `backend/shared/models.py`
- Provide shared package inits
- No TypeScript types needed yet (frontend is JS-only per SPEC)
- No separate shared/config.py needed (env validation is in main.py)
- No SQLAlchemy models (using SQLite via direct queries)
- No separate migration files (schema is managed in code)

**Files to create:**
- backend/shared/__init__.py (create) — package init
- backend/shared/models.py (create) — all Pydantic models: TicketCreate, Ticket, TicketStatusRequest, TicketStatusResponse, TelegramNotification

**Dependencies:** None

**Validation:**  
- `python -c "from backend.shared.models import TicketCreate, Ticket, TicketStatusRequest, TicketStatusResponse, TelegramNotification"` runs without error.

**Role:** role-tl (technical_lead)

---

### ITEM 2: Backend API — ticket endpoints, DB logic, notification utilities

**Goal:**  
Implement all backend logic for ticket management and Telegram integration.  
- FastAPI app entry point and routers
- SQLite DB connection and logic
- Ticket endpoints: create, list, status, update
- Telegram endpoints: status webhook, notify
- Telegram bot logic (python-telegram-bot)
- Notification utility
- Healthcheck endpoint
- Structured logging and env validation
- Backend Dockerfile and start script

**Files to create:**
- backend/Dockerfile (create) — multi-stage, EXPOSE 8001, CMD: uvicorn main:app --host 0.0.0.0 --port 8001
- backend/main.py (create) — FastAPI app, includes healthcheck, loads routers, starts Telegram bot
- backend/database.py (create) — SQLite connection, ticket CRUD, position logic
- backend/telegram_bot.py (create) — Telegram bot logic (start_bot, handle_new_ticket, handle_status_request)
- backend/api/__init__.py (create) — API package init
- backend/api/tickets.py (create) — Ticket endpoints (POST /api/tickets, GET /api/tickets, GET /api/tickets/{ticket_id}/status, PATCH /api/tickets/{ticket_id})
- backend/api/telegram.py (create) — Telegram endpoints (POST /api/telegram/status, POST /api/telegram/notify)
- backend/utils.py (create) — notify_telegram_user utility
- backend/start.sh (create) — startup script for backend container

**Dependencies:** Item 1

**Validation:**  
- `docker build -t backend ./backend` succeeds  
- `docker run -e BACKEND_PORT=8001 ... backend` starts FastAPI on port 8001  
- `curl http://localhost:8001/health` returns status JSON  
- All API endpoints respond as per SPEC.md

**Role:** role-be (backend_developer)

---

### ITEM 3: Frontend — static web app (HTML, JS, CSS, Bootstrap)

**Goal:**  
Implement the static frontend for ticket creation, status viewing, and operator panel.  
- index.html: main page with ticket form, status, ticket list, error alert
- main.js: JS logic for state, API calls, UI updates
- styles.css: custom CSS, Bootstrap overrides
- Frontend Dockerfile and start script

**Files to create:**
- frontend/Dockerfile (create) — multi-stage, serves static files on port 8080
- frontend/index.html (create) — main HTML page, includes Bootstrap, links main.js and styles.css
- frontend/main.js (create) — JS logic: state, API calls, UI updates, components (TicketForm, TicketStatus, TicketList, ErrorAlert)
- frontend/styles.css (create) — custom CSS
- frontend/start.sh (create) — startup script for frontend container

**Dependencies:** Item 1

**Validation:**  
- `docker build -t frontend ./frontend` succeeds  
- `docker run -e FRONTEND_PORT=8080 ... frontend` serves index.html on port 8080  
- Web UI loads, ticket creation and status work, operator panel displays tickets

**Role:** role-fe (frontend_developer)

---

### ITEM 4: Infrastructure & Deployment

**Goal:**  
Provide complete orchestration and documentation for local and production deployment.  
- docker-compose for backend and frontend, with healthchecks and depends_on
- .env.example with all required variables and descriptions
- .gitignore and .dockerignore for clean repo and builds
- run.sh for one-command startup and health validation
- README.md with setup, usage, and endpoint docs
- docs/architecture.md with system diagram and component descriptions

**Files to create:**
- docker-compose.yml (create) — backend (8001), frontend (8080), healthchecks, depends_on
- .env.example (create) — all env vars with descriptions and example values
- .gitignore (create) — excludes __pycache__, *.pyc, node_modules, dist, .env, .DS_Store, *.log
- .dockerignore (create) — excludes .git, node_modules, *.log, dist, __pycache__, *.pyc
- run.sh (create) — checks Docker, builds, starts, waits for healthy, prints URLs
- README.md (create) — prerequisites, setup, run, endpoints, env vars
- docs/architecture.md (create) — architecture diagrams and component descriptions

**Dependencies:** Items 1, 2, 3

**Validation:**  
- `./run.sh` builds and starts all services  
- All containers report healthy  
- Backend API accessible at http://localhost:8001/health  
- Frontend accessible at http://localhost:8080  
- README instructions work end-to-end

**Role:** role-devops (devops_support)

---