# Webhook Inspector

A full-stack webhook inspector tool that receives webhooks, stores them in a Postgres database, and displays them in HTML templates made with Jinja2. Built as a portfolio project to demonstrate professional development practices including API design, database management, containerization, testing, and cloud deployment.

## 🎯 Project Purpose

This application showcases:
- RESTful API design with FastAPI
- PostgreSQL database integration with SQLAlchemy ORM
- Server-side rendering with Jinja2 templates
- Docker containerization
- Comprehensive unit testing with pytest
- CI/CD pipeline with GitHub Actions
- AWS cloud deployment (ECS + RDS)

## 🏗️ Architecture

### Backend
- **Framework:** FastAPI (Python 3.14)
- **Database:** PostgreSQL (local: Postgres.app, production: AWS RDS)
- **ORM:** SQLAlchemy with declarative models
- **Templates:** Jinja2 with Tailwind CSS

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** docker-compose for local development
- **CI/CD:** GitHub Actions (automated testing + deployment)
- **Cloud:** AWS ECS (Fargate) + RDS + ECR

### Testing
- **Framework:** pytest with TestClient
- **Coverage:** 4 unit tests covering API endpoints and validation
- **Test Database:** In-memory SQLite with StaticPool for isolation

## 🚀 Features

- **Webhook Capture:** POST endpoint accepts any JSON payload
- **Storage:** Persists request body, headers, and query parameters
- **Web Interface:** View all captured webhooks in a table format
- **Detail View:** Inspect individual webhooks with pretty-printed JSON
- **Validation:** UTF-8 encoding and JSON format validation
- **API Endpoints:** Separation between JSON API routes and HTML routes

## 📋 Prerequisites

- Python 3.14+
- PostgreSQL (for local development)
- Docker Desktop (optional, for containerized development)
- AWS CLI (for deployment)

## 🛠️ Local Setup

### 1. Clone Repository
```bash
git clone https://github.com/ancs29/webhook-inspector.git
cd webhook-inspector
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database
```bash
# Create PostgreSQL database
createdb webhooks_inspector

# Set environment variable (optional, uses localhost by default)
export DATABASE_URL=postgresql://localhost/webhooks_inspector
```

### 5. Run Development Server
```bash
uvicorn backend.main:app --reload
```

Visit http://localhost:8000 to see the web interface.

## 🐳 Docker Usage

### Local Development with Docker Compose
```bash
# Start both app and PostgreSQL containers
docker-compose up

# Stop containers
docker-compose down
```

### Build Production Image
```bash
docker build -t webhook-inspector .
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test
```bash
pytest tests/webhook_test.py::test_receive_and_get_webhooks
```

**Note:** Tests use in-memory SQLite and run independently of PostgreSQL status.

## 📡 API Documentation

### Webhook Endpoints (JSON API)

#### Capture Webhook
```http
POST /api/receive
Content-Type: application/json

{
  "event": "user.created",
  "data": { ... }
}
```

**Response:**
```json
{
  "status": "saved",
  "id": 1
}
```

#### List All Webhooks
```http
GET /api/webhooks
```

**Response:**
```json
[
  {
    "id": 1,
    "body": "{\"event\":\"user.created\"}",
    "headers": "{\"content-type\":\"application/json\"}",
    "query_params": "{}"
  }
]
```

#### Get Single Webhook
```http
GET /api/webhooks/{id}
```

**Response:**
```json
{
  "id": 1,
  "body": {"event": "user.created"},
  "headers": {"content-type": "application/json"},
  "query_params": {}
}
```

### Web Routes (HTML)

- `GET /` - Home page with webhook table
- `GET /{id}` - Detail page for individual webhook

## 🔄 CI/CD Pipeline

### Automated Testing
Every push triggers:
1. Python dependency installation
2. pytest execution with SQLite test database
3. Test failure prevents deployment

### Docker Validation
Manual trigger validates:
1. Docker image builds successfully
2. Unit tests pass inside container
3. App serves HTTP requests correctly

### Deployment (Coming Soon)
Automatic deployment to AWS ECS after tests pass.

## ☁️ AWS Deployment

**Status:** Configured for deployment (pending manual setup)

### Infrastructure Components
- **ECS Cluster:** Fargate serverless containers
- **RDS PostgreSQL:** Managed database instance
- **ECR:** Docker image registry
- **Application Load Balancer:** Traffic distribution

### Deployment Steps
Documentation coming after initial AWS setup.

## 📁 Project Structure

```
webhook-inspector/
├── backend/
│   ├── main.py          # FastAPI application and routes
│   ├── db.py            # Database configuration
│   └── model.py         # SQLAlchemy ORM model
├── tests/
│   └── webhook_test.py  # Unit tests
├── templates/
│   ├── index.html       # Home page template
│   └── webhook.html     # Detail page template
├── .github/
│   └── workflows/
│       ├── tests.yml         # CI testing pipeline
│       └── docker-test.yml   # Docker validation
├── Dockerfile           # Production container image
├── docker-compose.yml   # Local development setup
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🧩 Key Design Decisions

### Database Storage
- JSON data serialized to TEXT columns using `json.dumps()`
- Enables storage in PostgreSQL without JSONB complexity
- Parsed back to dicts with `json.loads()` on retrieval

### Route Separation
- `/api/*` routes return JSON (for programmatic access)
- `/*` routes return HTML (for browser viewing)
- Single codebase serves both API and web interface

### Test Isolation
- StaticPool for in-memory SQLite prevents connection pooling issues
- `autouse=True` fixture drops/recreates tables before each test
- Dependency injection override ensures tests never touch production DB

### Environment Configuration
- `DATABASE_URL` environment variable for flexible deployment
- Falls back to `postgresql://localhost/webhooks_inspector` for local dev
- Tests set their own SQLite URL before importing app modules

## 🔮 Possible Enhancements

- Automated webhook table refreshing
- Search and filter functionality
- Password authentication
- Automatically generated curl command (for the user to send webhooks with)

## 📚 Documentation

All python files include docstrings explaining the purpose of each module, class and function.

All python code has been formatted with Pylint and Black.

**Tech Stack:** Python • FastAPI • PostgreSQL • SQLAlchemy • Jinja2 • Docker • GitHub Actions • AWS ECS
