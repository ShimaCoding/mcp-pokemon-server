# MCP Pokemon Server

Educational MCP Server implementation using FastMCP and PokéAPI integration.

## 🚧 Work in Progress

This project is currently under development following the implementation plan.

## 📋 Project Overview

This is an educational MCP (Model Context Protocol) server that demonstrates best practices for MCP development using:

- **FastMCP**: Modern Python MCP server framework
- **PokéAPI**: External data source integration
- **Educational Focus**: Comprehensive examples and documentation

## 🎯 Features

### Planned Features
- [ ] **Tools**: Pokemon information retrieval and analysis
- [ ] **Resources**: Dynamic Pokemon data resources
- [ ] **Prompts**: Educational and battle-focused prompts
- [ ] **Interactive Elicitation**: Multi-step tool interactions
- [ ] **Caching**: Multi-level caching system
- [ ] **Monitoring**: Comprehensive metrics and logging

## 🏗️ Architecture

```
src/
├── main.py                 # Entry point
├── server/                 # MCP server configuration
├── tools/                  # MCP tools implementation
├── resources/              # MCP resources
├── prompts/                # MCP prompts
├── clients/                # External API clients
├── models/                 # Data models
├── utils/                  # Utilities
└── config/                 # Configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ShimaCoding/mcp-pokemon-server.git
   cd mcp-pokemon-server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the server**:
   ```bash
   python -m src.main
   ```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_tools.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## 📋 Development Plan

See [plan-de-accion-mcp.md](../plan-de-accion-mcp.md) for the complete development roadmap.

## 🔧 Configuration

Configuration is handled through environment variables. See `.env.example` for all available options.

### Key Configuration Options

- `MCP_SERVER_HOST`: Server host (default: localhost)
- `MCP_SERVER_PORT`: Server port (default: 8000)
- `POKEAPI_BASE_URL`: PokéAPI base URL
- `REDIS_URL`: Redis connection URL
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 📖 Documentation

- [API Documentation](docs/api.md) *(Coming soon)*
- [Examples](docs/examples.md) *(Coming soon)*
- [Deployment Guide](docs/deployment.md) *(Coming soon)*

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PokéAPI](https://pokeapi.co/) for providing the Pokemon data
- [MCP](https://github.com/modelcontextprotocol) for the Model Context Protocol
- The Python community for excellent tools and libraries

## 📊 Project Status

- ✅ **Phase 0**: GitHub Configuration
- 🚧 **Phase 1**: Project Setup (In Progress)
- ⏳ **Phase 2**: Base Implementation
- ⏳ **Phase 3**: Advanced Features
- ⏳ **Phase 4**: Optimization & Monitoring
- ⏳ **Phase 5**: Testing & Documentation
- ⏳ **Phase 6**: Deployment
