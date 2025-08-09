# Docker Setup for MCP Pokemon Server

This directory contains Docker configuration files and utilities for the MCP Pokemon Server.

## 📋 Files Overview

- `Dockerfile` - Production-ready multi-stage build
- `Dockerfile.dev` - Development environment with hot reload
- `docker-compose.yml` - Production deployment configuration
- `docker-compose.dev.yml` - Development environment configuration
- `.dockerignore` - Files to exclude from Docker build context
- `docker/docker-utils.sh` - Utility script for common Docker operations

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

### Production Deployment

```bash
# Build and run production container
docker-compose up -d

# Or use the utility script
./docker/docker-utils.sh run-prod
```

### Development Environment

```bash
# Build and run development container
docker-compose -f docker-compose.dev.yml up -d

# Or use the utility script
./docker/docker-utils.sh run-dev
```

## 🛠️ Docker Utility Script

The `docker/docker-utils.sh` script provides convenient commands:

```bash
# Build images
./docker/docker-utils.sh build-prod    # Production image
./docker/docker-utils.sh build-dev     # Development image

# Run containers
./docker/docker-utils.sh run-prod      # Production environment
./docker/docker-utils.sh run-dev       # Development environment

# Management
./docker/docker-utils.sh stop          # Stop all containers
./docker/docker-utils.sh status        # Show container status
./docker/docker-utils.sh logs          # View logs
./docker/docker-utils.sh cleanup       # Clean up Docker resources

# Development
./docker/docker-utils.sh test          # Run tests
./docker/docker-utils.sh shell-dev     # Shell into dev container
```

## 🏗️ Build Process

### Production Build

The production Dockerfile uses a multi-stage build:

1. **Builder stage**: Installs dependencies and builds the application
2. **Production stage**: Creates minimal runtime image with only necessary components

Benefits:
- Smaller final image size
- Enhanced security (fewer attack vectors)
- Faster deployment and startup times

### Development Build

The development Dockerfile:
- Includes development dependencies
- Enables hot reload for code changes
- Provides debugging tools
- Mounts source code as volume

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `POKEAPI_BASE_URL` | `https://pokeapi.co/api/v2` | PokéAPI base URL |

### Ports

- `8000` - MCP server port
- `6379` - Redis port (if enabled)

### Volumes

- `./logs:/app/logs` - Log files
- `.:/app` - Source code (development only)

## 📊 Health Checks

Both production and development containers include health checks:

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' mcp-pokemon-server
```

## 🔍 Debugging

### View Logs

```bash
# Production logs
docker-compose logs -f mcp-pokemon-server

# Development logs
docker-compose -f docker-compose.dev.yml logs -f mcp-pokemon-server-dev

# Or use utility script
./docker/docker-utils.sh logs
./docker/docker-utils.sh logs-dev
```

### Shell Access

```bash
# Production container
docker-compose exec mcp-pokemon-server /bin/bash

# Development container
docker-compose -f docker-compose.dev.yml exec mcp-pokemon-server-dev /bin/bash

# Or use utility script
./docker/docker-utils.sh shell
./docker/docker-utils.sh shell-dev
```

### Run Tests

```bash
# In development container
./docker/docker-utils.sh test

# Or manually
docker-compose -f docker-compose.dev.yml exec mcp-pokemon-server-dev pytest
```

## 🔐 Security Considerations

### Non-Root User

Both containers run as non-root user `mcpuser` (UID 1000) for enhanced security.

### Minimal Attack Surface

Production image:
- Uses slim Python base image
- Includes only runtime dependencies
- No development tools or build dependencies

### Network Security

- Containers run on isolated bridge network
- Only necessary ports are exposed
- No privileged access required

## 📈 Performance Optimization

### Image Size

- Multi-stage build reduces final image size
- `.dockerignore` excludes unnecessary files
- Minimal base image (python:3.11-slim)

### Runtime Performance

- Python bytecode compilation disabled (`PYTHONDONTWRITEBYTECODE=1`)
- Unbuffered Python output (`PYTHONUNBUFFERED=1`)
- Proper signal handling for graceful shutdowns

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000

   # Use different port
   MCP_SERVER_PORT=8001 docker-compose up
   ```

2. **Permission denied**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Docker daemon not running**
   ```bash
   # Start Docker service
   sudo systemctl start docker  # Linux
   # or start Docker Desktop app
   ```

4. **Build failures**
   ```bash
   # Clean build cache
   docker builder prune

   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Logs Analysis

```bash
# Check application logs
./docker/docker-utils.sh logs

# Check Docker daemon logs
docker system events

# Check container resource usage
docker stats
```

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
# Rebuild after dependency changes
docker-compose build --no-cache

# Or use utility script
./docker/docker-utils.sh build-prod
```

### Cleaning Up

```bash
# Remove unused Docker resources
./docker/docker-utils.sh cleanup

# Remove all containers and images
docker-compose down --rmi all
docker system prune -a
```

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Security](https://docs.docker.com/engine/security/)
