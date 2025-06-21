# 🤖 TextFlow AI Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-green.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.x-orange.svg)
![MyPy](https://img.shields.io/badge/MyPy-typed-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent Telegram bot for text processing powered by Google Gemini AI**

[Features](#-features) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack) • [Database](#-database-schema) • [Repository Pattern](#-repository-pattern)

</div>

---

## 📖 About

TextFlow AI Assistant is a modern, scalable Telegram bot designed to help users with various text-related tasks using Google Gemini AI. Built with clean architecture principles and the Repository pattern, it provides a solid foundation for AI-powered chat applications.

### 🎯 Target Audience
- **Students** - assistance with academic materials
- **Content creators** - text generation and editing
- **Marketers** - brainstorming and content ideas
- **Anyone working with text** - quick access to AI capabilities

## ✨ Features

- 🤖 **AI-Powered Text Processing** - Integration with Google Gemini API
- 📱 **Telegram Bot Interface** - Modern aiogram 3.x framework
- 🗃️ **Conversation Context** - Maintains chat history for coherent responses
- 📊 **Usage Limits** - Daily request limits per user
- 🔄 **Message Status Tracking** - Real-time processing status
- 🏗️ **Clean Architecture** - SOLID principles with Repository pattern

## 🏗️ Architecture

The project follows clean architecture principles with clear separation of concerns:

```
📁 app/
├── 🔧 core/                     # Core business logic
│   ├── models/                  # SQLAlchemy models
│   │   ├── base.py             # Base model with common fields
│   │   ├── user.py             # User model
│   │   └── message.py          # Message model with roles/status
│   └── repositories/           # Data access layer
│       ├── base.py             # Generic BaseRepository[T]
│       ├── user_repository.py  # User-specific operations
│       └── message_repository.py # Message & context operations
├── 🔌 infrastructure/          # External concerns
│   └── database/               # Database configuration
│       ├── connection.py       # Async SQLAlchemy setup
│       └── migrations/         # Alembic migrations
├── 🎯 services/               # Business logic (planned)
├── 🤖 bot/                    # Telegram bot handlers (planned)
└── ⚙️ config/                 # Configuration (planned)
```

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.12+** - Modern Python with type hints
- **PostgreSQL 15+** - Robust relational database
- **SQLAlchemy 2.0+** - Modern async ORM
- **Alembic** - Database migrations

### Telegram & AI
- **aiogram 3.x** - Async Telegram bot framework
- **Google Gemini API** - Advanced AI text processing
- **google-generativeai** - Official Python SDK

### Development Tools
- **MyPy** - Static type checking
- **UV** - Fast Python package manager
- **Pydantic** - Data validation and settings

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    requests_today INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role message_role NOT NULL,           -- 'user' | 'assistant'
    status message_status DEFAULT 'pending', -- 'pending' | 'processing' | 'completed' | 'failed'
    content VARCHAR(1000) NOT NULL,
    ai_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Repository Pattern

### BaseRepository[T]
Generic repository providing CRUD operations for any model:

```python
class BaseRepository(Generic[ModelType]):
    async def get_by_id(self, id: int) -> Optional[ModelType]
    async def create(self, **kwargs: Any) -> ModelType  
    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]
    async def delete(self, id: int) -> bool
```

### UserRepository
Specialized operations for user management:

```python
class UserRepository(BaseRepository[User]):
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]
    async def get_or_create_user(self, telegram_id: int, ...) -> User
    async def update_user_info(self, telegram_id: int, ...) -> Optional[User]
    async def increment_requests_today(self, telegram_id: int) -> bool
    async def reset_daily_limits(self) -> int
```

### MessageRepository  
Handles conversation context and AI message flow:

```python
class MessageRepository(BaseRepository[Message]):
    async def create_message(self, user_id: int, role: MessageRole, ...) -> Message
    async def get_recent_context(self, user_id: int, limit: int = 10) -> List[Message]
    async def get_conversation_context(self, user_id: int, hours_back: int = 24) -> List[Message]
    async def update_message_status(self, message_id: int, status: MessageStatus) -> Optional[Message]
    async def delete_old_messages(self, days_old: int = 30) -> int
```

## 🎯 Design Principles

### SOLID Architecture
- ✅ **Single Responsibility** - Each repository handles one model
- ✅ **Open/Closed** - Easy to extend with new repositories
- ✅ **Liskov Substitution** - Repositories are interchangeable
- ✅ **Interface Segregation** - Focused, specific methods
- ✅ **Dependency Inversion** - Depend on abstractions

### Key Benefits
- 🔄 **Reusable** - Generic BaseRepository for all models
- 🧪 **Testable** - Easy to mock repositories for testing
- 🔧 **Maintainable** - Clear separation of concerns
- ⚡ **Scalable** - Async operations for high performance

## 📋 Current Status

### ✅ Completed
- [x] **Database Layer** - PostgreSQL setup with SQLAlchemy models
- [x] **Repository Layer** - Generic BaseRepository with specialized implementations
- [x] **Type Safety** - Full MyPy compatibility with Generic types
- [x] **Migrations** - Alembic database migrations
- [x] **Core Models** - User and Message models with proper relationships

### 🔄 In Progress
- [ ] **Service Layer** - Business logic implementation
- [ ] **Telegram Bot** - aiogram handlers and middleware
- [ ] **AI Integration** - Google Gemini API wrapper
- [ ] **Configuration** - Environment-based settings

### 📅 Planned
- [ ] **Authentication** - User session management
- [ ] **Rate Limiting** - Advanced usage controls
- [ ] **Monitoring** - Logging and metrics
- [ ] **Testing** - Comprehensive test suite
- [ ] **Deployment** - Docker containerization

## 🚀 Prerequisites

Before running this project, ensure you have:

- **Python 3.12+** installed
- **PostgreSQL 15+** running
- **Google Gemini API** key
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using clean architecture principles**

</div>