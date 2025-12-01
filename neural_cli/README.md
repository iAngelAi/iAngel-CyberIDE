# CyberIDE Neural Core

The **Neural Core** is the backend brain of CyberIDE, providing real-time project health monitoring, test execution, and WebSocket communication for the 3D brain visualization.

## Architecture

```
neural_cli/
├── main.py              # FastAPI app with WebSocket server
├── models.py            # Pydantic data models
├── file_watcher.py      # Watchdog file monitoring
├── test_analyzer.py     # Pytest integration & coverage
├── metric_calculator.py # Brain illumination metrics
└── __init__.py          # Package initialization
```

## Features

### 1. Real-Time WebSocket Communication
- Broadcasts project health updates to React frontend
- Sends file change events
- Streams test results as they complete
- Supports multiple concurrent client connections

### 2. File System Monitoring
- Watches `src/`, `tests/`, and `neural_cli/` directories
- Detects file creation, modification, deletion, and moves
- Intelligently ignores irrelevant files (node_modules, __pycache__, etc.)
- Debounces rapid changes to prevent event flooding
- Automatically triggers test runs when source files change

### 3. Test Execution & Analysis
- Integrates with pytest for test execution
- Collects code coverage using pytest-cov
- Parses test results (passed/failed/skipped)
- Identifies failing tests with error details
- Generates beautiful terminal summaries with color coding

### 4. Metric Calculation
- Calculates overall brain illumination (0-100%)
- Tracks multiple metrics:
  - **Test Coverage** (35% weight) - Most critical
  - **Module Completion** (25% weight) - Code completeness
  - **Documentation** (15% weight) - README, LICENSE, docs
  - **Integration** (15% weight) - API/MCP configuration
  - **Production Ready** (10% weight) - All tests passing

- Maps metrics to brain regions:
  - **Frontend** - React components and UI
  - **Backend** - Neural CLI Python code
  - **Tests** - Test suite health
  - **Documentation** - Docs completeness
  - **Integration** - External APIs/MCP

### 5. Progressive Illumination
The brain visualization illuminates progressively as you achieve milestones:

| Illumination | Status |
|-------------|---------|
| 0-25% | 🔴 Critical - No tests or very low coverage |
| 26-50% | 🟡 Warning - Basic structure, needs work |
| 51-75% | 🟢 Healthy - Good coverage, some gaps |
| 76-90% | 🟢 Excellent - High quality, well tested |
| 91-100% | ✨ Production Ready - All systems optimal |

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify installation:**
```bash
python start_neural_core.py
```

## Usage

### Starting the Neural Core

**Option 1: Using startup script (recommended)**
```bash
python start_neural_core.py
```

**Option 2: Direct module execution**
```bash
python -m neural_cli.main
```

**Option 3: Using uvicorn directly**
```bash
uvicorn neural_cli.main:app --host 0.0.0.0 --port 8000
```

### Accessing the Server

- **WebSocket:** `ws://localhost:8000/ws`
- **REST API:** `http://localhost:8000`
- **Status:** `http://localhost:8000/status`
- **Metrics:** `http://localhost:8000/metrics`

### Running Tests Manually

**Via API:**
```bash
curl -X POST http://localhost:8000/tests/run
```

**Via WebSocket:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.send(JSON.stringify({ command: 'run_tests' }));
```

## API Endpoints

### REST Endpoints

#### `GET /`
Health check - returns service status and current illumination.

**Response:**
```json
{
  "service": "CyberIDE Neural Core",
  "status": "online",
  "version": "1.0.0",
  "illumination": 0.75,
  "connected_clients": 2
}
```

#### `GET /status`
Get complete neural status.

**Response:** `NeuralStatus` object (see models.py)

#### `POST /tests/run`
Trigger a test run manually.

**Response:**
```json
{
  "message": "Test run initiated"
}
```

#### `GET /tests/results`
Get latest test results.

#### `GET /watcher/status`
Get file watcher statistics.

#### `GET /metrics`
Get detailed project metrics and file counts.

### WebSocket Endpoint

#### `WS /ws`
Real-time bidirectional communication.

**Client Commands:**
```json
{ "command": "run_tests" }
{ "command": "refresh_status" }
```

**Server Messages:**

**Neural Status Update:**
```json
{
  "type": "neural_status",
  "data": {
    "illumination": 0.75,
    "regions": { ... },
    "diagnostics": [ ... ],
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**File Change Event:**
```json
{
  "type": "file_change",
  "data": {
    "event_type": "modified",
    "file_path": "/path/to/file.py",
    "is_test_file": false,
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Test Result:**
```json
{
  "type": "test_result",
  "data": {
    "total_tests": 10,
    "passed": 8,
    "failed": 2,
    "coverage_percentage": 75.5,
    "duration": 2.34,
    "failed_tests": [ ... ]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Data Structures

### NeuralStatus
The main data structure representing the entire brain state.

```python
{
    "illumination": 0.75,  # 0.0 to 1.0
    "regions": {
        "frontend": {
            "status": "healthy",  # healthy/warning/error/offline
            "coverage": 85.0,
            "test_count": 10,
            "passing_tests": 8,
            "failing_tests": 2,
            "file_count": 25
        },
        # ... other regions
    },
    "diagnostics": [
        {
            "level": "ALERT",  # CAUTION or ALERT
            "region": "tests",
            "message": "2 tests failing",
            "details": "Immediate attention required"
        }
    ],
    "has_license": true,
    "has_readme": true,
    "documentation_complete": true,
    "api_configured": false
}
```

This data is:
1. Saved to `neural_status.json` on every update
2. Broadcast to WebSocket clients in real-time
3. Used by the frontend to render the 3D brain visualization

## Configuration

### Environment Variables

- `CYBER_PROJECT_ROOT` - Override project root path (default: current directory)

### Customizing Watched Directories

Edit `file_watcher.py` and modify `watch_dirs` in `FileWatcher.__init__()`.

### Customizing Ignored Patterns

Edit `file_watcher.py` and modify `ignored_patterns` in `NeuralFileHandler.__init__()`.

### Adjusting Metric Weights

Edit `metric_calculator.py` and modify `weights` in `MetricCalculator.__init__()`.

Default weights:
```python
{
    "test_coverage": 0.35,      # 35%
    "documentation": 0.15,       # 15%
    "module_completion": 0.25,   # 25%
    "integration": 0.15,         # 15%
    "production_ready": 0.10     # 10%
}
```

## Integration with React Frontend

The React frontend connects to the WebSocket endpoint to receive real-time updates:

```typescript
// src/hooks/useNeuralCore.ts
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'neural_status') {
    // Update brain visualization
    updateBrainIllumination(message.data.illumination);
    updateBrainRegions(message.data.regions);
  }

  if (message.type === 'test_result') {
    // Show test notification
    showTestResults(message.data);
  }
};
```

## Troubleshooting

### "pytest not found"
```bash
pip install pytest pytest-cov pytest-json-report
```

### "watchdog not found"
```bash
pip install watchdog
```

### WebSocket connection refused
1. Check that Neural Core is running: `curl http://localhost:8000`
2. Check CORS settings in `main.py` if using different ports
3. Check firewall settings

### Tests not running automatically
1. Check file watcher status: `curl http://localhost:8000/watcher/status`
2. Check that test files are in `tests/` directory
3. Check that test files start with `test_`

### Low illumination despite good coverage
Check these components of the illumination score:
1. Test coverage (35%)
2. Documentation files (15%)
3. Module completion (25%)
4. API/MCP configuration (15%)
5. All tests passing (10% bonus)

## Development

### Running in Development Mode

```bash
# Terminal 1: Start Neural Core
python start_neural_core.py

# Terminal 2: Start React frontend
cd /path/to/CyberIDE
npm run dev
```

### Adding New Metrics

1. Add metric calculation in `metric_calculator.py`
2. Update `ProjectMetrics` model in `models.py`
3. Update weight distribution in `MetricCalculator.__init__()`
4. Update `_calculate_illumination()` method

### Adding New WebSocket Message Types

1. Define message structure in `models.py`
2. Add handler in `main.py`
3. Update frontend WebSocket listener

## License

Part of the CyberIDE project. See main LICENSE file.

---

**Neural Pathways Restored. System Optimal.** 🧠✨
