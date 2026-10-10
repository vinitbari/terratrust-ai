# ==============================================================================
# Multi-stage Dockerfile for TerraTrust AI (Full-Stack Unified Production)
# Builds Frontend + Backend + AI/ML Model into a single cloud-ready container
# ==============================================================================

# Stage 1: Build Vite + React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY apps/web/package*.json ./apps/web/
COPY package*.json ./
RUN npm install

COPY apps/web ./apps/web
COPY packages ./packages
RUN npm run build --workspace=web

# Stage 2: Production Python ASGI + ML inference server
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    DATABASE_URL=sqlite:///./fin03.db

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API backend application code and ML model
COPY apps/api .

# Copy built frontend assets for unified single-origin SPA serving
COPY --from=frontend-builder /build/apps/web/dist /app/apps/web/dist
COPY --from=frontend-builder /build/apps/web/dist /app/dist

# Security: Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
