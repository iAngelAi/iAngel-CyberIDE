#!/usr/bin/env python3
"""
🧠 CyberIDE Neural Core - Universal Startup Script
Auto-detects, installs dependencies, and launches both frontend and backend.
Handles virtual environments automatically for modern Python installations.
"""

import os
import sys
import subprocess
import json
import time
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import platform

# ANSI color codes for beautiful terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print the Neural Core ASCII header"""
    header = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║    🧠  {Colors.BOLD}CYBERIDE NEURAL CORE{Colors.END}{Colors.CYAN} - INITIALIZATION SYSTEM    ║
║         Intelligent Dependency & Launch Manager          ║
╚══════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(header)

def run_command(cmd: List[str], check: bool = True, capture_output: bool = True, env: Dict = None) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        # Use current environment plus any additional env vars
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)

        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            env=cmd_env
        )
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr if capture_output else str(e)
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"

def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system"""
    return shutil.which(command) is not None

def get_python_command() -> Optional[str]:
    """Detect the correct Python command (python3, python, py)"""
    for cmd in ['python3', 'python', 'py']:
        if check_command_exists(cmd):
            success, output = run_command([cmd, '--version'])
            if success and 'Python 3' in output:
                return cmd
    return None

def check_python_version(python_cmd: str) -> Tuple[bool, str]:
    """Check if Python version is 3.8 or higher"""
    success, output = run_command([python_cmd, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'])
    if success:
        version = output.strip()
        major, minor = map(int, version.split('.'))
        if major >= 3 and minor >= 8:
            return True, version
        return False, version
    return False, "Unknown"

def check_node_npm() -> Tuple[bool, bool, str, str]:
    """Check if Node.js and npm are installed"""
    node_exists = check_command_exists('node')
    npm_exists = check_command_exists('npm')

    node_version = ""
    npm_version = ""

    if node_exists:
        success, output = run_command(['node', '--version'])
        node_version = output.strip() if success else "Unknown"

    if npm_exists:
        success, output = run_command(['npm', '--version'])
        npm_version = output.strip() if success else "Unknown"

    return node_exists, npm_exists, node_version, npm_version

def check_virtual_env() -> Tuple[bool, Optional[str]]:
    """Check if we're in a virtual environment or if one exists"""
    # Check if already in a virtual environment
    if sys.prefix != sys.base_prefix:
        return True, sys.prefix

    # Check for common venv directories
    venv_dirs = ['venv', '.venv', 'env', '.env', 'neural_venv']
    for venv_dir in venv_dirs:
        venv_path = Path(venv_dir)
        if venv_path.exists() and (venv_path / 'bin' / 'python').exists():
            return True, str(venv_path.absolute())

    return False, None

def create_virtual_env(python_cmd: str) -> Tuple[bool, str]:
    """Create a virtual environment"""
    venv_path = Path('neural_venv')

    print(f"\n{Colors.BLUE}🔧 Creating virtual environment...{Colors.END}")

    # Create venv
    success, error = run_command([python_cmd, '-m', 'venv', str(venv_path)])

    if success:
        print(f"  {Colors.GREEN}✅ Virtual environment created: {venv_path}{Colors.END}")
        return True, str(venv_path.absolute())
    else:
        print(f"  {Colors.RED}❌ Failed to create virtual environment: {error}{Colors.END}")
        return False, ""

def get_venv_python(venv_path: str) -> str:
    """Get the Python executable from a virtual environment"""
    if platform.system() == 'Windows':
        python_path = Path(venv_path) / 'Scripts' / 'python.exe'
    else:
        python_path = Path(venv_path) / 'bin' / 'python'

    return str(python_path) if python_path.exists() else 'python3'

def is_externally_managed(python_cmd: str) -> bool:
    """Check if Python environment is externally managed (PEP 668)"""
    success, output = run_command([python_cmd, '-m', 'pip', 'install', '--dry-run', 'test-package-that-doesnt-exist'], capture_output=True)
    return 'externally-managed-environment' in output

def install_python_package(python_cmd: str, package: str, use_user: bool = False) -> bool:
    """Install a Python package using pip"""
    print(f"  {Colors.YELLOW}📦 Installing {package}...{Colors.END}")

    cmd = [python_cmd, '-m', 'pip', 'install']
    if use_user:
        cmd.append('--user')
    cmd.append(package)

    success, _ = run_command(cmd, capture_output=False)
    return success

def check_python_dependencies(python_cmd: str) -> Dict[str, bool]:
    """Check which Python dependencies are installed"""
    # Dependencies from CLAUDE.md and requirements.txt
    required_packages = {
        'fastapi': 'fastapi>=0.104.0',
        'uvicorn': 'uvicorn[standard]>=0.24.0',
        'python_multipart': 'python-multipart>=0.0.6',  # Note: import name differs
        'typer': 'typer>=0.9.0',  # CLI framework specified in CLAUDE.md
        'rich': 'rich>=13.6.0',
        'colorama': 'colorama>=0.4.6',
        'watchdog': 'watchdog>=3.0.0',
        'yaml': 'pyyaml>=6.0.1',  # Note: import name is 'yaml' not 'pyyaml'
        'pytest': 'pytest>=7.4.0',
        'pytest_cov': 'pytest-cov>=4.1.0',  # Note: import name with underscore
        'pytest_json_report': 'pytest-json-report>=1.5.0',
        'black': 'black>=23.9.1',
        'pylint': 'pylint>=3.0.0'
    }

    # Optional AI packages (check but don't require)
    optional_packages = {
        'openai': 'openai>=1.3.0',
        'anthropic': 'anthropic>=0.5.0'
    }

    installed = {}

    # Check required packages
    for import_name, requirement in required_packages.items():
        try:
            success, _ = run_command([python_cmd, '-c', f'import {import_name}'], capture_output=True)
            installed[requirement] = success
        except:
            installed[requirement] = False

    # Check optional packages (for info only)
    for import_name, requirement in optional_packages.items():
        try:
            success, _ = run_command([python_cmd, '-c', f'import {import_name}'], capture_output=True)
            if success:
                print(f"  {Colors.CYAN}ℹ️  Optional: {requirement} is installed{Colors.END}")
        except:
            pass

    return installed

def auto_install_python_dependencies(python_cmd: str, venv_path: Optional[str] = None, force_system: bool = False) -> bool:
    """Automatically install missing Python dependencies"""
    print(f"\n{Colors.BLUE}🔍 Checking Python dependencies...{Colors.END}")

    # If we have a venv, use its Python
    if venv_path and not force_system:
        python_cmd = get_venv_python(venv_path)
        print(f"  {Colors.CYAN}📦 Using virtual environment: {venv_path}{Colors.END}")

    deps = check_python_dependencies(python_cmd)
    missing = [pkg for pkg, installed in deps.items() if not installed]

    if not missing:
        print(f"  {Colors.GREEN}✅ All Python dependencies installed!{Colors.END}")
        return True

    print(f"  {Colors.YELLOW}📋 Missing packages: {len(missing)}{Colors.END}")
    for pkg in missing:
        print(f"    - {pkg}")

    # Install missing packages
    print(f"\n{Colors.BLUE}📦 Installing missing Python packages...{Colors.END}")

    # First ensure pip is up to date
    print(f"  {Colors.YELLOW}⬆️  Updating pip...{Colors.END}")
    run_command([python_cmd, '-m', 'pip', 'install', '--upgrade', 'pip'], capture_output=False)

    # Install requirements.txt if it exists
    req_file = Path('requirements.txt')
    if req_file.exists():
        print(f"  {Colors.YELLOW}📄 Installing from requirements.txt...{Colors.END}")
        success, _ = run_command([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'], capture_output=False)
        if success:
            print(f"  {Colors.GREEN}✅ Python dependencies installed!{Colors.END}")
            return True

    # Fallback to installing packages individually
    all_success = True
    for pkg in missing:
        if not install_python_package(python_cmd, pkg):
            all_success = False
            print(f"    {Colors.RED}❌ Failed to install {pkg}{Colors.END}")

    return all_success

def check_npm_dependencies() -> bool:
    """Check if node_modules exists and has content"""
    node_modules = Path('node_modules')
    package_json = Path('package.json')

    if not package_json.exists():
        return True  # No package.json means no npm dependencies needed

    if not node_modules.exists() or not any(node_modules.iterdir()):
        return False

    # Check if package.json is newer than node_modules
    if package_json.stat().st_mtime > node_modules.stat().st_mtime:
        return False

    return True

def auto_install_npm_dependencies() -> bool:
    """Automatically install missing npm dependencies"""
    print(f"\n{Colors.BLUE}🔍 Checking npm dependencies...{Colors.END}")

    if check_npm_dependencies():
        print(f"  {Colors.GREEN}✅ All npm dependencies installed!{Colors.END}")
        return True

    print(f"  {Colors.YELLOW}📦 Installing npm dependencies...{Colors.END}")
    success, _ = run_command(['npm', 'install'], capture_output=False)

    if success:
        print(f"  {Colors.GREEN}✅ npm dependencies installed!{Colors.END}")
        return True
    else:
        print(f"  {Colors.RED}❌ Failed to install npm dependencies{Colors.END}")
        return False

def check_port_available(port: int) -> bool:
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except:
            return False

def start_backend(python_cmd: str, background: bool = False, venv_path: Optional[str] = None) -> Optional[subprocess.Popen]:
    """Start the FastAPI backend"""
    print(f"\n{Colors.CYAN}🚀 Starting Neural Core Backend...{Colors.END}")

    # Check if neural_cli exists
    if not Path('neural_cli').exists():
        print(f"  {Colors.RED}❌ Backend not found! Run with --init to create it.{Colors.END}")
        return None

    # Check if port 8000 is available
    if not check_port_available(8000):
        print(f"  {Colors.YELLOW}⚠️  Port 8000 is in use. Backend might already be running.{Colors.END}")
        return None

    # Use venv Python if available
    if venv_path:
        python_cmd = get_venv_python(venv_path)

    cmd = [python_cmd, '-m', 'uvicorn', 'neural_cli.main:app', '--reload', '--port', '8000']

    if background:
        process = subprocess.Popen(cmd)
        time.sleep(2)  # Give it time to start
        print(f"  {Colors.GREEN}✅ Backend started on http://localhost:8000{Colors.END}")
        print(f"  {Colors.GREEN}📡 WebSocket: ws://localhost:8000/ws{Colors.END}")
        return process
    else:
        subprocess.run(cmd)
        return None

def start_frontend(background: bool = False) -> Optional[subprocess.Popen]:
    """Start the React frontend"""
    print(f"\n{Colors.CYAN}🚀 Starting Neural Core Frontend...{Colors.END}")

    # Check if src directory exists
    if not Path('src').exists():
        print(f"  {Colors.RED}❌ Frontend not found! Run with --init to create it.{Colors.END}")
        return None

    # Check if port 5173 is available
    if not check_port_available(5173):
        print(f"  {Colors.YELLOW}⚠️  Port 5173 is in use. Frontend might already be running.{Colors.END}")
        return None

    cmd = ['npm', 'run', 'dev']

    if background:
        process = subprocess.Popen(cmd)
        time.sleep(3)  # Give it time to start
        print(f"  {Colors.GREEN}✅ Frontend started on http://localhost:5173{Colors.END}")
        return process
    else:
        subprocess.run(cmd)
        return None

def init_project():
    """Initialize the project structure if it doesn't exist"""
    print(f"\n{Colors.BLUE}🔧 Initializing CyberIDE project structure...{Colors.END}")

    # This would normally create the project structure
    # For now, we'll just check what exists
    components = {
        'Frontend (React)': Path('src').exists(),
        'Backend (FastAPI)': Path('neural_cli').exists(),
        'Package.json': Path('package.json').exists(),
        'Requirements.txt': Path('requirements.txt').exists()
    }

    for component, exists in components.items():
        status = f"{Colors.GREEN}✅{Colors.END}" if exists else f"{Colors.RED}❌{Colors.END}"
        print(f"  {status} {component}")

    if not all(components.values()):
        print(f"\n{Colors.YELLOW}⚠️  Some components are missing. Create them first!{Colors.END}")
        return False

    return True

def system_check(show_venv: bool = True) -> Tuple[Optional[str], Optional[str]]:
    """Perform a comprehensive system check"""
    print(f"\n{Colors.BLUE}🔍 System Check{Colors.END}")
    print(f"  {Colors.CYAN}Platform:{Colors.END} {platform.system()} {platform.release()}")

    # Check Python
    python_cmd = get_python_command()
    if python_cmd:
        valid, version = check_python_version(python_cmd)
        status = f"{Colors.GREEN}✅{Colors.END}" if valid else f"{Colors.YELLOW}⚠️{Colors.END}"
        print(f"  {status} Python: {version} ({python_cmd})")
    else:
        print(f"  {Colors.RED}❌ Python 3 not found!{Colors.END}")
        return None, None

    # Check for virtual environment
    venv_exists, venv_path = check_virtual_env()
    if show_venv:
        if venv_exists:
            print(f"  {Colors.GREEN}✅{Colors.END} Virtual Environment: {venv_path}")
        else:
            print(f"  {Colors.YELLOW}📦{Colors.END} Virtual Environment: Not found (will create if needed)")

    # Check Node.js and npm
    node_exists, npm_exists, node_version, npm_version = check_node_npm()

    if node_exists:
        print(f"  {Colors.GREEN}✅{Colors.END} Node.js: {node_version}")
    else:
        print(f"  {Colors.RED}❌ Node.js not found!{Colors.END}")

    if npm_exists:
        print(f"  {Colors.GREEN}✅{Colors.END} npm: {npm_version}")
    else:
        print(f"  {Colors.RED}❌ npm not found!{Colors.END}")

    if python_cmd and node_exists and npm_exists:
        return python_cmd, venv_path
    else:
        return None, None

def create_neural_status():
    """Create an initial neural_status.json file"""
    status = {
        "illumination": 0.0,
        "regions": {
            "frontend": {"status": "dark", "coverage": 0},
            "backend": {"status": "dark", "coverage": 0},
            "tests": {"status": "dark", "coverage": 0},
            "documentation": {"status": "dark", "coverage": 0},
            "integration": {"status": "dark", "coverage": 0}
        },
        "diagnostics": [
            {"level": "INFO", "message": "Neural Core initialized"}
        ],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "has_license": Path("LICENSE").exists(),
        "has_readme": Path("README.md").exists()
    }

    with open('neural_status.json', 'w') as f:
        json.dump(status, f, indent=2)

    print(f"  {Colors.GREEN}✅ Created neural_status.json{Colors.END}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='🧠 CyberIDE Neural Core Manager')
    parser.add_argument('--backend', '-b', action='store_true', help='Start backend only')
    parser.add_argument('--frontend', '-f', action='store_true', help='Start frontend only')
    parser.add_argument('--init', '-i', action='store_true', help='Initialize project')
    parser.add_argument('--check', '-c', action='store_true', help='System check only')
    parser.add_argument('--no-install', action='store_true', help='Skip auto-install of dependencies')
    parser.add_argument('--no-venv', action='store_true', help='Skip virtual environment (use system Python)')
    parser.add_argument('--create-venv', action='store_true', help='Create virtual environment and exit')
    args = parser.parse_args()

    print_header()

    # System check
    python_cmd, venv_path = system_check(show_venv=not args.no_venv)
    if not python_cmd:
        print(f"\n{Colors.RED}❌ System requirements not met!{Colors.END}")
        print(f"{Colors.YELLOW}Please install Python 3.8+ and Node.js/npm{Colors.END}")
        sys.exit(1)

    if args.check:
        print(f"\n{Colors.GREEN}✅ System check complete!{Colors.END}")
        sys.exit(0)

    # Handle virtual environment creation
    if args.create_venv:
        if venv_path:
            print(f"\n{Colors.YELLOW}Virtual environment already exists: {venv_path}{Colors.END}")
        else:
            success, venv_path = create_virtual_env(python_cmd)
            if success:
                print(f"\n{Colors.GREEN}✅ Virtual environment created!{Colors.END}")
                print(f"{Colors.CYAN}Activate it with:{Colors.END}")
                if platform.system() == 'Windows':
                    print(f"  {venv_path}\\Scripts\\activate")
                else:
                    print(f"  source {venv_path}/bin/activate")
        sys.exit(0)

    # Check if we need a virtual environment (for externally managed environments)
    if not args.no_venv and not venv_path and is_externally_managed(python_cmd):
        print(f"\n{Colors.YELLOW}⚠️  Python environment is externally managed (PEP 668){Colors.END}")
        print(f"{Colors.BLUE}Creating virtual environment to install dependencies...{Colors.END}")

        success, venv_path = create_virtual_env(python_cmd)
        if not success:
            print(f"\n{Colors.RED}❌ Failed to create virtual environment{Colors.END}")
            print(f"{Colors.YELLOW}Try running with --no-venv to use system Python (may require sudo){Colors.END}")
            sys.exit(1)

    # Initialize if requested
    if args.init:
        if not init_project():
            sys.exit(1)
        create_neural_status()
        print(f"\n{Colors.GREEN}✅ Initialization complete!{Colors.END}")
        sys.exit(0)

    # Auto-install dependencies unless disabled
    if not args.no_install:
        # Install Python dependencies
        if not auto_install_python_dependencies(python_cmd, venv_path, force_system=args.no_venv):
            print(f"\n{Colors.YELLOW}⚠️  Some Python packages failed to install{Colors.END}")

            if not venv_path and not args.no_venv:
                print(f"{Colors.BLUE}Try creating a virtual environment first:{Colors.END}")
                print(f"  ./neural --create-venv")
                print(f"  ./neural")

            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)

        # Install npm dependencies if frontend will be started
        if not args.backend:  # If not backend-only
            if not auto_install_npm_dependencies():
                print(f"\n{Colors.YELLOW}⚠️  npm install failed{Colors.END}")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    sys.exit(1)

    # Create neural_status.json if it doesn't exist
    if not Path('neural_status.json').exists():
        create_neural_status()

    # Start services
    processes = []

    try:
        if args.backend:
            # Backend only
            start_backend(python_cmd, background=False, venv_path=venv_path)
        elif args.frontend:
            # Frontend only
            start_frontend(background=False)
        else:
            # Both (default)
            print(f"\n{Colors.CYAN}🧠 Starting Full Neural Core System...{Colors.END}")

            # Start backend in background
            backend_process = start_backend(python_cmd, background=True, venv_path=venv_path)
            if backend_process:
                processes.append(backend_process)

            # Start frontend in background
            frontend_process = start_frontend(background=True)
            if frontend_process:
                processes.append(frontend_process)

            if processes:
                print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
                print(f"{Colors.BOLD}🧠 NEURAL CORE FULLY ACTIVATED!{Colors.END}")
                print(f"\n  {Colors.CYAN}Frontend:{Colors.END} http://localhost:5173")
                print(f"  {Colors.CYAN}Backend:{Colors.END}  http://localhost:8000")
                print(f"  {Colors.CYAN}WebSocket:{Colors.END} ws://localhost:8000/ws")

                if venv_path:
                    print(f"  {Colors.CYAN}Virtual Env:{Colors.END} {venv_path}")

                print(f"\n{Colors.YELLOW}Press Ctrl+C to shutdown all services{Colors.END}")
                print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")

                # Wait for interrupt
                for process in processes:
                    process.wait()
            else:
                print(f"\n{Colors.YELLOW}⚠️  Services may already be running{Colors.END}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Shutting down Neural Core...{Colors.END}")
        for process in processes:
            process.terminate()
        print(f"{Colors.GREEN}✅ Neural Core shutdown complete{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == '__main__':
    main()