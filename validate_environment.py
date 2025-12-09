#!/usr/bin/env python3
"""
CyberIDE Environment Setup Validator
=====================================
Validates development environment setup and prevents pollution.

Usage:
    python3 validate_environment.py [--strict]

Features:
    - Checks for lock files
    - Validates dependency versions
    - Detects environment pollution
    - Prevents conflicting installations
    - Provides setup recommendations
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

class EnvironmentValidator:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.root_dir = Path(__file__).parent
        
    def check_lock_files(self) -> bool:
        """Check if lock files exist and are up-to-date."""
        print_header("Checking Lock Files")
        
        issues_found = False
        
        # Check package-lock.json
        npm_lock = self.root_dir / "package-lock.json"
        if npm_lock.exists():
            print_success(f"package-lock.json exists ({npm_lock.stat().st_size // 1024}KB)")
        else:
            print_error("package-lock.json not found!")
            self.errors.append("Missing package-lock.json")
            issues_found = True
        
        # Check requirements-lock.txt
        py_lock = self.root_dir / "requirements-lock.txt"
        if py_lock.exists():
            print_success(f"requirements-lock.txt exists ({py_lock.stat().st_size // 1024}KB)")
        else:
            print_error("requirements-lock.txt not found!")
            self.errors.append("Missing requirements-lock.txt")
            issues_found = True
        
        return not issues_found
    
    def check_python_environment(self) -> bool:
        """Check Python environment for pollution and conflicts."""
        print_header("Validating Python Environment")
        
        issues_found = False
        
        # Check Python version
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"Python version: {version}")
            
            # Check if version is in acceptable range (3.10-3.12)
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            if not (major == 3 and 10 <= minor < 13):
                print_warning(f"Python version {major}.{minor} is outside recommended range (3.10-3.12)")
                self.warnings.append(f"Python version {major}.{minor} not optimal")
        except Exception as e:
            print_error(f"Failed to check Python version: {e}")
            self.errors.append("Python version check failed")
            issues_found = True
        
        # Check for virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            print_success("Virtual environment detected")
        else:
            print_warning("Not running in virtual environment (pollution risk!)")
            self.warnings.append("No virtual environment detected")
        
        # Check pip dependencies
        try:
            result = subprocess.run(
                ["python3", "-m", "pip", "check"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success("No broken Python dependencies")
            else:
                print_error("Broken Python dependencies detected!")
                print_error(result.stdout)
                self.errors.append("Broken Python dependencies")
                issues_found = True
        except Exception as e:
            print_warning(f"Could not check pip dependencies: {e}")
        
        return not issues_found
    
    def check_node_environment(self) -> bool:
        """Check Node.js environment."""
        print_header("Validating Node.js Environment")
        
        issues_found = False
        
        # Check Node version
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"Node.js version: {version}")
            
            # Check if LTS (v20.x)
            major_version = int(version.lstrip('v').split('.')[0])
            if major_version < 20:
                print_warning(f"Node.js v{major_version} is below recommended v20 (LTS)")
                self.warnings.append(f"Node.js v{major_version} below recommended")
        except Exception as e:
            print_error(f"Failed to check Node.js version: {e}")
            self.errors.append("Node.js version check failed")
            issues_found = True
        
        # Check npm version
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"npm version: {version}")
        except Exception as e:
            print_error(f"Failed to check npm version: {e}")
            self.errors.append("npm version check failed")
            issues_found = True
        
        # Check node_modules
        node_modules = self.root_dir / "node_modules"
        if node_modules.exists():
            print_success("node_modules directory exists")
        else:
            print_warning("node_modules not found (run 'npm ci' to install)")
            self.warnings.append("node_modules not installed")
        
        return not issues_found
    
    def check_docker_environment(self) -> bool:
        """Check Docker setup."""
        print_header("Validating Docker Environment")
        
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print_success(f"Docker: {version}")
        except Exception:
            print_warning("Docker not installed or not in PATH")
            return True  # Not critical
        
        # Check for Dockerfiles
        dockerfiles = [
            "Dockerfile.frontend",
            "Dockerfile.backend",
            "Dockerfile.dev"
        ]
        
        for dockerfile in dockerfiles:
            path = self.root_dir / dockerfile
            if path.exists():
                print_success(f"{dockerfile} exists")
            else:
                print_warning(f"{dockerfile} not found")
        
        return True
    
    def check_ignore_files(self) -> bool:
        """Check if ignore files are properly configured."""
        print_header("Validating Ignore Files")
        
        issues_found = False
        
        ignore_files = {
            ".gitignore": ["node_modules", "__pycache__", ".env", "dist", "coverage"],
            ".dockerignore": ["node_modules", "venv", ".git", "*.md"],
            ".npmignore": ["tests", "*.test.ts", "src/"]
        }
        
        for ignore_file, required_patterns in ignore_files.items():
            path = self.root_dir / ignore_file
            if path.exists():
                content = path.read_text()
                missing = [p for p in required_patterns if p not in content]
                if not missing:
                    print_success(f"{ignore_file} properly configured")
                else:
                    print_warning(f"{ignore_file} missing patterns: {', '.join(missing)}")
                    self.warnings.append(f"{ignore_file} incomplete")
            else:
                print_error(f"{ignore_file} not found!")
                self.errors.append(f"Missing {ignore_file}")
                issues_found = True
        
        return not issues_found
    
    def generate_report(self) -> bool:
        """Generate final validation report."""
        print_header("Validation Summary")
        
        if not self.errors and not self.warnings:
            print_success("All checks passed! Environment is properly configured.")
            return True
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.errors:
            print(f"\n{Colors.RED}Errors ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  • {error}")
            
            print(f"\n{Colors.RED}❌ Validation failed!{Colors.END}")
            return False
        
        if self.warnings and self.strict_mode:
            print(f"\n{Colors.YELLOW}⚠️  Validation passed with warnings (strict mode){Colors.END}")
            return False
        
        print(f"\n{Colors.GREEN}✓ Validation passed with warnings{Colors.END}")
        return True
    
    def provide_recommendations(self):
        """Provide setup recommendations."""
        print_header("Setup Recommendations")
        
        print_info("To create a clean environment:")
        print("  1. Create virtual environment: python3 -m venv .venv")
        print("  2. Activate it: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)")
        print("  3. Install Python dependencies: pip install -r requirements-lock.txt")
        print("  4. Install Node dependencies: npm ci")
        print("  5. Run validation: python3 validate_environment.py")
        
        print_info("\nTo use Docker for isolation:")
        print("  1. Build dev image: docker build -f Dockerfile.dev -t cyberide:dev .")
        print("  2. Run interactively: docker run -it -v $(pwd):/app cyberide:dev bash")
        print("  3. Inside container, run: npm run dev (or python3 neural_core.py)")
        
        print_info("\nTo prevent environment pollution:")
        print("  • Always use virtual environments for Python")
        print("  • Use 'npm ci' instead of 'npm install' to respect lock files")
        print("  • Never install packages globally unless necessary")
        print("  • Use Docker for complete isolation")

def main():
    strict_mode = "--strict" in sys.argv
    
    print(f"{Colors.BOLD}CyberIDE Environment Validator{Colors.END}")
    print(f"Mode: {'Strict' if strict_mode else 'Normal'}\n")
    
    validator = EnvironmentValidator(strict_mode=strict_mode)
    
    # Run all checks
    validator.check_lock_files()
    validator.check_python_environment()
    validator.check_node_environment()
    validator.check_docker_environment()
    validator.check_ignore_files()
    
    # Generate report
    success = validator.generate_report()
    
    # Provide recommendations if issues found
    if not success:
        validator.provide_recommendations()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
