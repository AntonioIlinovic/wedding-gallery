# Production Deployment Changes

## Summary

The frontend has been updated to use a proper production build with nginx instead of running React's development server in production. This fixes the "Invalid Host header" issue when using Cloudflare as a reverse proxy.

## What Changed

### 1. **Separate Dockerfiles for Development and Production**

#### Frontend
- **`apps/frontend/Dockerfile`** - Development (unchanged, uses React dev server)
- **`apps/frontend/Dockerfile.prod`** - Production (new, multi-stage build with nginx)

#### Backend
- **`apps/backend/Dockerfile`** - Development (unchanged, uses Django dev server)
- **`apps/backend/Dockerfile.prod`** - Production (new, uses gunicorn)

### 2. **Frontend Production Setup**

The production Dockerfile (`Dockerfile.prod`) uses a multi-stage build:
- **Stage 1 (Build)**: Compiles React app into static files
- **Stage 2 (Production)**: Serves static files with nginx

### 3. **Nginx Configuration**

Created `apps/frontend/nginx.conf` with:
- API proxying to backend (handles `/api/` requests)
- Gzip compression for better performance
- Security headers
- React Router support (SPA fallback to index.html)
- Static file caching
- Health check endpoint at `/health`

### 4. **Docker Compose Changes**

**`docker-compose.production.yml`**:
- Frontend now exposes port `80:80` (nginx) instead of `80:3000`
- Removed `env_file` for frontend (no runtime env vars needed)
- Frontend env vars are baked into the build at build time

### 5. **GitHub Actions Workflow**

**`.github/workflows/deploy.yml`**:
- Updated to use `Dockerfile.prod` for both frontend and backend
- Removed frontend `.env.production` file creation (not needed)

## Local Development (Unchanged)

Your local development setup is **NOT affected**:

```bash
# Still works exactly the same
docker compose up
```

This uses the regular `Dockerfile` (development mode with hot reload).

## Production Deployment

### Deploy to Production

Simply trigger the GitHub Actions workflow on Github Actions UI.

## Benefits

### ✅ Fixed Issues
- **No more "Invalid Host header"** - nginx accepts all host headers
- **Proper production build** - optimized, minified React bundle
- **Better performance** - gzip compression, static file caching
- **Separation of concerns** - dev and prod environments are separate

### ✅ Improvements
- **Gunicorn** for backend (production-grade WSGI server)
- **Nginx** for frontend (production-grade web server)
- **Security headers** added by nginx
- **Health check endpoint** at `/health` for monitoring
- **API proxying** handled by nginx (single origin, no CORS issues)

## Testing the Production Build Locally

If you want to test the production build locally:

```bash
# Build production images
docker build -f apps/backend/Dockerfile.prod -t wedding-backend-prod apps/backend
docker build -f apps/frontend/Dockerfile.prod -t wedding-frontend-prod apps/frontend

# Run them
docker network create wedding-network

docker run -d --name backend --network wedding-network \
  -p 8000:8000 \
  -e SECRET_KEY=test-secret \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=backend,localhost,127.0.0.1 \
  wedding-backend-prod

docker run -d --name frontend --network wedding-network \
  -p 80:80 \
  wedding-frontend-prod

# Test
curl http://localhost
curl http://localhost/health

# Cleanup
docker stop frontend backend
docker rm frontend backend
docker network rm wedding-network
```

## Accessing Django Admin in Production

Since port 8000 is not exposed publicly (security), use SSH tunneling:

```bash
# Create SSH tunnel (using port 9000 locally since 8000 is in use)
ssh -i ~/.ssh/aws-wedding-gallery-key -L 9000:localhost:8000 ubuntu@63.179.218.184

# Then access admin at:
# http://localhost:9000/admin
```

Or temporarily access via the EC2 IP directly:
```
http://63.179.218.184:8000/admin
```

## Getting the Access Token

1. Log into Django admin (see above)
2. Navigate to **Events** section
3. Click on your event
4. Copy the **access_token** field
5. Share this URL with guests:
   ```
   https://weddinggallery.site/?token=YOUR_TOKEN_HERE
   ```

## Cloudflare Setup

Your Cloudflare should work now with these settings:
- **SSL/TLS Mode**: Flexible (Cloudflare ↔ Your server uses HTTP)
- **DNS**: Proxied (orange cloud) ✅
- **A Record**: Points to your EC2 IP (`63.179.218.184`)

## Next Deployment

Just commit your changes and run the workflow:

```bash
git add .
git commit -m "Add production Dockerfiles with nginx and gunicorn"
git push origin main

# Then trigger deployment via GitHub Actions
```

---

**Questions?** Check the logs on EC2:
```bash
ssh -i ~/.ssh/aws-wedding-gallery-key ubuntu@63.179.218.184
sudo docker logs wedding-gallery-frontend-prod
sudo docker logs wedding-gallery-backend-prod
```

