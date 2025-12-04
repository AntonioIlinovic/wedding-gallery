# GEMINI.md



IMPORTANT NOTE:
NEVER COMMIT YOURSELF. I WILL MANUALLY COMMIT TO GIT.


## Project Overview

This repository contains the source code for the "Wedding Gallery" web application. It is a full-stack project designed to allow wedding guests to upload and view photos from an event. The application is containerized using Docker and orchestrated with Docker Compose for both local development and production environments.

The architecture consists of:

*   **Frontend:** A React single-page application built with `create-react-app`.
*   **Backend:** A Django REST API that provides endpoints for the frontend.
*   **Storage:** MinIO for local S3-compatible object storage for photos. In production, this would be swapped out for a cloud-based object storage service like AWS S3.
*   **Infrastructure:** The infrastructure is managed as code using Terraform.

## Building and Running

### Local Development

The project is designed to be run locally using Docker Compose.

**Prerequisites:**

*   Docker
*   Docker Compose

**Running the Application:**

1.  **Clone the repository.**
2.  **Create a `.env` file** in the root of the project and in the `apps/backend` directory, using the `.env.example` files as a template.
3.  **Build and start the containers:**

    ```bash
    docker compose up --build
    ```

    This command will:
    *   Build the Docker images for the frontend and backend services.
    *   Start all the services defined in the `docker-compose.yml` file.
    *   Run database migrations for the backend.
    *   Create a superuser for the Django admin interface.

**Accessing the Application:**

*   **Frontend:** `http://localhost:3000`
*   **Backend API:** `http://localhost:8000`
*   **MinIO Console:** `http://localhost:9090`

### Testing

*   **Frontend:**

    ```bash
    docker compose exec frontend npm test
    ```

*   **Backend:**

    The backend does not have a test suite configured yet.

## Development Conventions

*   All services are containerized and should be run via Docker Compose.
*   The backend is a Django project, and the frontend is a React project.
*   Environment variables are used for configuration. See the `.env.example` files for details.
*   Infrastructure is managed with Terraform.


IMPORTANT NOTE:
NEVER COMMIT YOURSELF. I WILL MANUALLY COMMIT TO GIT.