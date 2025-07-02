#!/usr/bin/env python3
"""
Test runner script for FaceAuth platform.
Provides convenient commands to run different test suites and generate reports.
"""

import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        
        print(f"✅ SUCCESS ({duration:.2f}s)")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ FAILED ({duration:.2f}s)")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def run_basic_tests():
    """Run basic functionality tests."""
    cmd = ["python", "-m", "pytest", "tests/test_basic.py", "-v", "--tb=short"]
    return run_command(cmd, "Basic Functionality Tests")

def run_core_tests():
    """Run core module tests."""
    tests = [
        "tests/test_enrollment.py",
        "tests/test_authentication.py"
    ]
    cmd = ["python", "-m", "pytest"] + tests + ["-v", "--tb=short"]
    return run_command(cmd, "Core Module Tests")

def run_security_tests():
    """Run security-related tests."""
    tests = [
        "tests/test_security.py",
        "tests/test_encryption.py"
    ]
    cmd = ["python", "-m", "pytest"] + tests + ["-v", "--tb=short"]
    return run_command(cmd, "Security Tests")

def run_integration_tests():
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "tests/test_integration.py", "-v", "--tb=short"]
    return run_command(cmd, "Integration Tests")

def run_performance_tests():
    """Run performance tests."""
    cmd = ["python", "-m", "pytest", "tests/test_performance.py", "-v", "--tb=short", "-s"]
    return run_command(cmd, "Performance Tests")

def run_cli_tests():
    """Run CLI tests."""
    cmd = ["python", "-m", "pytest", "tests/test_cli.py", "-v", "--tb=short"]
    return run_command(cmd, "CLI Tests")

def run_all_tests():
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    return run_command(cmd, "All Tests")

def run_with_coverage():
    """Run tests with coverage report."""
    try:
        import coverage
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "--cov=faceauth",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ]
        return run_command(cmd, "Tests with Coverage")
    except ImportError:
        print("Coverage package not installed. Running without coverage...")
        return run_all_tests()

def install_test_dependencies():
    """Install test dependencies."""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "psutil>=5.9.0",
        "memory-profiler>=0.60.0"
    ]
    
    for dep in dependencies:
        cmd = ["pip", "install", dep]
        success = run_command(cmd, f"Installing {dep}")
        if not success:
            print(f"Warning: Failed to install {dep}")

def run_quick_tests():
    """Run a quick subset of tests for rapid feedback."""
    tests = [
        "tests/test_basic.py",
        "tests/test_enrollment.py::TestFaceEnrollment::test_successful_enrollment",
        "tests/test_authentication.py::TestFaceAuthenticator::test_successful_authentication",
        "tests/test_encryption.py::TestEncryptionManager::test_encrypt_decrypt_file"
    ]
    cmd = ["python", "-m", "pytest"] + tests + ["-v", "--tb=short"]
    return run_command(cmd, "Quick Test Suite")

def run_smoke_tests():
    """Run smoke tests to verify basic functionality."""
    tests = [
        "tests/test_basic.py::test_imports",
        "tests/test_enrollment.py::TestFaceEnrollment::test_enrollment_initialization",
        "tests/test_authentication.py::TestFaceAuthenticator::test_authenticator_initialization"
    ]
    cmd = ["python", "-m", "pytest"] + tests + ["-v", "--tb=short"]
    return run_command(cmd, "Smoke Tests")

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n" + "="*80)
    print("FACEAUTH TEST REPORT")
    print("="*80)
    
    results = {}
    
    # Run different test suites
    test_suites = [
        ("Smoke Tests", run_smoke_tests),
        ("Basic Tests", run_basic_tests),
        ("Core Tests", run_core_tests),
        ("Security Tests", run_security_tests),
        ("CLI Tests", run_cli_tests),
        ("Integration Tests", run_integration_tests)
    ]
    
    for suite_name, test_func in test_suites:
        results[suite_name] = test_func()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_suites = len(results)
    passed_suites = sum(1 for result in results.values() if result)
    
    for suite_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{suite_name:.<40} {status}")
    
    print(f"\nOverall: {passed_suites}/{total_suites} test suites passed")
    
    if passed_suites == total_suites:
        print("🎉 All test suites passed!")
        return True
    else:
        print("⚠️  Some test suites failed. Please review the output above.")
        return False

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="FaceAuth Test Runner")
    parser.add_argument("command", choices=[
        "smoke", "quick", "basic", "core", "security", "integration", 
        "performance", "cli", "all", "coverage", "install-deps", "report"
    ], help="Test command to run")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    print(f"FaceAuth Test Runner")
    print(f"Working directory: {project_root}")
    
    command_map = {
        "smoke": run_smoke_tests,
        "quick": run_quick_tests,
        "basic": run_basic_tests,
        "core": run_core_tests,
        "security": run_security_tests,
        "integration": run_integration_tests,
        "performance": run_performance_tests,
        "cli": run_cli_tests,
        "all": run_all_tests,
        "coverage": run_with_coverage,
        "install-deps": install_test_dependencies,
        "report": generate_test_report
    }
    
    start_time = time.time()
    success = command_map[args.command]()
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"Test execution completed in {total_time:.2f}s")
    
    if success:
        print("✅ Tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
