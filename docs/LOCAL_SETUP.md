# Local Development Setup

This guide explains how to set up and run the application locally using Docker Compose. The local environment includes the backend and frontend applications, a PostgreSQL database, and a MinIO server for S3-compatible object storage. This simulates AWS cloud services locally before deployment.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Quick Start

1.  **Create Environment File:**
    Navigate to the backend app directory and create a `.env` file from the example. This file contains the credentials for the local database and MinIO server.

    ```bash
    cd apps/backend
    cp .env.example .env
    cd ../.. 
    ```

2.  **Start the Application:**
    Build and start all services using Docker Compose.

    ```bash
    docker compose up --build
    ```

3.  **Access the Services (Migrations & Superuser Automated):**
    When the backend service starts, database migrations are automatically applied, and a superuser with username `admin` and password `admin` is created (if it doesn't already exist). These credentials can be configured in `apps/backend/.env`.
    -   **Frontend:** [http://localhost:3000](http://localhost:3000)
    -   **Backend API:** [http://localhost:8000/api/](http://localhost:8000/api/)
    -   **MinIO Console (Object Storage):** [http://localhost:9090](http://localhost:9090)
        -   **Username:** `miniouser`
        -   **Password:** `miniopassword`
        (These are the default values from the `.env` file).

## Stopping the Application

To stop all services, run:
```bash
docker compose down
```
To stop the services and remove the database and MinIO data volumes, run:
```bash
docker compose down -v
```

## Common Commands

### Run Django management commands:
```bash
docker compose exec backend python manage.py <command>
```
*Examples:*
-   **Apply migrations manually (if needed):**
    ```bash
    docker compose exec backend python manage.py migrate
    ```
-   **Create new migrations (after model changes):**
    ```bash
    docker compose exec backend python manage.py makemigrations
    ```
-   **Create a superuser manually (only if the automated one is not desired):**
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```
    (Note: A superuser with username 'admin' and password 'admin' is automatically created on backend startup if one does not exist. These credentials can be configured in `apps/backend/.env`.)

### View logs:
```bash
docker compose logs -f
```
*To view logs for a specific service:*
```bash
docker compose logs -f backend
```

### Rebuild containers:
```bash
docker compose up --build
```

## Project Services

-   `frontend`: The React frontend application.
-   `backend`: The Django backend application.
-   `postgres`: PostgreSQL database for data persistence.
-   `minio`: S3-compatible object storage for file uploads.
-   `mc`: A setup client for MinIO that creates the initial storage bucket.