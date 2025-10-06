# Project Structure

```
remnabot/
│
├── src/                          # Source code
│   ├── core/                     # Core modules
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging setup
│   │   └── bot.py               # Bot initialization
│   │
│   ├── handlers/                 # Command handlers
│   │   ├── __init__.py
│   │   ├── start.py             # Start command and main menu
│   │   ├── users.py             # User management
│   │   ├── hosts.py             # Hosts management
│   │   ├── nodes.py             # Nodes management
│   │   ├── hwid.py              # HWID management
│   │   ├── squads.py            # Squads management
│   │   └── mass.py              # Mass operations
│   │
│   ├── services/                 # External services
│   │   ├── __init__.py
│   │   ├── api.py               # Remnawave API client
│   │   └── cache.py             # Redis cache service
│   │
│   ├── middleware/               # Middleware
│   │   ├── __init__.py
│   │   └── auth.py              # Admin authentication
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── keyboards.py         # Telegram keyboards
│   │   ├── formatters.py        # Data formatters
│   │   └── validators.py        # Input validators
│   │
│   ├── models/                   # Data models (if needed)
│   │   └── schemas.py
│   │
│   └── main.py                   # Application entry point
│
├── logs/                         # Log files
│
├── tests/                        # Tests (to be implemented)
│
├── .env.example                  # Environment variables example
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── Dockerfile                    # Docker image
├── docker-compose.yml            # Docker Compose (production)
├── docker-compose.dev.yml        # Docker Compose (development)
├── dev.sh                        # Development startup script (Linux/Mac)
├── dev.ps1                       # Development startup script (Windows)
├── README.md                     # Project documentation
└── STRUCTURE.md                  # This file
```

## Module Descriptions

### Core (`src/core/`)
- **config.py**: Manages application configuration using pydantic-settings
- **logger.py**: Sets up structured logging with loguru
- **bot.py**: Initializes the Telegram bot application

### Handlers (`src/handlers/`)
Each handler module manages specific bot functionality:
- **start.py**: Welcome message and main menu
- **users.py**: User CRUD operations, subscription management
- **hosts.py**: Host management
- **nodes.py**: Node management and statistics
- **hwid.py**: Device (HWID) management and statistics
- **squads.py**: Squad (group) management
- **mass.py**: Mass operations on users

### Services (`src/services/`)
- **api.py**: Async HTTP client for Remnawave API with authentication
- **cache.py**: Redis caching service for performance optimization

### Middleware (`src/middleware/`)
- **auth.py**: Admin authentication decorator and utilities

### Utils (`src/utils/`)
- **keyboards.py**: Telegram inline keyboard builders
- **formatters.py**: Data formatting for display
- **validators.py**: Input validation functions

## Architecture Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Async/Await**: All I/O operations are asynchronous
3. **Error Handling**: Comprehensive error handling with logging
4. **Type Hints**: Full type annotations for better IDE support
5. **Configuration**: Environment-based configuration
6. **Security**: Admin-only access with PIN confirmation for critical operations
7. **Logging**: Detailed logging for debugging and monitoring

## Development Workflow

1. **Local Development**:
   ```bash
   # Windows
   .\dev.ps1
   
   # Linux/Mac
   ./dev.sh
   ```

2. **Docker Development**:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Production Deployment**:
   ```bash
   docker-compose up -d
   ```

## Adding New Features

1. Create new handler in `src/handlers/`
2. Register handler in `src/main.py`
3. Add keyboard layouts in `src/utils/keyboards.py`
4. Add formatters in `src/utils/formatters.py` if needed
5. Add API methods in `src/services/api.py` if needed
6. Update documentation

## Testing

Tests should be placed in the `tests/` directory (to be implemented):
```
tests/
├── test_handlers/
├── test_services/
├── test_utils/
└── conftest.py
```

## Environment Variables

All configuration is done through environment variables (see `.env.example`):
- Telegram bot token
- Admin IDs
- Remnawave API credentials
- Logging level
- Redis configuration
