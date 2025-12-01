#!/usr/bin/env python3
"""
Startup script for CyberIDE Neural Core.

This script starts the FastAPI backend server with WebSocket support,
file monitoring, and real-time test execution.

Usage:
    python start_neural_core.py

Or make executable and run:
    chmod +x start_neural_core.py
    ./start_neural_core.py
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check that all required dependencies are installed."""
    required_packages = {
        "fastapi": "FastAPI web framework",
        "uvicorn": "ASGI server",
        "watchdog": "File system monitoring",
        "pytest": "Testing framework",
        "pydantic": "Data validation"
    }

    missing = []

    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(f"  - {package:15} ({description})")

    if missing:
        print("❌ Missing required dependencies:")
        print("\n".join(missing))
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False

    return True


def setup_environment():
    """Setup environment variables and paths."""
    # Set project root
    project_root = Path(__file__).parent.absolute()
    os.environ["CYBER_PROJECT_ROOT"] = str(project_root)

    # Add project to Python path
    sys.path.insert(0, str(project_root))

    print(f"✓ Project root: {project_root}")


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         🧠 CyberIDE NEURAL CORE STARTUP 🧠                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)

    print("✓ All dependencies installed\n")

    # Setup environment
    setup_environment()

    # Import and run neural core
    try:
        from neural_cli.main import main as run_neural_core
        run_neural_core()
    except KeyboardInterrupt:
        print("\n\n✓ Neural Core shutdown complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
