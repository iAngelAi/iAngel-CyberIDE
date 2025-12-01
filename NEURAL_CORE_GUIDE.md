# CyberIDE Neural Core - Complete Setup & Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the project root
cd /Users/felixlefebvre/CyberIDE

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Neural Core

```bash
# Option A: Using the startup script (recommended)
python start_neural_core.py

# Option B: Direct execution
python -m neural_cli.main
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║             🧠 CyberIDE NEURAL CORE 🧠                    ║
║                                                           ║
║         Neural Architecture for IDE Illumination         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🧠 CyberIDE NEURAL CORE Initializing...
============================================================
ℹ Project Root: /Users/felixlefebvre/CyberIDE
✓ Loaded neural status (illumination: 0.0%)
ℹ Performing initial project scan...
✓ Neural File Watcher active
============================================================
✓ NEURAL CORE Online - Ready to illuminate
============================================================
WebSocket endpoint: ws://localhost:8000/ws
Status file: /Users/felixlefebvre/CyberIDE/neural_status.json
============================================================
```

### 3. Start the React Frontend (in another terminal)

```bash
# In a new terminal
cd /Users/felixlefebvre/CyberIDE
npm run dev
```

The frontend will connect to the Neural Core automatically at `ws://localhost:8000/ws`.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (3D Brain Visualization)                    │
│                  localhost:5173                          │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket Connection
                     │ ws://localhost:8000/ws
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Neural Core                         │
│                  localhost:8000                          │
│                                                          │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   File     │  │     Test     │  │    Metric      │  │
│  │  Watcher   │  │   Analyzer   │  │  Calculator    │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│              Monitors: src/, tests/, neural_cli/        │
└──────────────────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  neural_status.json   │
         │  (Persistent State)   │
         └───────────────────────┘
```

## How It Works

### The Brain Illumination System

The Neural Core calculates a **brain illumination percentage** (0-100%) based on five key metrics:

| Metric | Weight | Description |
|--------|--------|-------------|
| Test Coverage | 35% | Code coverage from pytest-cov |
| Module Completion | 25% | Presence of key files and modules |
| Documentation | 15% | README, LICENSE, docs completeness |
| Integration | 15% | API/MCP provider configuration |
| Production Ready | 10% | All tests passing (bonus) |

### Progressive Illumination

As you develop your project, the brain lights up:

```
0%   ━━━━━━━━━━━━━━━━━━━━━━━━━━━ Dark (no tests)
25%  ████━━━━━━━━━━━━━━━━━━━━━━━ Dim (basic structure)
50%  ████████████━━━━━━━━━━━━━━━ Partial (good progress)
75%  ████████████████████━━━━━━━ Bright (excellent)
100% ████████████████████████████ FULL (production ready!)
```

### Brain Regions

The brain is divided into 5 regions, each with its own health status:

1. **Frontend** (src/)
   - Status based on test coverage
   - Green: >80% coverage
   - Yellow: 50-80% coverage
   - Red: <50% or failing tests

2. **Backend** (neural_cli/)
   - Status based on code quality
   - Tracks test coverage for Python backend

3. **Tests** (tests/)
   - Status based on test execution
   - Red (pulsing): Failing tests
   - Green: All tests passing

4. **Documentation**
   - Status based on docs completeness
   - Checks: README, LICENSE, SETUP, etc.

5. **Integration** (APIs/MCP)
   - Status based on external integrations
   - Checks: .env, API configs, MCP providers

### Real-Time Updates

The system updates in real-time when:

1. **File Changes** - Watchdog detects changes in monitored directories
2. **Test Execution** - pytest runs and reports results
3. **Metric Calculation** - Illumination percentage is recalculated
4. **WebSocket Broadcast** - All connected clients receive updates

## File Structure

```
CyberIDE/
├── neural_cli/                   # Neural Core Backend
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app & WebSocket server
│   ├── models.py                # Pydantic data models
│   ├── file_watcher.py          # Watchdog file monitoring
│   ├── test_analyzer.py         # pytest integration
│   ├── metric_calculator.py     # Illumination calculator
│   └── README.md                # Neural Core docs
│
├── tests/                        # Test directory (auto-created)
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   └── test_*.py                # Test files
│
├── src/                          # React frontend
│   ├── components/
│   ├── hooks/
│   └── App.tsx
│
├── start_neural_core.py          # Startup script
├── pytest.ini                    # pytest configuration
├── neural_status.json            # Generated state file
├── requirements.txt              # Python dependencies
└── package.json                  # Node dependencies
```

## Usage Examples

### Example 1: Check Neural Status

```bash
# Get current status
curl http://localhost:8000/status

# Get simplified health check
curl http://localhost:8000/

# Get detailed metrics
curl http://localhost:8000/metrics
```

### Example 2: Manual Test Run

```bash
# Trigger test run via API
curl -X POST http://localhost:8000/tests/run

# Get test results
curl http://localhost:8000/tests/results
```

### Example 3: WebSocket Communication (JavaScript)

```javascript
// Connect to Neural Core
const ws = new WebSocket('ws://localhost:8000/ws');

// Handle connection
ws.onopen = () => {
  console.log('✓ Connected to Neural Core');
};

// Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'neural_status':
      // Update brain visualization
      const { illumination, regions, diagnostics } = message.data;
      updateBrain(illumination, regions);
      showDiagnostics(diagnostics);
      break;

    case 'file_change':
      // Show file change notification
      console.log(`File ${message.data.event_type}: ${message.data.file_path}`);
      break;

    case 'test_result':
      // Show test results
      const { passed, failed, coverage_percentage } = message.data;
      showTestNotification(passed, failed, coverage_percentage);
      break;
  }
};

// Send commands
ws.send(JSON.stringify({ command: 'run_tests' }));
ws.send(JSON.stringify({ command: 'refresh_status' }));
```

### Example 4: Reading neural_status.json

```python
import json

# Read the current neural status
with open('neural_status.json', 'r') as f:
    status = json.load(f)

print(f"Illumination: {status['illumination'] * 100:.1f}%")

for region_name, region in status['regions'].items():
    print(f"{region_name}: {region['status']} ({region['coverage']:.1f}% coverage)")

for diagnostic in status['diagnostics']:
    print(f"{diagnostic['level']}: {diagnostic['message']}")
```

## Advanced Configuration

### Custom Project Root

```bash
# Set custom project root
export CYBER_PROJECT_ROOT=/path/to/your/project
python start_neural_core.py
```

### Adjust Metric Weights

Edit `/Users/felixlefebvre/CyberIDE/neural_cli/metric_calculator.py`:

```python
self.weights = {
    "test_coverage": 0.35,      # Increase for more test focus
    "documentation": 0.15,
    "module_completion": 0.25,
    "integration": 0.15,
    "production_ready": 0.10
}
```

### Custom Ignored Patterns

Edit `/Users/felixlefebvre/CyberIDE/neural_cli/file_watcher.py`:

```python
self.ignored_patterns = {
    ".git",
    "node_modules",
    "*.pyc",
    "your_custom_pattern"  # Add here
}
```

### Add More Watch Directories

```python
# In file_watcher.py
self.watch_dirs = [
    self.project_root / "src",
    self.project_root / "tests",
    self.project_root / "neural_cli",
    self.project_root / "custom_dir"  # Add here
]
```

## Development Workflow

### Typical Development Session

**Terminal 1: Neural Core**
```bash
cd /Users/felixlefebvre/CyberIDE
python start_neural_core.py

# Keep this running - it will:
# - Watch for file changes
# - Run tests automatically
# - Broadcast updates to frontend
```

**Terminal 2: React Frontend**
```bash
cd /Users/felixlefebvre/CyberIDE
npm run dev

# Your frontend at http://localhost:5173
# Will show live brain updates
```

**Terminal 3: Development**
```bash
cd /Users/felixlefebvre/CyberIDE

# Edit code
vim src/components/YourComponent.tsx

# File change detected → tests run → brain updates!

# Add tests
vim tests/test_your_feature.py

# Test runs → coverage increases → brain lights up!
```

### Watching the Brain Illuminate

1. **Start with 0% illumination** (no tests)
   - Brain is dark/offline

2. **Add first test** → ~15% illumination
   - Frontend region starts to glow

3. **Add more tests** → 30-50% illumination
   - Multiple regions light up
   - Yellow/green status

4. **Reach 80% coverage** → 70-80% illumination
   - Brain mostly illuminated
   - Green healthy regions

5. **All tests pass + docs complete** → 90-100% illumination
   - Full brain activation!
   - Production ready status
   - Satellite connection complete! 🛰️✨

## Diagnostic Messages

The Neural Core generates diagnostics for issues:

### ALERT (Red - Immediate Action Required)
```
ALERT: 2 test(s) failing
→ Immediate attention required. Tests must pass for production readiness.
```

### CAUTION (Yellow - Medium Risk)
```
CAUTION: Low test coverage (45.0%)
→ Medium risk. Aim for at least 80% coverage.

CAUTION: Incomplete documentation
→ Missing critical documentation files (README, LICENSE, or API docs).

CAUTION: API/MCP not configured
→ No external integrations detected. Configure API keys or MCP providers.
```

## Troubleshooting

### Issue: WebSocket not connecting

**Check:**
1. Neural Core is running: `curl http://localhost:8000`
2. Port 8000 is available: `lsof -i :8000`
3. CORS settings in `main.py` match your frontend port

**Solution:**
```bash
# Kill process on port 8000
kill $(lsof -t -i:8000)

# Restart Neural Core
python start_neural_core.py
```

### Issue: Tests not running automatically

**Check:**
1. File watcher status: `curl http://localhost:8000/watcher/status`
2. Files are in watched directories (src/, tests/, neural_cli/)
3. Python files have .py extension

**Solution:**
```bash
# Manual test run
curl -X POST http://localhost:8000/tests/run
```

### Issue: Illumination stuck at 0%

**Causes:**
1. No test files exist
2. Tests failing to run
3. Coverage not being calculated

**Solution:**
```bash
# Check if tests exist
ls tests/test_*.py

# If no tests, Neural Core creates placeholders automatically
# Check the logs when starting Neural Core

# Manual test run to see errors
cd /Users/felixlefebvre/CyberIDE
pytest tests/ -v
```

### Issue: Import errors in neural_cli

**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, watchdog, pytest; print('OK')"
```

## Production Deployment

### Environment Setup

```bash
# Set production environment
export CYBER_ENV=production
export CYBER_PROJECT_ROOT=/path/to/project

# Install dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn neural_cli.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Docker Deployment (Future)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY neural_cli/ neural_cli/
COPY start_neural_core.py .

EXPOSE 8000

CMD ["python", "start_neural_core.py"]
```

## Best Practices

1. **Keep Neural Core Running** - Leave it running during development for instant feedback

2. **Write Tests First** - Watch the brain light up as you add coverage

3. **Monitor Diagnostics** - Address ALERT messages immediately

4. **Aim for 80%+ Coverage** - This unlocks the highest illumination levels

5. **Complete Documentation** - README, LICENSE, and setup guides matter

6. **Configure Integrations** - API keys and MCP providers boost your score

7. **All Tests Must Pass** - This is required for 100% illumination

## Next Steps

1. **Start the Neural Core**: `python start_neural_core.py`
2. **Create Your First Test**: See tests light up the brain
3. **Watch Real-Time Updates**: Edit files and see instant feedback
4. **Reach 100% Illumination**: Achieve production-ready status

---

**Neural Pathways Restored. System Optimal.** 🧠✨

For detailed API documentation, see: `/Users/felixlefebvre/CyberIDE/neural_cli/README.md`
