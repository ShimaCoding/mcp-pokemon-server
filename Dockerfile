# Multi-stage build for MCP Pokemon Server
FROM python:3.12-slim AS builder

# Add security labels and metadata
LABEL org.opencontainers.image.title="MCP Pokemon Server" \
    org.opencontainers.image.description="Secure MCP Pokemon Server" \
    org.opencontainers.image.vendor="YourOrganization" \
    org.opencontainers.image.version="1.0.0" \
    security.scan="required"

# Set security-focused environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONHASHSEED=random

# Update system and install security updates and dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# Production stage
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=mcpuser:mcpuser src/ ./src/
COPY --chown=mcpuser:mcpuser config/ ./config/
COPY --chown=mcpuser:mcpuser pyproject.toml ./
COPY --chown=mcpuser:mcpuser README.md ./

# Create logs directory
RUN mkdir -p /app/logs && chown mcpuser:mcpuser /app/logs

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.main"]
