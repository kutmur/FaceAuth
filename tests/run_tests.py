#!/usr/bin/env python3
"""
Master test runner for FaceAuth comprehensive testing suite.
This script orchestrates all test categories and provides detailed reporting.
"""

import sys
import os
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json


class FaceAuthTestRunner:
    """Comprehensive test runner for FaceAuth platform."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.results = {}
        
    def run_test_category(self, category: str, test_files: List[str], 
                         extra_args: List[str] = None) -> Dict[str, Any]:
        """Run a category of tests and return results."""
        print(f"\n{'='*60}")
        print(f"Running {category.upper()} Tests")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test files
        for test_file in test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
        
        # Add extra arguments
        if extra_args:
            cmd.extend(extra_args)
        
        # Add basic options
        cmd.extend(["-v", "--tb=short"])
        
        # Run tests
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            output_lines = result.stdout.split('\n')
            passed = failed = skipped = 0
            
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Parse summary line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                        elif part == "failed":
                            failed = int(parts[i-1])
                        elif part == "skipped":
                            skipped = int(parts[i-1])
                elif line.endswith(" passed"):
                    passed = int(line.split()[0])
                elif "FAILED" in line:
                    failed += 1
            
            return {
                "category": category,
                "duration": duration,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "category": category,
                "duration": 600,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timeout after 10 minutes"
            }
        except Exception as e:
            return {
                "category": category,
                "duration": time.time() - start_time,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests for basic functionality verification."""
        return self.run_test_category(
            "Smoke",
            ["test_smoke.py"],
            ["--maxfail=1"]
        )
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for individual components."""
        return self.run_test_category(
            "Unit",
            [
                "test_enrollment.py",
                "test_authentication.py", 
                "test_encryption.py",
                "test_security.py"
            ],
            ["-m", "not integration and not performance"]
        )
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for system workflows."""
        return self.run_test_category(
            "Integration",
            [
                "test_integration.py",
                "test_cli.py",
                "test_file_encryption.py"
            ],
            ["-m", "integration", "--maxfail=3"]
        )
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and benchmarking tests."""
        return self.run_test_category(
            "Performance",
            ["test_performance.py"],
            ["-m", "performance", "-s", "--maxfail=2"]
        )
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run tests with coverage analysis."""
        print(f"\n{'='*60}")
        print("Running Coverage Analysis")
        print(f"{'='*60}")
        
        # Check if pytest-cov is available
        try:
            import pytest_cov
            has_coverage = True
        except ImportError:
            has_coverage = False
            print("Warning: pytest-cov not available. Skipping coverage analysis.")
            return {"category": "Coverage", "available": False}
        
        if not has_coverage:
            return {"category": "Coverage", "available": False}
        
        return self.run_test_category(
            "Coverage",
            [
                "test_smoke.py",
                "test_enrollment.py",
                "test_authentication.py",
                "test_encryption.py"
            ],
            [
                "--cov=faceauth",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=70"
            ]
        )
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        total_passed = sum(r.get("passed", 0) for r in self.results.values())
        total_failed = sum(r.get("failed", 0) for r in self.results.values())
        total_skipped = sum(r.get("skipped", 0) for r in self.results.values())
        total_duration = sum(r.get("duration", 0) for r in self.results.values())
        
        report = f"""
FaceAuth Test Suite Results
{'='*50}

Overall Summary:
  Total Tests: {total_passed + total_failed + total_skipped}
  Passed: {total_passed}
  Failed: {total_failed}
  Skipped: {total_skipped}
  Total Duration: {total_duration:.2f}s

Category Results:
"""
        
        for category, result in self.results.items():
            if result.get("available", True):
                status = "PASS" if result["return_code"] == 0 else "FAIL"
                report += f"""
  {category}:
    Status: {status}
    Passed: {result['passed']}
    Failed: {result['failed']}
    Skipped: {result['skipped']}
    Duration: {result['duration']:.2f}s
"""
            else:
                report += f"""
  {category}:
    Status: SKIPPED (dependencies not available)
"""
        
        # Add failure details
        failed_categories = [k for k, v in self.results.items() 
                           if v.get("return_code", 0) != 0 and v.get("available", True)]
        
        if failed_categories:
            report += f"""
Failed Categories:
{'='*20}
"""
            for category in failed_categories:
                result = self.results[category]
                report += f"""
{category} Failures:
{result['stderr'][:500]}...
"""
        
        # Add recommendations
        report += f"""
Recommendations:
{'='*15}
"""
        
        if total_failed == 0:
            report += "✅ All tests passed! System is ready for production.\n"
        else:
            report += f"❌ {total_failed} tests failed. Review failures before deployment.\n"
        
        if total_skipped > 0:
            report += f"⚠️  {total_skipped} tests skipped. Check dependencies.\n"
        
        if total_duration > 300:  # 5 minutes
            report += "⏱️  Tests took longer than expected. Consider optimization.\n"
        
        return report
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        results_file = self.project_root / filename
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"Results saved to: {results_file}")
    
    def run_all_tests(self, include_performance: bool = True, 
                     include_coverage: bool = True):
        """Run all test categories."""
        print("Starting FaceAuth Comprehensive Test Suite")
        print("="*60)
        
        # Run test categories in order
        self.results["smoke"] = self.run_smoke_tests()
        
        # Only continue if smoke tests pass
        if self.results["smoke"]["return_code"] == 0:
            self.results["unit"] = self.run_unit_tests()
            self.results["integration"] = self.run_integration_tests()
            
            if include_performance:
                self.results["performance"] = self.run_performance_tests()
            
            if include_coverage:
                self.results["coverage"] = self.run_coverage_analysis()
        else:
            print("❌ Smoke tests failed. Skipping remaining tests.")
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save results
        self.save_results()
        
        # Return overall success
        return all(r.get("return_code", 0) == 0 or not r.get("available", True) 
                  for r in self.results.values())


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="FaceAuth Test Suite Runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only smoke and unit tests")
    parser.add_argument("--performance", action="store_true",
                       help="Include performance tests")
    parser.add_argument("--no-coverage", action="store_true",
                       help="Skip coverage analysis")
    parser.add_argument("--category", choices=["smoke", "unit", "integration", "performance"],
                       help="Run only specific test category")
    
    args = parser.parse_args()
    
    runner = FaceAuthTestRunner()
    
    if args.category:
        # Run specific category
        if args.category == "smoke":
            result = runner.run_smoke_tests()
        elif args.category == "unit":
            result = runner.run_unit_tests()
        elif args.category == "integration":
            result = runner.run_integration_tests()
        elif args.category == "performance":
            result = runner.run_performance_tests()
        
        runner.results[args.category] = result
        print(runner.generate_report())
        success = result["return_code"] == 0
    
    elif args.quick:
        # Quick testing
        runner.results["smoke"] = runner.run_smoke_tests()
        if runner.results["smoke"]["return_code"] == 0:
            runner.results["unit"] = runner.run_unit_tests()
        
        print(runner.generate_report())
        success = all(r["return_code"] == 0 for r in runner.results.values())
    
    else:
        # Full test suite
        include_performance = args.performance or not args.quick
        include_coverage = not args.no_coverage
        
        success = runner.run_all_tests(
            include_performance=include_performance,
            include_coverage=include_coverage
        )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
