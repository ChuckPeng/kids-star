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

# Startup: safe migration that NEVER destroys data
RUN cat > /start.sh <<'START'
#!/bin/bash
set -e
cd /app

echo "=== Checking database state ==="
python3 <<'PYEOF'
import asyncio, asyncpg, os

async def main():
    url = os.environ['DATABASE_URL'].replace('+asyncpg', '')
    conn = await asyncpg.connect(url)
    try:
        # Check if any app tables exist
        rows = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename IN ('users','families','tasks','submissions')"
        )
        existing = [r['tablename'] for r in rows]
        print(f"Existing app tables: {existing if existing else 'none'}")

        # Check alembic version tracking
        try:
            ver = await conn.fetchval("SELECT version_num FROM alembic_version")
            print(f"Current alembic version: {ver}")
        except:
            print("No alembic_version table")
            ver = None

        if existing and ver is None:
            # Tables exist but no migration tracking -> stamp current head
            print("Tables exist without migration record, stamping head version...")
            import subprocess, sys
            subprocess.run([sys.executable, '-m', 'alembic', 'stamp', 'head'], check=True)
            print("Stamped head version, data preserved.")
        elif not existing:
            print("Fresh database, running migration...")
            import subprocess, sys
            subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], check=True)
            print("Migration complete.")
        else:
            print("Database up to date, data preserved.")
    finally:
        await conn.close()

asyncio.run(main())
PYEOF

echo "=== Starting services ==="
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
START
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"]
