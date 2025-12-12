# Development Guide

## Development Environment

This guide covers day-to-day development workflow for CyberIDE.

## Prerequisites

Complete the [Installation Guide](installation.md) first.

## Starting Development

### Option 1: Unified Launch (Recommended)

Start both frontend and backend together:

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start everything
python3 neural_core.py

# Or using npm
npm start
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Separate Services

Run frontend and backend in separate terminals:

```bash
# Terminal 1 - Backend
source .venv/bin/activate
python3 neural_core.py --backend

# Terminal 2 - Frontend
npm run dev
```

## Development Workflow

### 1. Code Changes

Edit files in:
- `src/` - Frontend React + TypeScript
- `neural_cli/` - Backend Python + FastAPI
- `tests/` - Backend tests
- `src/__tests__/` - Frontend tests

### 2. Hot Reloading

Both frontend and backend support hot reloading:
- **Frontend**: Changes automatically reload (Vite HMR)
- **Backend**: Use `uvicorn --reload` (automatic in neural_core.py)

### 3. Testing

Run tests frequently:

```bash
# Frontend tests
npm test                  # Run once
npm run test:watch        # Watch mode
npm run test:coverage     # With coverage

# Backend tests
pytest                    # All tests
pytest -v                 # Verbose
pytest --cov=neural_cli tests/  # With coverage
```

### 4. Linting and Formatting

Fix code style before committing:

```bash
# Frontend
npm run lint              # ESLint
npm run lint -- --fix     # Auto-fix

# Backend (using Ruff)
ruff check .              # Check
ruff check --fix .        # Auto-fix
ruff format .             # Format
```

### 5. Type Checking

Verify types:

```bash
# Frontend
npx tsc --noEmit          # TypeScript check

# Backend
mypy neural_cli/          # Type check
```

## Code Standards

### TypeScript

- Strict mode enabled
- Use Zod for runtime validation (NO type casting with `as`)
- NO `any` types
- Proper error handling

Example:
```typescript
// WRONG
const data = response as NeuralStatus;

// CORRECT
const result = NeuralStatusSchema.safeParse(response);
if (!result.success) {
  throw new ValidationError(result.error);
}
const data = result.data;
```

### Python

- Type hints required
- Use Pydantic for models
- Structured logging with structlog
- NO generic exceptions

Example:
```python
# CORRECT
def calculate_metrics(data: MetricData) -> float:
    """Calculate illumination from metrics."""
    return data.coverage * 0.35 + data.modules * 0.25
```

## Project Structure

```
iAngel-CyberIDE/
├── src/                    # Frontend
│   ├── components/         # React components
│   ├── hooks/              # Custom hooks
│   ├── schemas/            # Zod schemas
│   └── types/              # TypeScript types
├── neural_cli/             # Backend
│   ├── main.py             # FastAPI app
│   ├── models.py           # Pydantic models
│   ├── metric_calculator.py
│   └── file_watcher.py
├── tests/                  # Backend tests
├── src/__tests__/          # Frontend tests
└── docs/                   # Documentation
```

## Debugging

### Frontend

Use browser DevTools:
1. Open Chrome DevTools (F12)
2. Check Console for errors
3. Use React DevTools extension
4. Network tab for WebSocket messages

### Backend

Use logging and debugger:

```python
# Add logging
import structlog
logger = structlog.get_logger()
logger.info("debug_point", value=some_value)

# Or use debugger
import pdb; pdb.set_trace()
```

## Common Tasks

### Adding a New Feature

1. Create a feature branch:
```bash
git checkout -b feature/your-feature
```

2. Implement feature with tests
3. Run linters and tests
4. Commit with conventional commit message:
```bash
git commit -m "feat: Add new neural region visualization"
```

5. Push and create pull request

### Updating Dependencies

```bash
# Python
pip-compile requirements.txt --output-file=requirements-lock.txt
pip install -r requirements-lock.txt

# Node.js
npm update package-name
```

### Debugging WebSocket Connection

Check connection status:
1. Frontend logs: Browser console
2. Backend logs: Terminal output
3. Network tab: WS frame messages

## Git Workflow

### Commit Message Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
test:     Tests
refactor: Code refactoring
style:    Formatting
chore:    Maintenance
```

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

## Performance

### Frontend

- Code splitting with dynamic imports
- Optimize Three.js rendering (60 FPS target)
- Use React.memo for expensive components
- Lazy load heavy dependencies

### Backend

- Async operations with FastAPI
- WebSocket connection pooling
- File watcher optimization
- Efficient metrics calculation

## Security Considerations

- Never commit secrets or API keys
- Validate all user inputs
- Use HTTPS in production
- Follow OWASP Top 10 guidelines
- See [Security Policy](../../SECURITY.md)

## Resources

- [TypeScript Standards](.github/standards/tsconfig.strict.json)
- [Python Standards](.github/standards/pyproject.strict.toml)
- [Testing Guide](testing.md)
- [Architecture Decisions](../adr/)
- [Contributing Guidelines](contributing.md)

## Getting Help

- Check [Troubleshooting Guide](troubleshooting.md)
- Review [existing issues](https://github.com/iAngelAi/iAngel-CyberIDE/issues)
- Ask in discussions
