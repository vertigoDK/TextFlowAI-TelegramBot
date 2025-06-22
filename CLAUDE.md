# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Bot
```bash
python main.py
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade migration
alembic downgrade -1
```

### Development
```bash
# Type checking
mypy .

# Code formatting
black .

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test modules
pytest tests/core/models/ -v
pytest tests/infrastructure/database/repositories/ -v
pytest tests/core/services/ -v
```

## Architecture Overview

This is a Telegram bot built with clean architecture principles using the Repository pattern. The project follows async/await patterns throughout.

### Key Architecture Patterns

**Repository Pattern**: Each model has its own repository inheriting from `BaseRepository[T]` generic class. This provides consistent CRUD operations across all entities.

**Dependency Injection via Container**: The `Container` class manages service creation. **CRITICAL**: Database sessions are created per-request, not shared across requests. Each call to `get_user_service()` or `get_message_service()` creates a new DB session.

**Message Flow**: 
1. User sends message → `handle_text_message()` in `messages.py`
2. New services created with fresh DB sessions via `container.get_*_service()`
3. Message stored → Context retrieved → AI generates response → Response stored

### Core Components

**Models** (`app/core/models/`):
- `User`: Telegram user with daily request limits
- `Message`: Chat messages with roles (user/assistant) and AI metadata

**Services** (`app/core/services/`):
- `UserService`: User management and rate limiting
- `MessageService`: Message CRUD and conversation context
- `AIGenerator`: Generic AI wrapper using provider pattern

**AI Integration** (`app/core/services/ai/`):
- Uses Google Gemini via LangChain
- `GoogleProvider`: Actual AI calls
- `ConversationPromptBuilder`: Formats message history into prompts

**Database Sessions**: 
- NEVER reuse DB sessions across requests
- Always create new sessions via `container.get_*_service()` methods
- Each request gets its own isolated database session

### Important Files

- `main.py`: Bot entry point and dispatcher setup
- `app/core/services/container.py`: Service factory with per-request DB sessions
- `app/bot/handlers/messages.py`: Main message handling logic
- `app/infrastructure/database/connection.py`: Async SQLAlchemy setup
- `app/config/settings.py`: Environment configuration via Pydantic

### Testing

The project has comprehensive test coverage with pytest:

**Test Structure:**
- `tests/core/models/` - Model validation and enum tests (24 tests)
- `tests/infrastructure/database/repositories/` - Repository CRUD and business logic (36 tests)
- `tests/core/services/` - Service layer and business rules
- `tests/conftest.py` - Test fixtures with in-memory SQLite database

**Key Testing Patterns:**
- Uses `pytest-asyncio` for async test support
- In-memory SQLite database for fast, isolated tests
- Comprehensive fixtures for test data setup
- Tests cover both happy path and edge cases

### Environment Variables Required

- `DATABASE_URL`: PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
- `GOOGLE_API_KEY`: Google Gemini API key