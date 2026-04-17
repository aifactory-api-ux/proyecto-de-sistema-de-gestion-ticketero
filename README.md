# Sistema de Gestión Ticketero

Sistema de gestión de turnos con notificaciones vía Telegram - MVP.

## Descripción

Sistema de tickets para gestión de colas con las siguientes funcionalidades:

- **Creación de turnos**: Los usuarios pueden solicitar un turno a través de la interfaz web o el bot de Telegram.
- **Gestión de turnos**: Los operadores pueden visualizar todos los turnos, activar el siguiente turno y marcar turnos como atendidos.
- **Notificaciones**: Los usuarios que proporcionaron su ID de Telegram reciben notificaciones cuando su turno es asignado o actualizado.
- **Bot de Telegram**: Consulta de estado y envío de notificaciones vía webhook.

## Requisitos Previos

- Docker 26.0.0+
- Docker Compose 2.27.0+
- Puerto 8001 disponible (backend)
- Puerto 8080 disponible (frontend)

## Configuración

1. Clonar el repositorio:

```bash
git clone <repository-url>
cd ticket-system
```

2. Copiar el archivo de configuración de ejemplo:

```bash
cp .env.example .env
```


3. Editar `.env` con los valores apropiados:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_WEBHOOK_URL=https://tu-dominio.com/api/telegram/webhook

# Debug Mode
DEBUG=false
```


## Ejecución


### Opción 1: Script automático (recomendado)

```bash
./run.sh
```

### Opción 2: Docker Compose manualmente

```bash
docker-compose build
docker-compose up -d
```


## Servicios y Puertos

| Servicio   | Puerto | Descripción              |
|------------|--------|--------------------------|
| backend    | 8001   | API REST de tickets      |
| frontend   | 8080   | Interfaz web estática    |

## URLs de Acceso

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## Variables de Entorno

| Variable            | Descripción                                 | Valor por defecto              |
|---------------------|--------------------------------------------|----------------------------|
| BACKEND_HOST        | Host del backend                           | 0.0.0.0                    |
| BACKEND_PORT        | Puerto del backend (debe ser 8001)         | 8001                       |
| TELEGRAM_BOT_TOKEN  | Token del Bot de Telegram                  | -                          |
| TELEGRAM_WEBHOOK_URL| URL pública del webhook de Telegram        | -                          |
| DATABASE_URL       | URL de la base de datos SQLite             | sqlite:///./tickets.db     |
| FRONTEND_PORT      | Puerto del servidor frontend              | 8080                       |
| TZ                  | Zona horaria de los contenedores          | America/Argentina/Buenos_Aires |
| DEBUG               | Habilitar logging de debug               | false                       |

## API Endpoints

### Tickets

| Método | Path                    | Descripción                    |
|--------|-------------------------|--------------------------------|
| POST   | /api/tickets            | Crear un nuevo turno           |
| GET    | /api/tickets            | Obtener todos los turnos       |
| GET    | /api/tickets/{id}/status| Consultar estado de turno     |
| PATCH  | /api/tickets/{id}       | Actualizar estado de turno     |

### Telegram

| Método | Path                  | Descripción                    |
|--------|----------------------|--------------------------------|
| POST   | /api/telegram/status | Consultar estado (webhook)     |
| POST   | /api/telegram/notify | Enviar notificación            |

## Comandos Útiles

### Iniciar servicios
```bash
docker-compose up -d
```


### Ver logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```


### Detener servicios
```bash
docker-compose down
```


### Reiniciar servicios
```bash
docker-compose restart
```

### Ver estado de servicios
```bash
docker-compose ps
```


## Arquitectura

- **Backend**: Python 3.11 con FastAPI
- **Base de datos**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript vanilla, Bootstrap 5
- **Contenedorización**: Docker + Docker Compose

## Desarrollo


El proyecto sigue una arquitectura MVC:

- **Modelos**: `backend/shared/models.py` (Pydantic)
- **Controladores**: `backend/api/` (endpoints FastAPI)
- **Vistas**: `frontend/` (HTML/CSS/JS estático)

## Licencia

MIT
