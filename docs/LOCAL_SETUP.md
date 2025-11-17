# Local Development Setup

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. **Start the application:**
   ```bash
   docker compose up --build
   ```

2. **Run Django migrations (first time only):**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Backend Health: http://localhost:8000/api/health/

## Stopping the Application

```bash
docker compose down
```

## Common Commands

### Run Django management commands:
```bash
docker compose exec backend python manage.py <command>
```

### Create Django superuser:
```bash
docker compose exec backend python manage.py createsuperuser
```

### View logs:
```bash
docker compose logs -f
```

### Rebuild containers:
```bash
docker compose up --build
```

## Project Structure

- `apps/backend/` - Django backend application
- `apps/frontend/` - React frontend application
- `docker-compose.yml` - Local development configuration
- `deploy/` - Deployment configurations (for production)

## Troubleshooting

- If containers fail to start, check logs: `docker compose -f docker-compose.yml logs`
- If port conflicts occur, modify ports in `docker-compose.yml`
- To reset the database, remove volumes: `docker compose -f docker-compose.yml down -v`

