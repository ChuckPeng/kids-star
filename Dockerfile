# ---- Stage 1: Build Frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Stage 2: Build Backend Dependencies ----
FROM python:3.12-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 3: Runtime ----
FROM python:3.12-slim

# System deps + nginx + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY backend/ .

# Frontend static files
COPY --from=frontend-builder /app/frontend/dist /app/static

# Nginx config
COPY nginx.prod.conf /etc/nginx/sites-available/default

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
