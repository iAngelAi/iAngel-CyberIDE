# Environment Setup Guide

## Purpose

This guide ensures reproducible, conflict-free development environment setup for CyberIDE.

## Prerequisites

- **Python**: 3.10 - 3.12 (recommended: 3.11)
- **Node.js**: 20.x LTS (recommended: 20.19+)
- **npm**: 10.x+ (comes with Node.js)
- **Docker**: Optional but recommended for isolation

## Lock Files

This project uses **lock files** to ensure reproducible builds:

| Lock File | Purpose | Package Manager |
|-----------|---------|-----------------|
| `package-lock.json` | Node.js dependencies | npm |
| `requirements-lock.txt` | Python dependencies | pip |

**CRITICAL**: Lock files are tracked in Git. **Never delete or ignore them.**

## Setup Methods

### Method 1: Native Installation (Recommended for Development)

#### Step 1: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On Linux/Mac:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

**Why virtual environment?**
- Prevents system Python pollution
- Isolates project dependencies
- Avoids version conflicts with other projects

#### Step 2: Install Python Dependencies

```bash
# Install from lock file (exact versions)
pip install -r requirements-lock.txt

# Verify no conflicts
python3 -m pip check
```

**DO NOT** use `pip install -r requirements.txt` directly - it will install latest versions, breaking reproducibility.

#### Step 3: Install Node.js Dependencies

```bash
# Install from lock file (exact versions)
npm ci

# Verify installation
npm list --depth=0
```

**Use `npm ci`**, not `npm install`:
- `npm ci` uses exact versions from `package-lock.json`
- `npm install` may update versions and modify lock file
- `npm ci` is faster and more reliable for CI/CD

#### Step 4: Validate Environment

```bash
# Run validation script
python3 validate_environment.py

# Run in strict mode (treats warnings as errors)
python3 validate_environment.py --strict
```

### Method 2: Docker (Recommended for Isolation)

#### Build Development Image

```bash
docker build -f Dockerfile.dev -t cyberide:dev .
```

#### Run Development Container

```bash
# Interactive shell
docker run -it -v $(pwd):/app cyberide:dev bash

# Frontend development
docker run -p 5173:5173 -v $(pwd):/app cyberide:dev npm run dev

# Backend development
docker run -p 8000:8000 -v $(pwd):/app cyberide:dev python3 neural_core.py
```

**Benefits of Docker:**
- Complete environment isolation
- Consistent across all platforms
- No system pollution
- Matches production environment

### Method 3: Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Workflow

### Running the Application

```bash
# Frontend (Vite dev server)
npm run dev
# Accessible at http://localhost:5173

# Backend (FastAPI server)
python3 neural_core.py --backend
# Accessible at http://localhost:8000

# Full stack (Neural Core)
python3 neural_core.py
```

### Running Tests

```bash
# Frontend tests (Vitest)
npm test                    # Run once
npm run test:watch         # Watch mode
npm run test:coverage      # With coverage

# Backend tests (pytest)
pytest                     # Run all tests
pytest tests/              # Specific directory
pytest -v                  # Verbose mode
pytest --cov=neural_cli    # With coverage
```

### Linting and Formatting

```bash
# Frontend (ESLint)
npm run lint

# Backend (Black + Pylint)
black neural_cli/          # Auto-format
pylint neural_cli/         # Lint check
```

### Building for Production

```bash
# Frontend build
npm run build
# Output: dist/

# Backend (Docker)
docker build -f Dockerfile.backend -t cyberide:backend .
docker build -f Dockerfile.frontend -t cyberide:frontend .
```

## 🔄 Updating Dependencies

### Adding New Dependencies

#### Python

```bash
# 1. Add to requirements.txt with version constraint
echo "new-package>=1.0.0,<2.0.0" >> requirements.txt

# 2. Regenerate lock file
pip-compile requirements.txt --output-file=requirements-lock.txt

# 3. Install new dependencies
pip install -r requirements-lock.txt

# 4. Verify no conflicts
python3 -m pip check

# 5. Commit both files
git add requirements.txt requirements-lock.txt
```

#### Node.js

```bash
# 1. Add package (automatically updates package.json and package-lock.json)
npm install --save package-name

# Or for dev dependencies
npm install --save-dev package-name

# 2. Commit both files
git add package.json package-lock.json
```

### Updating Existing Dependencies

#### Python

```bash
# Update specific package
pip-compile --upgrade-package package-name requirements.txt

# Update all packages (careful!)
pip-compile --upgrade requirements.txt

# Regenerate lock file
pip-compile requirements.txt --output-file=requirements-lock.txt
```

#### Node.js

```bash
# Update specific package
npm update package-name

# Check for outdated packages
npm outdated

# Update all packages (careful!)
npm update
```

## 🚨 Troubleshooting

### Issue: "Dependency conflict detected"

**Solution:**
```bash
# Python
pip-compile --resolver=backtracking requirements.txt

# Node.js
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Virtual environment not activated"

**Symptom:** Packages installing globally

**Solution:**
```bash
# Ensure you see (.venv) in your prompt
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Issue: "Lock file out of sync"

**Solution:**
```bash
# Python
pip-compile requirements.txt --output-file=requirements-lock.txt

# Node.js
npm ci  # Reinstall from lock file
```

### Issue: "Node modules not found"

**Solution:**
```bash
# Remove and reinstall
rm -rf node_modules
npm ci
```

### Issue: "Docker build fails"

**Solution:**
```bash
# Clear Docker cache
docker build --no-cache -f Dockerfile.dev -t cyberide:dev .

# Check Docker disk space
docker system df
docker system prune -a
```

## 🛡️ Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Always use lock files** - Ensures consistent dependencies
3. **Run security audits regularly**:
   ```bash
   # Node.js
   npm audit
   npm audit fix
   
   # Python
   pip-audit  # Requires: pip install pip-audit
   ```
4. **Keep dependencies updated** - But test thoroughly!
5. **Use virtual environments** - Prevents system-wide pollution

## Environment Validation

Run validation before starting work:

```bash
python3 validate_environment.py
```

Expected output:
```
✓ package-lock.json exists (209KB)
✓ requirements-lock.txt exists (8KB)
✓ Python version: Python 3.11.14
✓ Virtual environment detected
✓ No broken Python dependencies
✓ Node.js version: v20.19.6
✓ npm version: 10.8.2
✓ node_modules directory exists
✓ All checks passed!
```

## 🔗 Related Documentation

- [SETUP.md](./SETUP.md) - General setup instructions
- [README.md](./README.md) - Project overview
- [SECURITY.md](./SECURITY.md) - Security policies
- [Dockerfile.dev](./Dockerfile.dev) - Development Dockerfile
- [docker-compose.yml](./docker-compose.yml) - Docker Compose configuration

## 📞 Support

If you encounter issues not covered here:

1. Run the validation script: `python3 validate_environment.py`
2. Check existing GitHub issues
3. Create a new issue with validation output

---

**Remember**: Quality and reproducibility > Speed
