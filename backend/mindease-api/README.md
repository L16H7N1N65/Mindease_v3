# MindEase API - Mental Health RAG Platform

A comprehensive mental health platform with RAG (Retrieval-Augmented Generation) chatbot capabilities, built with FastAPI, PostgreSQL, and modern AI technologies.

## 🎯 Features

### Core Platform
- **Mental Health Tracking**: Mood monitoring, therapy session management
- **RAG Chatbot**: AI-powered mental health support with document retrieval
- **Multi-tenant Architecture**: Organization-based data isolation
- **Admin Dashboard**: Complete system management and analytics
- **ETL Pipeline**: Automated data processing and validation

### Technical Features
- **FastAPI**: High-performance async API framework
- **PostgreSQL + pgvector**: Vector database for semantic search
- **Redis**: Caching and session management
- **JWT Authentication**: Secure user authentication and authorization
- **Comprehensive Monitoring**: Health checks, metrics, and logging
- **Production Ready**: Docker deployment with full infrastructure

## 🏗️ Architecture

```
mindease-api/
├── app/
│   ├── core/                   # Core infrastructure
│   │   ├── api.py             # API configuration
│   │   ├── config.py          # Environment settings
│   │   ├── security.py        # Authentication utilities
│   │   ├── dependencies.py    # Dependency injection
│   │   ├── middleware.py      # CORS, rate limiting, logging
│   │   ├── exceptions.py      # Error handling
│   │   ├── cache.py           # Redis caching
│   │   └── monitoring.py      # Health checks & metrics
│   │
│   ├── db/                    # Database layer
│   │   ├── models/            # SQLAlchemy models
│   │   ├── migrations/        # Alembic migrations
│   │   ├── session.py         # Database sessions
│   │   └── database.py        # Database utilities
│   │
│   ├── routers/               # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── mood.py           # Mood tracking
│   │   ├── therapy.py        # Therapy management
│   │   ├── social.py         # Social features
│   │   ├── organization.py   # Multi-tenant management
│   │   ├── document.py       # Document management
│   │   ├── chat.py           # RAG chatbot
│   │   ├── admin.py          # Admin operations
│   │   └── health.py         # Health monitoring
│   │
│   ├── services/              # Business logic
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── mood_service.py   # Mood tracking logic
│   │   ├── chatbot_service.py # RAG chatbot logic
│   │   ├── embedding_service.py # Vector embeddings
│   │   ├── document_search_service.py # Semantic search
│   │   ├── mistral.py        # LLM integration
│   │   └── admin_service.py  # Admin operations
│   │
│   ├── schemas/               # Pydantic models
│   │   ├── auth.py           # Authentication schemas
│   │   ├── mood.py           # Mood tracking schemas
│   │   ├── chat.py           # Chat schemas
│   │   └── admin.py          # Admin schemas
│   │
│   └── etl/                   # ETL pipeline
│       ├── extractors.py     # Data extraction
│       ├── transformers.py   # Data transformation
│       ├── validators.py     # Data validation
│       ├── loaders.py        # Database loading
│       └── pipeline.py       # ETL orchestration
│
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Full stack deployment
├── requirements.txt           # Python dependencies
└── .env.example              # Environment template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and Setup**
```bash
git clone <repository-url>
cd mindease-api
cp .env.example .env
# Edit .env with your configuration
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
```bash
# Install PostgreSQL with pgvector
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb mindease_db
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_db.py
```

4. **Start Services**
```bash
# Start Redis
redis-server

# Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. **Full Stack with Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

2. **Production Deployment**
```bash
# Build production image
docker build -t mindease-api:latest .

# Run with production settings
docker run -d \
  --name mindease-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=your-db-url \
  -e REDIS_URL=your-redis-url \
  mindease-api:latest
```

## 📊 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

#### Mental Health Features
- `GET /api/v1/mood/entries` - Get mood entries
- `POST /api/v1/mood/entries` - Create mood entry
- `GET /api/v1/therapy/sessions` - Get therapy sessions
- `POST /api/v1/therapy/sessions` - Create therapy session

#### RAG Chatbot
- `POST /api/v1/chat/message` - Send chat message
- `GET /api/v1/chat/conversations` - Get conversations
- `POST /api/v1/chat/conversations` - Start new conversation

#### Admin Operations
- `POST /api/v1/admin/datasets/upload` - Upload dataset
- `GET /api/v1/admin/health` - System health
- `GET /api/v1/admin/analytics` - System analytics

#### Health Monitoring
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health status
- `GET /health/metrics` - System metrics

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mindease_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-app-secret

# External APIs
MISTRAL_API_KEY=your-mistral-key

# Features
ENABLE_RATE_LIMITING=true
ENABLE_CRISIS_DETECTION=true
```

### Production Settings

For production deployment:

```bash
ENVIRONMENT=production
DEBUG=false
WORKERS=4
LOG_LEVEL=WARNING
ALLOWED_HOSTS=["your-domain.com"]
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run ETL tests
pytest tests/test_etl_basic.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **ETL Tests**: Data pipeline testing
- **Performance Tests**: Load and stress testing

## 📈 Monitoring

### Health Checks
- **Basic**: `/health` - Simple status check
- **Detailed**: `/health/detailed` - All system components
- **Metrics**: `/health/metrics` - Performance metrics

### Monitoring Stack (Optional)
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Redis**: Metrics storage and caching

### Key Metrics
- API response times
- Database performance
- Cache hit rates
- Error rates
- System resource usage

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure authentication
- **Role-Based Access**: Admin, user, organization roles
- **Multi-tenant**: Organization-based data isolation

### Security Features
- **Rate Limiting**: API request throttling
- **CORS**: Cross-origin request handling
- **Security Headers**: HSTS, CSP, XSS protection
- **Input Validation**: Comprehensive data validation
- **Crisis Detection**: Mental health safety monitoring

## 🤖 AI & ML Features

### RAG System
- **Document Retrieval**: Semantic search with pgvector
- **LLM Integration**: Mistral AI for response generation
- **Context Management**: Conversation history and context
- **Safety Filtering**: Crisis detection and content filtering

### Embedding Service
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimension**: 384-dimensional vectors
- **Batch Processing**: Optimized embedding generation
- **Caching**: Redis-based embedding cache

### ETL Pipeline
- **Multi-format Support**: CSV, JSON, TXT, PDF, DOCX
- **Data Validation**: Mental health content validation
- **Quality Checks**: Relevance scoring and safety filtering
- **Batch Processing**: Optimized data loading

## 📚 Mental Health Features

### Mood Tracking
- Daily mood entries with scores (1-10)
- Energy level tracking
- Mood pattern analysis
- Trend visualization

### Therapy Management
- Session scheduling and tracking
- Therapist assignment
- Progress monitoring
- Goal setting and tracking

### Social Platform
- Community features
- Support groups
- Peer connections
- Moderated discussions

### Crisis Support
- Crisis keyword detection
- Emergency resource recommendations
- Safety plan integration
- Professional referrals

## 🏢 Multi-tenant Architecture

### Organization Management
- **Tenant Isolation**: Complete data separation
- **Admin Hierarchy**: Organization and system admins
- **Custom Branding**: Organization-specific customization
- **Usage Analytics**: Per-organization metrics

### Data Isolation
- **Database Level**: Organization-scoped queries
- **API Level**: Automatic tenant filtering
- **File Storage**: Organization-specific directories
- **Cache Isolation**: Tenant-aware caching

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# With Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# With Docker
docker-compose up -d
```

### Scaling
- **Horizontal**: Multiple API instances behind load balancer
- **Database**: Read replicas and connection pooling
- **Cache**: Redis cluster for high availability
- **Background Tasks**: Celery for async processing

## 📝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests before committing
5. Submit pull request

### Code Standards
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **Health Status**: http://localhost:8000/health
- **Admin Panel**: http://localhost:8000/admin

### Troubleshooting

#### Common Issues
1. **Database Connection**: Check PostgreSQL service and credentials
2. **Redis Connection**: Verify Redis service is running
3. **Migration Errors**: Run `alembic upgrade head`
4. **Import Errors**: Check PYTHONPATH and virtual environment

#### Performance Issues
1. **Slow Queries**: Check database indexes
2. **High Memory**: Monitor embedding service usage
3. **Cache Misses**: Verify Redis configuration
4. **Rate Limiting**: Adjust rate limit settings

### Getting Help
- Check the documentation
- Review health check endpoints
- Examine application logs
- Test with provided scripts

## 🎯 Roadmap

### Upcoming Features
- [ ] Real-time chat with WebSockets
- [ ] Mobile app API endpoints
- [ ] Advanced analytics dashboard
- [ ] Machine learning insights
- [ ] Integration with wearable devices
- [ ] Telehealth video integration

### Performance Improvements
- [ ] Database query optimization
- [ ] Advanced caching strategies
- [ ] Background task processing
- [ ] API response compression
- [ ] CDN integration

---

**MindEase API** - Empowering mental health through technology 🧠💙

