#!/usr/bin/env python3
"""
Test Runner for MoneyPrinterTurboPro
Runs different types of tests and generates reports
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False


def run_unit_tests(verbose=False, coverage=True):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", "unit"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(cmd, "Running unit tests")


def run_integration_tests(verbose=False, coverage=True):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(cmd, "Running integration tests")


def run_api_tests(verbose=False, coverage=True):
    """Run API tests"""
    cmd = ["python", "-m", "pytest", "tests/test_api.py", "-m", "api"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(cmd, "Running API tests")


def run_video_tests(verbose=False, coverage=True):
    """Run video generation tests"""
    cmd = ["python", "-m", "pytest", "tests/test_video_generator.py", "-m", "video"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(cmd, "Running video generation tests")


def run_all_tests(verbose=False, coverage=True):
    """Run all tests"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html", "--cov-report=xml"])
    
    return run_command(cmd, "Running all tests")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function"""
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Running specific test: {test_path}")


def run_linting():
    """Run code linting"""
    # Check if flake8 is available
    try:
        subprocess.run(["flake8", "--version"], check=True, capture_output=True)
        return run_command(["flake8", "app/", "tests/"], "Running flake8 linting")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  flake8 not available, skipping linting")
        return True


def run_formatting_check():
    """Check code formatting"""
    # Check if black is available
    try:
        subprocess.run(["black", "--version"], check=True, capture_output=True)
        return run_command(["black", "--check", "app/", "tests/"], "Checking code formatting with black")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  black not available, skipping formatting check")
        return True


def run_type_checking():
    """Run type checking with mypy"""
    # Check if mypy is available
    try:
        subprocess.run(["mypy", "--version"], check=True, capture_output=True)
        return run_command(["mypy", "app/"], "Running type checking with mypy")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  mypy not available, skipping type checking")
        return True


def run_security_scan():
    """Run security scanning with bandit"""
    # Check if bandit is available
    try:
        subprocess.run(["bandit", "--version"], check=True, capture_output=True)
        return run_command(["bandit", "-r", "app/"], "Running security scan with bandit")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  bandit not available, skipping security scan")
        return True


def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 Generating test report...")
    
    # Check if coverage report exists
    coverage_html = Path("htmlcov/index.html")
    if coverage_html.exists():
        print(f"✅ Coverage report available at: {coverage_html.absolute()}")
    else:
        print("⚠️  No coverage report found")
    
    # Check if test results exist
    test_results = Path(".pytest_cache")
    if test_results.exists():
        print(f"✅ Test results cached at: {test_results.absolute()}")
    else:
        print("⚠️  No test results cache found")
    
    print("\n📋 Test Summary:")
    print("- Unit tests: Core functionality testing")
    print("- Integration tests: Service interaction testing")
    print("- API tests: Endpoint and HTTP testing")
    print("- Video tests: Video generation pipeline testing")
    print("- Coverage: Code coverage analysis")
    print("- Linting: Code quality checks")
    print("- Formatting: Code style validation")
    print("- Type checking: Static type analysis")
    print("- Security: Vulnerability scanning")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Runner for MoneyPrinterTurboPro")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--video", action="store_true", help="Run video generation tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--format", action="store_true", help="Check code formatting only")
    parser.add_argument("--types", action="store_true", help="Run type checking only")
    parser.add_argument("--security", action="store_true", help="Run security scan only")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--quick", action="store_true", help="Quick test run (no coverage, no slow tests)")
    
    args = parser.parse_args()
    
    # Set coverage flag
    coverage = not args.no_coverage and not args.quick
    
    print("🧪 MoneyPrinterTurboPro Test Runner")
    print("=" * 50)
    
    success = True
    
    try:
        # Change to project directory
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Run specific test if specified
        if args.test:
            success = run_specific_test(args.test, args.verbose)
        
        # Run specific test types
        elif args.unit:
            success = run_unit_tests(args.verbose, coverage)
        elif args.integration:
            success = run_integration_tests(args.verbose, coverage)
        elif args.api:
            success = run_api_tests(args.verbose, coverage)
        elif args.video:
            success = run_video_tests(args.verbose, coverage)
        elif args.lint:
            success = run_linting()
        elif args.format:
            success = run_formatting_check()
        elif args.types:
            success = run_type_checking()
        elif args.security:
            success = run_security_scan()
        
        # Run all tests by default or if --all is specified
        elif args.all or not any([args.unit, args.integration, args.api, args.video, args.lint, args.format, args.types, args.security]):
            print("\n🎯 Running comprehensive test suite...")
            
            # Run code quality checks first
            if not args.quick:
                print("\n🔍 Running code quality checks...")
                success &= run_linting()
                success &= run_formatting_check()
                success &= run_type_checking()
                success &= run_security_scan()
            
            # Run tests
            print("\n🧪 Running tests...")
            success &= run_all_tests(args.verbose, coverage)
        
        # Generate report
        if success:
            generate_test_report()
        
        # Final status
        if success:
            print("\n🎉 All tests and checks completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests or checks failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
