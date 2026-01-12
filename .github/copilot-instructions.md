<!-- Copilot instructions for the `webhook-inspector` repo -->

# Project Context

**Purpose:** A webhook inspector application built as a portfolio piece to demonstrate professional full-stack development skills to potential employers.

**Quality Standards:** Maintain professional-grade organization, detailed documentation, consistent formatting, and comprehensive test coverage. This is a showcase project—every commit should reflect production-ready code quality.

# Architecture Overview

## Backend (`backend/`)
- **Framework:** FastAPI with SQLAlchemy ORM
- **Database:** SQLite (production: `webhooks.db`, tests: in-memory with StaticPool)
- **Structure:** Python package with relative imports
  - `main.py` - FastAPI routes (API: POST /api/webhooks, GET /api/webhooks, GET /api/webhooks/{id}; Web: GET /, GET /{id})
  - `db.py` - SQLAlchemy engine and session configuration
  - `model.py` - WebhookTable ORM model
- **Key Patterns:**
  - JSON serialization for storing dicts in Text columns
  - Dependency injection with `get_db()` for database sessions
  - UTF-8 and JSON validation on webhook intake

## Frontend (`webhook-inspector-frontend/`)
- **Framework:** React 19 with Vite 7
- **Structure:** Standard Vite scaffold
  - `src/App.jsx` - Main application component
  - `vite.config.js` - Build configuration (needs proxy setup for backend)
  - `package.json` - Dependencies and scripts

## Testing (`tests/`)
- **Framework:** pytest with TestClient
- **Coverage:** 4 unit tests covering webhook creation, retrieval, validation errors
- **Key Patterns:**
  - In-memory SQLite with StaticPool for connection persistence
  - `@pytest.fixture(autouse=True)` for database isolation between tests
  - Tests verify JSON serialization, UTF-8 validation, individual/bulk retrieval

# Development Workflow

## Backend Setup
```zsh
# From repo root
python3 -m venv venv
source venv/bin/activate  # zsh
pip install -r requirements.txt
uvicorn backend.main:app --reload  # Run development server
pytest  # Run all tests
```

## Frontend Setup
```zsh
# From webhook-inspector-frontend/
npm install
npm run dev  # Starts Vite dev server on port 5173
npm run build  # Production build
npm run lint  # ESLint check
```

# Coding Standards for AI Agents

## General Principles
1. **Professional Quality:** Write production-ready code with clear variable names, proper error handling, and informative comments
2. **Test Everything:** Add tests for new features. Maintain 100% pass rate before committing
3. **Document Changes:** Update README.md when adding features or changing setup steps
4. **Git Hygiene:** Small, focused commits with descriptive messages

## Backend Conventions
- Use relative imports within `backend/` package (`.db`, `.model`, `.main`)
- Serialize Python objects to JSON before storing in Text columns
- Include type hints on function signatures
- Handle database sessions with try/finally or context managers
- Validate input data (UTF-8 encoding, JSON structure) before persisting

## Frontend Conventions
- Follow React hooks patterns (useState, useEffect for API calls)
- Use semantic HTML and accessible markup
- Implement error boundaries for graceful failure handling
- Keep components focused and single-responsibility

## Testing Conventions
- Use descriptive test names: `test_<action>_<expected_outcome>`
- Arrange-Act-Assert structure
- Test both success and failure paths
- Use fixtures for setup/teardown (database clearing, test data)
- Import from `backend` package, not relative paths

## File Organization
- `requirements.txt` - Backend Python dependencies
- `webhook-inspector-frontend/package.json` - Frontend Node dependencies
- `.gitignore` - Excludes `venv/`, `webhooks.db`, `node_modules/`, `__pycache__/`, `.vscode/`
- Keep production data files (`webhooks.db`) out of version control

# Common Tasks for AI Agents

## Adding Backend Endpoint
1. Add route function in `backend/main.py`
2. Update `model.py` if new database columns needed
3. Add corresponding test in `tests/webhook_test.py`
4. Update README.md with endpoint documentation

## Adding Frontend Feature
1. Update `src/App.jsx` or create new component
2. Configure proxy in `vite.config.js` if calling backend
3. Add CORS middleware in `backend/main.py` if needed
4. Test cross-origin requests work correctly

## Database Schema Changes
1. Modify `backend/model.py` ORM model
2. Delete `webhooks.db` (dev database will recreate)
3. Update tests to match new schema
4. Document migration strategy in commit message

## Performance/Optimization
1. Add indexes to frequently queried columns
2. Implement pagination for large result sets
3. Consider caching strategies for repeated queries
4. Profile with appropriate tools before optimizing

# What NOT to Assume

- **Don't add** formatters (black, prettier) without asking—user may have preferences
- **Don't add** CI/CD without approval—this is planned but not yet implemented
- **Don't add** heavy frameworks or dependencies without justification
- **Don't create** documentation files summarizing changes unless requested
- **Don't guess** at implementation details—ask clarifying questions for ambiguous requirements

# Tech Stack Details

- **Python:** 3.14 (FastAPI, SQLAlchemy, pytest)
- **Node:** Latest stable (React 19, Vite 7, ESLint)
- **Database:** SQLite with Text columns for JSON storage
- **Shell:** zsh on macOS
- **Editor:** VS Code with GitHub Copilot

# Current State & Priorities

**Completed:**
- ✅ FastAPI backend with webhook capture/retrieval endpoints
- ✅ SQLite persistence with proper JSON serialization
- ✅ 4 passing unit tests with in-memory database isolation
- ✅ React frontend scaffolded with Vite

**In Progress:**
- Frontend UI implementation (webhook list/detail views)
- Backend-frontend integration (proxy, CORS, API calls)

**Future Considerations:**
- Real-time webhook updates (WebSockets or polling)
- Search/filter functionality
- Request replay capabilities
- Deployment configuration

---

**Agent Guidance:** Treat every change as if it's being reviewed in a job interview. Prioritize clarity, maintainability, and professional standards. When in doubt, ask rather than assume.
