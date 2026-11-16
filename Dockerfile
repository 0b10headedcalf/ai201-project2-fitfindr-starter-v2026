# Local stand-in for Render's native Python runtime — NOT used by Render itself
# (render.yaml deploys without Docker). Same Python, same install, same start
# command, so "works in compose" means "works on Render" as closely as a laptop
# can show it. See docker-compose.yml for the 512 MB / 0.1 CPU limits.
FROM python:3.13.1-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Exactly render.yaml's startCommand. Render sets PORT (default 10000);
# gunicorn reads it and binds 0.0.0.0, like on Render.
CMD ["sh", "-c", "exec gunicorn serve:app --workers 1 --timeout 120 --bind 0.0.0.0:${PORT}"]
