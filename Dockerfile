# LLMtrader - Multi-Stage Docker Build
# Stage 1: Frontend Build (Vue 3 + Vite)
# Stage 2: Python Backend
# Stage 3: Production Runtime with Nginx

# ============================================================================
# STAGE 1: Frontend Build
# ============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build production bundle
RUN npm run build

# ============================================================================
# STAGE 2: Python Backend Build
# ============================================================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 3: Production Runtime
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies including nginx
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend source
COPY backend/ ./backend/

# Copy frontend build from frontend-builder
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Configure nginx
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/sites-available/llmtrader
RUN ln -s /etc/nginx/sites-available/llmtrader /etc/nginx/sites-enabled/

# Create directories for logs
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/log/uvicorn

# Create supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start supervisor (manages nginx + uvicorn)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
