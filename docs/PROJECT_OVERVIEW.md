# Project Overview

A single reference file describing the repository structure, the tools and services to be used (high‑level), and a step‑by‑step plan to create and set up the application.

---

## 1) Project Structure (planned)

```
/                          # repo root
├─ README.md
├─ .gitignore
├─ .env.example
├─ docker-compose.yml          # local development (run yourself)
├─ docker-compose.production.yml     # production deployment (real domain later)
├─ apps/
│  ├─ backend/
│  │  ├─ Dockerfile                  # lives with the code
│  │  ├─ requirements.txt            # Python deps
│  │  ├─ manage.py                   # Django entrypoint (kept here)
│  │  └─ src/                        # (empty for now; project package will go here)
│  └─ frontend/
│     ├─ Dockerfile                  # lives with the code
│     ├─ package.json
│     └─ src/                        # (empty for now)
├─ deploy/
│  └─ nginx.conf                     # reverse proxy for production
└─ infra/
   └─ terraform/
      ├─ modules/                    # reusable building blocks
      └─ envs/
         └─ prod/                    # production environment (dev done locally)
```

**Notes**

* `backend/` and `frontend/` are nested under `apps/`.
* Dockerfiles stay inside each app folder for clarity and better build caching.
* No deploy scripts for now; production compose + reverse proxy config live in `deploy/`.

---

## 2) Tools (high‑level, no deep specifics)

* **Frontend:** React + build tooling
* **Backend:** Django + REST framework
* **Containerization:** Docker; Compose for local and production orchestration
* **Version Control & CI/CD:** GitHub + GitHub Actions
* **Infrastructure as Code:** Terraform
* **Testing:** Unit tests for frontend and backend; basic end‑to‑end tests
* **Observability (baseline):** Error tracking and logs

---

## 3) Cloud & Services (high‑level)

* **Domain, DNS, Security:** Cloudflare (DNS, HTTPS termination/proxy, basic WAF)
* **Production Domain:** [weddinggallery.site](http://weddinggallery.site/)
* **Compute (initial):** Single VM/instance running `docker-compose`
* **Object Storage:** S3‑compatible storage for photos
* **Container Registry:** AWS ECR (for built images)
* **Database:** Managed PostgreSQL

---

## 4) Implementation & Setup Plan

### Phase A — Bootstrap Repository

1. Create repository skeleton as shown above.
2. Add `requirements.txt` (backend) and `package.json` (frontend) placeholders.
3. Add `docker-compose.yml` and `docker-compose.production.yml` with service stubs.
4. Add `deploy/nginx.conf` placeholder.
5. Commit an initial `README.md` and this `PROJECT_OVERVIEW.md`.

### Phase B — Minimal Running App (Local)

1. Initialize Django project (inside `apps/backend/src/`) and keep `manage.py` at `apps/backend/`.
2. Add a healthcheck endpoint on the backend and a simple homepage on the frontend.
3. Wire local compose to run both services (`docker compose up`).

### Phase C — Core Features (MVP)

1. Event model (short code + optional PIN) and QR code generation.
2. Presigned upload endpoint for direct browser → storage uploads.
3. Gallery listing with simple moderation (hide/delete).
4. Basic validations (file type/size), rate limiting, and minimal consent text.

### Phase D — Infrastructure Provisioning (Terraform)

1. Define Terraform modules for object storage, container registry, database, IAM/auth.
2. Apply production environment; store state securely.
3. Configure CORS for uploads and minimal lifecycle rules for storage.

**Note:** Development is done locally using `docker-compose.yml`. Only production infrastructure is managed via Terraform.

### Phase E — CI/CD & Production

1. GitHub Actions: lint/test → build images → push to registry.
2. Provision a small VM and point domain via Cloudflare.
3. Use `docker-compose.production.yml` to run the app behind Nginx.
4. Run backend migrations as part of the first deploy; verify health.
5. Configure DNS: Point [weddinggallery.site](http://weddinggallery.site/) to the EC2 instance via Cloudflare.
