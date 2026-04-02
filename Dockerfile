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

# Install system dependencies for Python packages (including TA-Lib build deps)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Build and install TA-Lib C library (required for TA-Lib Python package)
RUN wget -q https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make -j$(nproc) && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

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

# Install runtime dependencies including nginx + TA-Lib shared library
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy TA-Lib shared library from builder stage
COPY --from=backend-builder /usr/lib/libta_lib* /usr/lib/
COPY --from=backend-builder /usr/include/ta-lib /usr/include/ta-lib
RUN ldconfig

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
