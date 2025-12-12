# Installation Guide

## System Requirements

### Minimum Requirements

- **Node.js**: 18.x or higher
- **Python**: 3.8 or higher (3.10-3.12 recommended)
- **npm**: 10.x or higher (comes with Node.js)
- **Git**: 2.x or higher

### Recommended Requirements

- **Node.js**: 20.x LTS
- **Python**: 3.11
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for dependencies and build artifacts

## Quick Installation

```bash
# Clone repository
git clone https://github.com/iAngelAi/iAngel-CyberIDE.git
cd iAngel-CyberIDE

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-lock.txt
npm ci

# Verify installation
python3 validate_environment.py

# Start application
python3 neural_core.py
```

For detailed instructions, environment troubleshooting, and Docker setup, see [ENVIRONMENT_SETUP.md](../../ENVIRONMENT_SETUP.md).

## Next Steps

- Read the [Quick Start Guide](../../QUICKSTART.md)
- Review the [Development Guide](development.md)
- Check the [Security Policy](../../SECURITY.md)
