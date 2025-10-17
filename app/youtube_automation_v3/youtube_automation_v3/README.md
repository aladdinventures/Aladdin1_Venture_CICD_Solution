# YouTube Automation System v3.0

**Copyright © 2025 Saeed Alaediny. All rights reserved.**

A modular, scalable YouTube content automation platform built with FastAPI, Celery, and Docker.

## 🎯 Project Status

**Current Version:** 3.0.0 (MVP in Development)  
**Base:** Refactored from v2.0 PoC  
**Completion:** Phase 1 - Core Infrastructure ✅

## 📋 What's Implemented

### ✅ Phase 1: Core Infrastructure (COMPLETE)

1. **Project Structure**
   - Modular architecture with clear separation of concerns
   - Core, API, Services, Providers, Models, Schemas, Tasks structure

2. **Database Layer**
   - SQLAlchemy ORM models (User, Channel, Video, VideoAnalytics)
   - PostgreSQL database configuration
   - Database session management

3. **Authentication System**
   - JWT-based authentication
   - Password hashing with bcrypt
   - Role-based access control (RBAC)
   - User registration and login schemas

4. **AI Provider Abstraction** (from v2.0)
   - OpenAI integration
   - Ollama integration (self-hosted, FREE!)
   - DeepSeek support
   - Factory pattern for easy provider switching

5. **Configuration Management** (from v2.0)
   - Pydantic Settings for type-safe configuration
   - Environment-based configuration
   - Support for multiple AI, TTS, and storage providers

6. **Docker Infrastructure**
   - Multi-container setup (web, db, redis, celery_worker, celery_beat)
   - Docker Compose orchestration
   - Health checks for all services
   - Volume management for data persistence

7. **Dependencies**
   - Complete requirements.txt with all necessary packages
   - FastAPI, SQLAlchemy, Celery, Redis, OpenAI, MoviePy, etc.

## 🚧 What's Pending (Phases 2-5)

### Phase 2: API Endpoints
- [ ] Authentication endpoints (`/api/v1/auth/*`)
- [ ] Channel management endpoints (`/api/v1/channels/*`)
- [ ] Video management endpoints (`/api/v1/videos/*`)
- [ ] Analytics endpoints (`/api/v1/analytics/*`)

### Phase 3: Content Generation
- [ ] Mock AI content generator
- [ ] Script generation service
- [ ] Video builder with FFmpeg/MoviePy
- [ ] TTS integration

### Phase 4: Upload & Automation
- [ ] YouTube uploader (stub for MVP)
- [ ] Celery task definitions
- [ ] Scheduled automation
- [ ] Progress tracking

### Phase 5: Advanced Features
- [ ] Analytics & notification system
- [ ] Logging infrastructure
- [ ] Testing suite
- [ ] Documentation

## 🏗️ Architecture

```
youtube_automation_v3/
├── core/                   # Core utilities
│   ├── config.py          # ✅ Configuration management
│   ├── database.py        # ✅ Database connection
│   └── auth.py            # ✅ Authentication utilities
├── models/                # Database models
│   └── database.py        # ✅ SQLAlchemy models
├── schemas/               # Pydantic schemas
│   └── auth.py            # ✅ Auth request/response schemas
├── api/                   # API endpoints
│   └── v1/                # API version 1
│       ├── auth.py        # ⏳ Authentication endpoints
│       ├── channels.py    # ⏳ Channel endpoints
│       ├── videos.py      # ⏳ Video endpoints
│       └── analytics.py   # ⏳ Analytics endpoints
├── services/              # Business logic
│   ├── content.py         # ⏳ Content generation
│   ├── video.py           # ⏳ Video building
│   └── upload.py          # ⏳ YouTube upload
├── providers/             # External service providers
│   ├── ai/                # ✅ AI providers (from v2.0)
│   ├── tts/               # ⏳ TTS providers
│   └── storage/           # ⏳ Storage providers
├── tasks/                 # Celery tasks
│   └── celery_app.py      # ⏳ Celery configuration
├── tests/                 # Test suite
├── main.py                # ✅ FastAPI application
├── requirements.txt       # ✅ Python dependencies
├── Dockerfile             # ✅ Docker image definition
├── docker-compose.yml     # ✅ Multi-container orchestration
└── .env.example           # ✅ Environment configuration template
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

### Installation

1. **Clone or extract the project:**
   ```bash
   cd youtube_automation_v3
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file:**
   - Set `JWT_SECRET_KEY` to a random string
   - Set `SECRET_KEY` to a random string
   - Configure AI provider (default: Ollama - FREE!)
   - Configure database credentials (if needed)

4. **Start with Docker Compose:**
   ```bash
   docker compose up -d
   ```

5. **Check service health:**
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

6. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Manual Installation (Without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   ```bash
   createdb youtube_automation
   ```

3. **Set up Redis:**
   ```bash
   redis-server
   ```

4. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start the application:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Start Celery worker (in another terminal):**
   ```bash
   celery -A tasks.celery_app worker --loglevel=info
   ```

7. **Start Celery beat (in another terminal):**
   ```bash
   celery -A tasks.celery_app beat --loglevel=info
   ```

## 🔧 Configuration

### AI Providers

The system supports multiple AI providers. Configure in `.env`:

**Ollama (Self-Hosted, FREE!):**
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**OpenAI:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-3.5-turbo
```

**DeepSeek (20x cheaper than OpenAI):**
```env
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=...
AI_MODEL=deepseek-chat
```

### TTS Providers

**Google TTS (Free tier available):**
```env
TTS_PROVIDER=gtts
TTS_VOICE=en-US-Standard-A
```

**Coqui TTS (Self-Hosted, FREE!):**
```env
TTS_PROVIDER=coqui
COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC
```

### Storage Providers

**Local Storage (Default):**
```env
STORAGE_PROVIDER=local
STORAGE_PATH=/app/storage
```

**S3/MinIO:**
```env
STORAGE_PROVIDER=s3
S3_ENDPOINT=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=youtube-automation
```

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `role`: User role (admin, user, viewer)
- `is_active`: Account status
- `is_verified`: Email verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

### Channels Table
- `id`: Primary key
- `name`: Channel name
- `description`: Channel description
- `niche`: Content niche
- `youtube_channel_id`: YouTube channel ID
- `status`: Channel status (active, inactive, suspended)
- `upload_schedule`: Upload frequency
- `auto_upload`: Auto-upload enabled
- `auto_generate`: Auto-generation enabled
- `settings`: JSON configuration
- `owner_id`: Foreign key to users
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Videos Table
- `id`: Primary key
- `title`: Video title
- `description`: Video description
- `script`: Video script
- `status`: Video status (draft, generating, generated, uploading, uploaded, failed)
- `youtube_video_id`: YouTube video ID
- `video_path`: Local video file path
- `thumbnail_path`: Thumbnail file path
- `duration`: Video duration (seconds)
- `file_size`: File size (bytes)
- `metadata`: JSON metadata (tags, category, etc.)
- `generation_progress`: Progress percentage (0-100)
- `error_message`: Error message (if failed)
- `channel_id`: Foreign key to channels
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `published_at`: Publication timestamp

### Video Analytics Table
- `id`: Primary key
- `views`: View count
- `likes`: Like count
- `dislikes`: Dislike count
- `comments`: Comment count
- `shares`: Share count
- `watch_time`: Total watch time (seconds)
- `average_view_duration`: Average view duration (seconds)
- `click_through_rate`: CTR percentage
- `engagement_rate`: Engagement percentage
- `revenue`: Estimated revenue
- `video_id`: Foreign key to videos (unique)
- `last_updated`: Last update timestamp

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication:

1. **Register a new user:**
   ```bash
   POST /api/v1/auth/register
   {
     "email": "user@example.com",
     "username": "johndoe",
     "password": "SecurePass123",
     "full_name": "John Doe"
   }
   ```

2. **Login:**
   ```bash
   POST /api/v1/auth/login
   {
     "username": "johndoe",
     "password": "SecurePass123"
   }
   ```

3. **Use the access token:**
   ```bash
   Authorization: Bearer <access_token>
   ```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 📝 API Endpoints (Planned)

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update current user
- `POST /api/v1/auth/change-password` - Change password

### Channels
- `GET /api/v1/channels` - List user's channels
- `POST /api/v1/channels` - Create new channel
- `GET /api/v1/channels/{id}` - Get channel details
- `PUT /api/v1/channels/{id}` - Update channel
- `DELETE /api/v1/channels/{id}` - Delete channel

### Videos
- `GET /api/v1/videos` - List channel's videos
- `POST /api/v1/videos` - Create new video
- `GET /api/v1/videos/{id}` - Get video details
- `PUT /api/v1/videos/{id}` - Update video
- `DELETE /api/v1/videos/{id}` - Delete video
- `POST /api/v1/videos/{id}/generate` - Generate video
- `POST /api/v1/videos/{id}/upload` - Upload to YouTube

### Analytics
- `GET /api/v1/analytics/channel/{id}` - Get channel analytics
- `GET /api/v1/analytics/video/{id}` - Get video analytics

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker compose ps db

# Check logs
docker compose logs db

# Restart database
docker compose restart db
```

### Celery Worker Issues
```bash
# Check worker is running
docker compose ps celery_worker

# Check logs
docker compose logs celery_worker

# Restart worker
docker compose restart celery_worker
```

### Redis Connection Issues
```bash
# Check Redis is running
docker compose ps redis

# Test Redis connection
redis-cli ping

# Restart Redis
docker compose restart redis
```

## 📚 Development Roadmap

### Phase 1: Core Infrastructure ✅ (COMPLETE)
- [x] Project structure
- [x] Database models
- [x] Authentication system
- [x] Docker infrastructure
- [x] Configuration management
- [x] AI provider abstraction

### Phase 2: API Endpoints (In Progress)
- [ ] Authentication endpoints
- [ ] Channel management endpoints
- [ ] Video management endpoints
- [ ] Analytics endpoints

### Phase 3: Content Generation
- [ ] Mock AI content generator
- [ ] Script generation service
- [ ] Video builder with FFmpeg/MoviePy
- [ ] TTS integration

### Phase 4: Upload & Automation
- [ ] YouTube uploader (stub)
- [ ] Celery task definitions
- [ ] Scheduled automation
- [ ] Progress tracking

### Phase 5: Advanced Features
- [ ] Analytics & notification
- [ ] Logging infrastructure
- [ ] Testing suite (80%+ coverage)
- [ ] Comprehensive documentation

### Phase 6: Production Readiness
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Monitoring & alerting
- [ ] Deployment automation

## 💰 Cost Optimization

### AI Provider Costs (per 1M tokens)

| Provider | Cost | Use Case |
|----------|------|----------|
| **Ollama** | **$0.00** | Development, Testing, Production (if you have GPU server) |
| DeepSeek | $0.10 | Production (20x cheaper than OpenAI) |
| OpenAI GPT-3.5 | $2.00 | Production (general content) |
| OpenAI GPT-4 | $30.00 | Production (high-quality content) |

**Recommendation:** Use **Ollama** (FREE!) for development and testing. Use **DeepSeek** for production (best cost/quality ratio).

## 📄 License

Copyright © 2025 Saeed Alaediny. All rights reserved.

## 🤝 Contributing

This is a proprietary project. Contributions are managed by the copyright holder.

## 📧 Support

For support, please contact: [Your Contact Information]

---

**Built with ❤️ using FastAPI, Celery, and Docker**

