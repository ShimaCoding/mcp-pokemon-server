# =============================================================================
# Multi-stage build for MCP Pokemon Server (Production)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

LABEL org.opencontainers.image.title="MCP Pokemon Server" \
    org.opencontainers.image.description="Secure MCP Pokemon Server" \
    org.opencontainers.image.vendor="ShimaCoding" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.source="https://github.com/ShimaCoding/mcp-pokemon-server"

# Security-focused environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONHASHSEED=random

# Update system and install build dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (layer caching optimization)
COPY pyproject.toml README.md ./

# Install Python dependencies with BuildKit cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install .

# ---------------------------------------------------------------------------
# Stage 2: Production — minimal runtime image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS production

# Runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8000

# No extra runtime deps needed — Python stdlib handles healthcheck
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with correct ownership
COPY --chown=mcpuser:mcpuser src/ ./src/
COPY --chown=mcpuser:mcpuser config/ ./config/
COPY --chown=mcpuser:mcpuser pyproject.toml README.md ./

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown mcpuser:mcpuser /app/logs

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 8000

# Health check — verify TCP port is open using Python's built-in socket
# (MCP endpoint requires special Accept headers, so HTTP-level check would always 406)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', 8000)); s.close()" || exit 1

# Default command
CMD ["python", "-m", "src.main"]
