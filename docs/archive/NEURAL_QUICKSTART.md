# 🧠 CyberIDE Neural Core - Quick Start Guide

## ⚡ One-Command Launch

### Using Python Script (Recommended)
```bash
# Start everything (auto-installs dependencies)
./neural

# Or if not executable:
python3 neural_core.py
```

### Using npm
```bash
# Start everything
npm start

# Or specific npm scripts:
npm run neural          # Full system
npm run neural:backend  # Backend only
npm run neural:frontend # Frontend only
npm run neural:check    # System check
```

## 🚀 Command Reference

### Universal Launcher: `neural_core.py`

This intelligent script auto-detects and installs all dependencies before launching.

#### Basic Usage
```bash
# Full system launch (frontend + backend)
./neural

# Backend only
./neural --backend
# or
./neural -b

# Frontend only
./neural --frontend
# or
./neural -f

# System check only
./neural --check
# or
./neural -c

# Initialize project
./neural --init
# or
./neural -i

# Skip auto-install
./neural --no-install
```

## 🔧 Features

### Auto-Detection & Installation
The script automatically:
- ✅ Detects Python version (3.8+ required)
- ✅ Finds correct Python command (python3, python, py)
- ✅ Detects Node.js and npm
- ✅ Installs missing Python packages from requirements.txt
- ✅ Runs `npm install` if node_modules missing
- ✅ Creates neural_status.json if not exists
- ✅ Checks port availability (8000 for backend, 5173 for frontend)

### Smart Dependency Management
- Checks all required Python packages
- Updates pip before installing
- Installs from requirements.txt first
- Falls back to individual package installation
- Detects outdated node_modules

### Process Management
- Starts services in background
- Graceful shutdown with Ctrl+C
- Detects already running services
- Color-coded terminal output

## 📊 System Requirements

Automatically checked by the script:
- Python 3.8+ (auto-detected)
- Node.js 16+ (for frontend)
- npm (for package management)

## 🎯 Quick Examples

### First Time Setup
```bash
# Check your system
./neural --check

# Initialize and start everything
./neural --init
./neural
```

### Daily Development
```bash
# Just run this - it handles everything
./neural
```

### Testing Backend Changes
```bash
# Run backend only (frontend already running)
./neural --backend
```

### Production Build
```bash
# Check everything is ready
./neural --check

# Build frontend
npm run build
```

## 🌈 Visual Indicators

The script uses color coding:
- 🟢 **Green**: Success
- 🟡 **Yellow**: Warning/Info
- 🔴 **Red**: Error
- 🔵 **Blue**: Progress
- 🟦 **Cyan**: Headers/URLs

## 📝 Output Example

```
╔══════════════════════════════════════════════════════════╗
║    🧠  CYBERIDE NEURAL CORE - INITIALIZATION SYSTEM     ║
║         Intelligent Dependency & Launch Manager          ║
╚══════════════════════════════════════════════════════════╝

🔍 System Check
  Platform: Darwin 25.1.0
  ✅ Python: 3.14 (python3)
  ✅ Node.js: v24.10.0
  ✅ npm: 11.6.0

🔍 Checking Python dependencies...
  ✅ All Python dependencies installed!

🔍 Checking npm dependencies...
  ✅ All npm dependencies installed!

🚀 Starting Neural Core Backend...
  ✅ Backend started on http://localhost:8000
  📡 WebSocket: ws://localhost:8000/ws

🚀 Starting Neural Core Frontend...
  ✅ Frontend started on http://localhost:5173

============================================================
🧠 NEURAL CORE FULLY ACTIVATED!

  Frontend: http://localhost:5173
  Backend:  http://localhost:8000
  WebSocket: ws://localhost:8000/ws

Press Ctrl+C to shutdown all services
============================================================
```

## 🛠️ Troubleshooting

### Port Already in Use
If you see "Port X is in use", the service might already be running:
```bash
# Check what's running
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port

# Kill if needed
killall python3
killall node
```

### Dependencies Won't Install
```bash
# Force reinstall Python deps
pip install -r requirements.txt --force-reinstall

# Force reinstall npm deps
rm -rf node_modules package-lock.json
npm install
```

### Permission Denied
```bash
# Make script executable
chmod +x neural neural_core.py
```

## 🎉 That's It!

Just run `./neural` and watch your Neural Core come to life! The script handles everything else automatically.

**Neural Illumination Progress:** 🌑 → 🔵 → 🟣 → 🟡 → 🟢 → ⚡

---

*"Pas de test = Pas de lumière" - No test, no light!*