# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Python Version Mismatch

**Problem:** "Python version 3.10-3.12 required"

**Solution:**
```bash
# Check current version
python3 --version

# Install Python 3.11
# Ubuntu/Debian:
sudo apt-get install python3.11 python3.11-venv

# macOS with Homebrew:
brew install python@3.11
```

#### Node.js Version Mismatch

**Problem:** "Node version 18+ required"

**Solution:**
```bash
# Using nvm (recommended)
nvm install 20
nvm use 20

# Verify
node --version  # Should show v20.x.x
```

#### Dependency Conflicts

**Problem:** "Conflicting dependencies detected"

**Solution:**
```bash
# Python: Clear and reinstall
pip cache purge
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt

# Node.js: Clear and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Runtime Issues

#### Port Already in Use

**Problem:** "Port 5173 or 8000 already in use"

**Solution:**
```bash
# Find process using the port
lsof -i :5173  # Frontend
lsof -i :8000  # Backend

# Kill the process
kill -9 <PID>

# Or change ports in .env
FRONTEND_PORT=5174
BACKEND_PORT=8001
```

#### WebSocket Connection Failed

**Problem:** "WebSocket connection to 'ws://localhost:8000/ws' failed"

**Solution:**
1. Ensure backend is running:
```bash
python3 neural_core.py --backend
```

2. Check backend logs for errors
3. Verify VITE_API_URL in .env matches backend URL
4. Check firewall settings

#### 3D Brain Not Rendering

**Problem:** Blank screen where 3D brain should be

**Solution:**
1. Check WebGL support: Visit https://get.webgl.org/
2. Update graphics drivers
3. Try a different browser (Chrome/Firefox recommended)
4. Check browser console for Three.js errors
5. Disable browser extensions that might block WebGL

### Development Issues

#### Hot Reload Not Working

**Problem:** Changes not reflecting in browser

**Solution:**
```bash
# Frontend
# Clear Vite cache
rm -rf node_modules/.vite

# Restart dev server
npm run dev

# Backend
# Ensure uvicorn --reload is active
# Check neural_core.py logs
```

#### Tests Failing

**Problem:** Tests fail locally but pass in CI

**Solution:**
```bash
# Ensure clean test environment
# Frontend
npm run test -- --clearCache

# Backend
pytest --cache-clear
```

#### Type Errors

**Problem:** TypeScript/mypy errors

**Solution:**
```bash
# TypeScript
npx tsc --noEmit

# If issues persist, regenerate types
npm run build

# Python
mypy neural_cli/ --show-error-codes
```

### Docker Issues

#### Build Fails with SSL Error

**Problem:** SSL certificate verification failed during Docker build

**Solution:**
This is a known CI environment issue. See [BUILD_NOTES](../reports/BUILD_NOTES.md).

Build locally instead:
```bash
docker build -f Dockerfile.dev -t cyberide:dev .
```

#### Container Won't Start

**Problem:** Docker container exits immediately

**Solution:**
```bash
# Check logs
docker logs <container_id>

# Run interactively to debug
docker run -it cyberide:dev bash
```

### Performance Issues

#### Slow Frontend Performance

**Problem:** Low FPS, laggy 3D rendering

**Solution:**
1. Check GPU acceleration is enabled in browser
2. Reduce neural nodes in config
3. Lower post-processing effects
4. Check browser console for performance warnings

#### Backend Sluggish

**Problem:** Slow API responses

**Solution:**
1. Check system resources (CPU, RAM)
2. Review backend logs for slow operations
3. Optimize file watcher patterns
4. Consider caching frequently accessed data

## Error Messages

### "ModuleNotFoundError: No module named 'X'"

**Cause:** Missing Python dependency

**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements-lock.txt
```

### "Cannot find module 'X'"

**Cause:** Missing Node.js dependency

**Solution:**
```bash
npm ci
# Or
npm install
```

### "EACCES: permission denied"

**Cause:** Permission issues with npm global install

**Solution:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm

# Or use nvm instead of global install
```

## Diagnostic Commands

```bash
# Check environment
python3 validate_environment.py

# Check Python installation
python3 --version
pip list

# Check Node.js installation
node --version
npm --version
npm list --depth=0

# Check ports
lsof -i :5173
lsof -i :8000

# Check system resources
top
# Or
htop
```

## Getting More Help

If your issue isn't covered here:

1. **Search existing issues:** [GitHub Issues](https://github.com/iAngelAi/iAngel-CyberIDE/issues)
2. **Check documentation:** [Documentation Index](../README.md)
3. **Enable debug logging:** Set `LOG_LEVEL=DEBUG` in `.env`
4. **Create a new issue:** Include:
   - OS and version
   - Python and Node.js versions
   - Complete error messages
   - Steps to reproduce
   - Relevant logs

## Reporting Bugs

When reporting bugs, include:

```bash
# Environment information
python3 --version
node --version
npm --version
cat /etc/os-release  # Linux
sw_vers  # macOS

# Error output
npm test 2>&1 | tee frontend-error.log
pytest -v 2>&1 | tee backend-error.log
```

## Additional Resources

- [Installation Guide](installation.md)
- [Development Guide](development.md)
- [ENVIRONMENT_SETUP.md](../../ENVIRONMENT_SETUP.md)
- [GitHub Issues](https://github.com/iAngelAi/iAngel-CyberIDE/issues)
