#!/usr/bin/env python3
"""
Validation script for CyberIDE Neural Core.

This script checks that all components are properly installed
and can be imported without errors.
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_imports():
    """Check that all required imports work."""
    print_header("Checking Imports")

    required_modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn ASGI Server"),
        ("watchdog", "File System Watcher"),
        ("pytest", "Testing Framework"),
        ("pydantic", "Data Validation"),
    ]

    all_ok = True

    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name:20} ({description})")
        except ImportError as e:
            print(f"  ✗ {module_name:20} (MISSING - {description})")
            all_ok = False

    return all_ok


def check_neural_cli():
    """Check that neural_cli modules can be imported."""
    print_header("Checking Neural CLI Modules")

    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    modules = [
        ("neural_cli.models", "Data Models"),
        ("neural_cli.file_watcher", "File Watcher"),
        ("neural_cli.test_analyzer", "Test Analyzer"),
        ("neural_cli.metric_calculator", "Metric Calculator"),
        ("neural_cli.main", "FastAPI Application"),
    ]

    all_ok = True

    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name:30} ({description})")
        except Exception as e:
            print(f"  ✗ {module_name:30} (ERROR: {e})")
            all_ok = False

    return all_ok


def check_file_structure():
    """Check that all required files exist."""
    print_header("Checking File Structure")

    project_root = Path(__file__).parent
    required_files = [
        "neural_cli/__init__.py",
        "neural_cli/main.py",
        "neural_cli/models.py",
        "neural_cli/file_watcher.py",
        "neural_cli/test_analyzer.py",
        "neural_cli/metric_calculator.py",
        "start_neural_core.py",
        "pytest.ini",
        "requirements.txt",
    ]

    all_ok = True

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {file_path:40} ({size:,} bytes)")
        else:
            print(f"  ✗ {file_path:40} (MISSING)")
            all_ok = False

    return all_ok


def test_basic_functionality():
    """Test basic functionality of neural_cli."""
    print_header("Testing Basic Functionality")

    try:
        # Test model creation
        from neural_cli.models import NeuralStatus, BrainRegion, RegionStatus

        status = NeuralStatus(
            illumination=0.5,
            regions={
                "test": BrainRegion(status=RegionStatus.HEALTHY, coverage=75.0)
            }
        )
        print(f"  ✓ Created NeuralStatus with {status.illumination:.0%} illumination")

        # Test metric calculator
        from neural_cli.metric_calculator import MetricCalculator

        calculator = MetricCalculator(str(Path(__file__).parent))
        print(f"  ✓ Initialized MetricCalculator for {calculator.project_root.name}")

        # Test file counts
        counts = calculator.count_files_by_region()
        print(f"  ✓ Counted files: {counts}")

        return True

    except Exception as e:
        print(f"  ✗ Error testing functionality: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main validation routine."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║      🧠 CyberIDE Neural Core Validation 🧠                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    results = []

    # Run all checks
    results.append(("Dependencies", check_imports()))
    results.append(("File Structure", check_file_structure()))
    results.append(("Neural CLI Modules", check_neural_cli()))
    results.append(("Basic Functionality", test_basic_functionality()))

    # Print summary
    print_header("Validation Summary")

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:10} {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("""
✓ All validations passed!

Your Neural Core is ready to run.

Next steps:
  1. Start the Neural Core:
     python start_neural_core.py

  2. In another terminal, start the React frontend:
     npm run dev

  3. Watch your brain illuminate as you develop!

For more information, see:
  - NEURAL_CORE_GUIDE.md
  - neural_cli/README.md
        """)
        return 0
    else:
        print("""
✗ Some validations failed.

Please fix the errors above and try again.

Common fixes:
  - Install missing dependencies: pip install -r requirements.txt
  - Check that you're in the project root directory
  - Ensure all neural_cli files were created correctly
        """)
        return 1


if __name__ == "__main__":
    sys.exit(main())
