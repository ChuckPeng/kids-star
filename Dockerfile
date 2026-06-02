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

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor libpq5 && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /etc/nginx/sites-enabled/default && \
    rm -rf /etc/nginx/conf.d/*

WORKDIR /app

COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY backend/ .

COPY --from=frontend-builder /app/frontend/dist /app/static

# Nginx
RUN cat > /etc/nginx/conf.d/default.conf <<'NGX'
server {
    listen 80 default_server;
    server_name localhost;
    root /app/static;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGX

# Supervisor
RUN cat > /etc/supervisor/conf.d/supervisord.conf <<'SUP'
[supervisord]
nodaemon=true
user=root
[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
[program:uvicorn]
command=uvicorn main:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
[program:celery-worker]
command=celery -A app.tasks.celery_app worker --loglevel=info
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
[program:celery-beat]
command=celery -A app.tasks.celery_app beat --loglevel=info
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
SUP

# Startup: reset tracking, migrate, fallback to full recreate
RUN cat > /start.sh <<'START'
#!/bin/bash
cd /app
# Fix asyncpg URL format and drop stale tracking
python3 <<'PYEOF'
import asyncio, asyncpg, os
async def main():
    url = os.environ['DATABASE_URL'].replace('+asyncpg', '')
    conn = await asyncpg.connect(url)
    await conn.execute("DROP TABLE IF EXISTS alembic_version")
    await conn.close()
asyncio.run(main())
PYEOF
# Try migration; if tables exist from old schema, drop and retry
alembic upgrade head 2>&1 || {
    echo "Stale tables detected, recreating..."
    python3 <<'PYEOF2'
import asyncio, asyncpg, os
async def main():
    url = os.environ['DATABASE_URL'].replace('+asyncpg', '')
    conn = await asyncpg.connect(url)
    rows = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    for r in rows:
        await conn.execute(f'DROP TABLE IF EXISTS "{r[0]}" CASCADE')
    await conn.close()
asyncio.run(main())
PYEOF2
    alembic upgrade head
}
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
START
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"]
