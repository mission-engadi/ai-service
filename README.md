# AI Service - Mission Engadi

AI-powered content generation, translation, and automation service for the Mission Engadi platform.

## Overview

The AI Service provides comprehensive AI capabilities including:
- **Content Generation**: Social posts, articles, stories, donor communications, newsletters
- **Translation**: Multi-language translation (en/es/fr/pt) with quality scoring
- **Image Generation**: AI-powered image creation and variations
- **Content Enhancement**: Grammar correction, tone adjustment, SEO optimization, summarization
- **Automation**: Workflow automation for content publishing
- **Task Management**: AI task tracking with approval workflows
- **Template Management**: Reusable content templates
- **Generated Content**: Management and publishing of AI-generated content

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: Abacus.AI Platform
- **Authentication**: JWT tokens
- **Testing**: Pytest with async support
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Abacus.AI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mission-engadi/ai-service.git
cd ai-service
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the service**
```bash
# Using startup script
./scripts/start.sh

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

### Using Docker

```bash
docker-compose up -d
```

## API Endpoints

The service exposes **49 endpoints** across 8 routers:

- **Content Generation** (8 endpoints): `/api/v1/content/generate/*`
- **Translation** (5 endpoints): `/api/v1/translation/*`
- **Image Generation** (4 endpoints): `/api/v1/images/*`
- **Content Enhancement** (6 endpoints): `/api/v1/enhancement/*`
- **Automation** (7 endpoints): `/api/v1/automation/*`
- **AI Tasks** (6 endpoints): `/api/v1/tasks/*`
- **Content Templates** (7 endpoints): `/api/v1/templates/*`
- **Generated Content** (6 endpoints): `/api/v1/generated/*`

### API Documentation

- Swagger UI: `http://localhost:8010/docs`
- ReDoc: `http://localhost:8010/redoc`
- Full API Documentation: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Service Scripts

```bash
# Start service
./scripts/start.sh

# Stop service
./scripts/stop.sh

# Restart service
./scripts/restart.sh

# Check status
./scripts/status.sh
```

## Testing

Run tests with coverage:

```bash
# All tests
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_content_generation.py

# View coverage
open htmlcov/index.html
```

## Project Structure

```
ai_service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/          # 8 endpoint routers (49 total endpoints)
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   ├── security.py            # JWT authentication
│   │   └── abacus_client.py       # Abacus.AI integration
│   ├── db/
│   │   ├── session.py             # Database session
│   │   └── base_class.py          # Base model
│   ├── models/                     # SQLAlchemy models
│   ├── schemas/                    # Pydantic schemas
│   ├── services/                   # Business logic (8 services)
│   └── main.py                    # Application entry point
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── conftest.py                # Test fixtures
├── migrations/                     # Alembic migrations
├── scripts/                        # Startup scripts
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Configuration

Key environment variables:

```bash
# Service
SERVICE_NAME=ai-service
SERVICE_PORT=8010
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ai_service

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Abacus.AI
ABACUS_API_KEY=your-abacus-api-key
ABACUS_BASE_URL=https://api.abacus.ai

# External Services
CONTENT_SERVICE_URL=http://localhost:8002
SOCIAL_MEDIA_SERVICE_URL=http://localhost:8009
```

## Integration

The AI Service integrates with:

- **Auth Service**: User authentication and authorization
- **Content Service**: Content publishing and management
- **Social Media Service**: Social media posting
- **Abacus.AI Platform**: AI model inference

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed integration instructions.

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Production deployment
- Docker deployment
- Kubernetes deployment
- Environment configuration

## Development

### Adding New Endpoints

1. Create schema in `app/schemas/`
2. Add service method in `app/services/`
3. Create endpoint in `app/api/v1/endpoints/`
4. Register router in `app/api/v1/api.py`
5. Write tests in `tests/`

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Monitoring

- Health check: `GET /api/v1/health`
- Readiness check: `GET /api/v1/ready`
- Metrics: Available via Prometheus endpoint (if enabled)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Integration Guide](./INTEGRATION_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Implementation Summary](./IMPLEMENTATION_COMPLETE.md)

## Support

For issues and questions:
- GitHub Issues: https://github.com/mission-engadi/ai-service/issues
- Documentation: https://docs.mission-engadi.org

## License

Copyright © 2024 Mission Engadi. All rights reserved.

---

**Service Port**: 8010  
**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: December 2024
