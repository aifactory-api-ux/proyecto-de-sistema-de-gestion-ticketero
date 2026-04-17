# SPEC.md

## 1. TECHNOLOGY STACK

- **Backend**
  - Python 3.11
  - FastAPI 0.110.0
  - Pydantic 2.6.4
  - python-telegram-bot 20.7
  - SQLite 3 (via Python’s sqlite3 module)
- **Frontend**
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - Bootstrap 5.3.3
- **Infrastructure**
  - Docker 26.0.0
  - Docker Compose 2.27.0

---

## 2. DATA CONTRACTS

### Python (Pydantic Models)

```python
# backend/shared/models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TicketCreate(BaseModel):
    user_name: str = Field(..., max_length=100)
    telegram_id: Optional[int] = None

class Ticket(BaseModel):
    id: int
    user_name: str
    telegram_id: Optional[int] = None
    number: int
    status: str
    created_at: datetime
    updated_at: datetime

class TicketStatusRequest(BaseModel):
    ticket_id: int

class TicketStatusResponse(BaseModel):
    ticket_id: int
    position: int
    status: str
    number: int

class TelegramNotification(BaseModel):
    telegram_id: int
    message: str
```

### TypeScript (for future frontend expansion, field-for-field identical)

```typescript
// frontend/types.ts

export interface TicketCreate {
    user_name: string;
    telegram_id?: number;
}

export interface Ticket {
    id: number;
    user_name: string;
    telegram_id?: number;
    number: number;
    status: string;
    created_at: string; // ISO 8601
    updated_at: string; // ISO 8601
}

export interface TicketStatusRequest {
    ticket_id: number;
}

export interface TicketStatusResponse {
    ticket_id: number;
    position: number;
    status: string;
    number: number;
}

export interface TelegramNotification {
    telegram_id: number;
    message: string;
}
```

---

## 3. API ENDPOINTS

### 1. Create Ticket

- **Method:** POST
- **Path:** `/api/tickets`
- **Request Body:** `TicketCreate`
- **Response:** `Ticket`

```json
// Request
{
  "user_name": "Juan Perez",
  "telegram_id": 123456789
}

// Response
{
  "id": 1,
  "user_name": "Juan Perez",
  "telegram_id": 123456789,
  "number": 15,
  "status": "waiting",
  "created_at": "2026-04-17T15:00:00Z",
  "updated_at": "2026-04-17T15:00:00Z"
}
```

### 2. Get All Tickets

- **Method:** GET
- **Path:** `/api/tickets`
- **Response:** `List[Ticket]`

```json
[
  {
    "id": 1,
    "user_name": "Juan Perez",
    "telegram_id": 123456789,
    "number": 15,
    "status": "waiting",
    "created_at": "2026-04-17T15:00:00Z",
    "updated_at": "2026-04-17T15:00:00Z"
  }
]
```

### 3. Get Ticket Status (by ID)

- **Method:** GET
- **Path:** `/api/tickets/{ticket_id}/status`
- **Response:** `TicketStatusResponse`

```json
{
  "ticket_id": 1,
  "position": 3,
  "status": "waiting",
  "number": 15
}
```

### 4. Update Ticket Status

- **Method:** PATCH
- **Path:** `/api/tickets/{ticket_id}`
- **Request Body:** `{ "status": "attended" }`
- **Response:** `Ticket`

```json
// Request
{
  "status": "attended"
}

// Response
{
  "id": 1,
  "user_name": "Juan Perez",
  "telegram_id": 123456789,
  "number": 15,
  "status": "attended",
  "created_at": "2026-04-17T15:00:00Z",
  "updated_at": "2026-04-17T15:10:00Z"
}
```

### 5. Telegram Bot: Get Ticket Status (Webhook)

- **Method:** POST
- **Path:** `/api/telegram/status`
- **Request Body:** `TicketStatusRequest`
- **Response:** `TicketStatusResponse`

```json
// Request
{
  "ticket_id": 1
}

// Response
{
  "ticket_id": 1,
  "position": 3,
  "status": "waiting",
  "number": 15
}
```

### 6. Telegram Bot: Notify User (Internal Use)

- **Method:** POST
- **Path:** `/api/telegram/notify`
- **Request Body:** `TelegramNotification`
- **Response:** `{ "ok": true }`

```json
// Request
{
  "telegram_id": 123456789,
  "message": "Su turno ha sido asignado: 15"
}

// Response
{
  "ok": true
}
```

---

## 4. FILE STRUCTURE

```
.
├── backend/
│   ├── Dockerfile                # Docker build for FastAPI backend
│   ├── main.py                   # FastAPI app entry point
│   ├── database.py               # SQLite connection and ORM logic
│   ├── telegram_bot.py           # Telegram bot logic (python-telegram-bot)
│   ├── api/
│   │   ├── __init__.py           # API package init
│   │   ├── tickets.py            # Ticket endpoints
│   │   └── telegram.py           # Telegram endpoints
│   ├── shared/
│   │   ├── __init__.py           # Shared package init
│   │   └── models.py             # Pydantic models (data contracts)
│   ├── utils.py                  # Utility functions (e.g., notification helpers)
│   └── start.sh                  # Startup script for backend container
├── frontend/
│   ├── Dockerfile                # Docker build for static frontend
│   ├── index.html                # Main HTML page
│   ├── main.js                   # JavaScript logic for ticket creation/status
│   ├── styles.css                # Custom CSS (Bootstrap overrides)
│   └── start.sh                  # Startup script for frontend container
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
```

### PORT TABLE

| Service    | Listening Port | Path              |
|------------|---------------|-------------------|
| backend    | 8001          | backend/          |

### SHARED MODULES

| Shared path         | Imported by services |
|---------------------|---------------------|
| backend/shared/     | backend             |

---

## 5. ENVIRONMENT VARIABLES

| Name                  | Type    | Description                                             | Example Value           |
|-----------------------|---------|---------------------------------------------------------|------------------------|
| BACKEND_HOST          | string  | Host for FastAPI backend                                | 0.0.0.0                |
| BACKEND_PORT          | int     | Port for FastAPI backend (must be 8001)                 | 8001                   |
| TELEGRAM_BOT_TOKEN    | string  | Telegram Bot API token                                  | 123456:ABC-DEF1234ghI  |
| TELEGRAM_WEBHOOK_URL  | string  | Public webhook URL for Telegram bot                     | https://mydomain.com/api/telegram/webhook |
| DATABASE_URL          | string  | SQLite DB URL                                           | sqlite:///./tickets.db |
| FRONTEND_PORT         | int     | Port for frontend static server                         | 8080                   |
| TZ                    | string  | Timezone for containers                                 | America/Argentina/Buenos_Aires |
| DEBUG                 | bool    | Enable debug logging                                    | true                   |

---

## 6. IMPORT CONTRACTS

### backend/main.py

- `from backend.api.tickets import router as tickets_router`
- `from backend.api.telegram import router as telegram_router`
- `from backend.telegram_bot import start_bot`
- `from backend.database import get_db, init_db`

### backend/api/tickets.py

- `from backend.shared.models import TicketCreate, Ticket, TicketStatusResponse`
- `from backend.database import get_db`
- `from backend.utils import notify_telegram_user`

### backend/api/telegram.py

- `from backend.shared.models import TicketStatusRequest, TicketStatusResponse, TelegramNotification`
- `from backend.database import get_db`
- `from backend.utils import notify_telegram_user`

### backend/shared/models.py

- `TicketCreate`
- `Ticket`
- `TicketStatusRequest`
- `TicketStatusResponse`
- `TelegramNotification`

### backend/database.py

- `get_db`
- `init_db`
- `create_ticket`
- `get_ticket_by_id`
- `get_all_tickets`
- `update_ticket_status`
- `get_ticket_position`

### backend/telegram_bot.py

- `start_bot`
- `handle_new_ticket`
- `handle_status_request`

### backend/utils.py

- `notify_telegram_user`

---

## 7. FRONTEND STATE & COMPONENT CONTRACTS

### State Primitives

No framework-specific state primitives (React/Vue/Angular/Svelte) are used. All state is managed via vanilla JavaScript objects and functions.

#### JavaScript State Objects

- `window.tickets: Ticket[]` — List of all tickets fetched from backend.
- `window.currentTicket: Ticket | null` — The ticket created in the current session.
- `window.loading: boolean` — Indicates if a request is in progress.
- `window.error: string | null` — Error message if any.

#### JavaScript Functions

- `createTicket(user_name: string, telegram_id?: number): Promise<Ticket>`
- `getAllTickets(): Promise<Ticket[]>`
- `getTicketStatus(ticket_id: number): Promise<TicketStatusResponse>`

### UI Components (HTML/JS)

- **TicketForm**
  - Props/inputs: `{ onSubmit: (user_name: string, telegram_id?: number) => void, loading: boolean }`
- **TicketStatus**
  - Props/inputs: `{ ticket: Ticket | null, status: TicketStatusResponse | null, loading: boolean }`
- **TicketList**
  - Props/inputs: `{ tickets: Ticket[], onSelect: (ticket_id: number) => void }`
- **ErrorAlert**
  - Props/inputs: `{ message: string | null }`

---

## 8. FILE EXTENSION CONVENTION

- **Frontend files:** `.js` (JavaScript only, no TypeScript, no JSX/TSX)
- **Backend files:** `.py`
- **Entry point:** `/frontend/main.js` (referenced in `<script src="/main.js"></script>` in `index.html`)
- **All frontend files use `.js` and `.css` extensions.**
- **All backend files use `.py` extensions.**

---

**CRITICAL:**
- All field names, API paths, and state property names must be used verbatim as specified above.
- Dockerfile for backend must EXPOSE 8001 and run `uvicorn` on port 8001.
- All shared modules in `backend/shared/` must be copied into the backend Docker image.
- All environment variables must be present in `.env.example` with the exact names and types as above.
- No React/Vue/Angular/Svelte code or file extensions are to be used anywhere in the project. All frontend logic is vanilla JavaScript.
- All API endpoints must strictly follow the schemas and paths defined above.