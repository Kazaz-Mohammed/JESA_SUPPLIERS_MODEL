#!/usr/bin/env python3
"""
Test Runner for JESA Tender Evaluation System
Runs all test suites: comprehensive, performance, and stress tests
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def run_test_suite(test_file, test_name):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        execution_time = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Return results
        return {
            'success': result.returncode == 0,
            'execution_time': execution_time,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'success': False,
            'execution_time': execution_time,
            'return_code': -1,
            'stdout': '',
            'stderr': str(e)
        }


def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking Dependencies...")
    
    required_modules = [
        'unittest',
        'tempfile',
        'json',
        'pandas',
        'openpyxl'
    ]
    
    optional_modules = [
        'psutil',
        'concurrent.futures',
        'threading'
    ]
    
    missing_required = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_required.append(module)
            print(f"   ❌ {module} (REQUIRED)")
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_optional.append(module)
            print(f"   ⚠️ {module} (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_required)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional dependencies: {', '.join(missing_optional)}")
        print("Some tests may be skipped or run with reduced functionality.")
    
    return True


def main():
    """Main test runner"""
    print("🚀 JESA Tender Evaluation System - Test Runner")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Define test suites
    test_suites = [
        {
            'file': 'test_comprehensive.py',
            'name': 'Comprehensive Test Suite',
            'description': 'Unit tests for all components, edge cases, and error handling'
        },
        {
            'file': 'test_performance.py',
            'name': 'Performance Test Suite',
            'description': 'Performance tests with large datasets and stress conditions'
        },
        {
            'file': 'test_stress.py',
            'name': 'Stress Test Suite',
            'description': 'Stress tests with extreme conditions and error scenarios'
        }
    ]
    
    # Run all test suites
    results = []
    total_start_time = time.time()
    
    for suite in test_suites:
        if os.path.exists(suite['file']):
            result = run_test_suite(suite['file'], suite['name'])
            result['name'] = suite['name']
            result['description'] = suite['description']
            results.append(result)
        else:
            print(f"\n⚠️ Test file not found: {suite['file']}")
            results.append({
                'name': suite['name'],
                'success': False,
                'execution_time': 0,
                'return_code': -1,
                'stdout': '',
                'stderr': f"File not found: {suite['file']}"
            })
    
    total_execution_time = time.time() - total_start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    successful_tests = 0
    total_tests = len(results)
    
    for result in results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{status} {result['name']}")
        print(f"   Time: {result['execution_time']:.2f}s")
        print(f"   Description: {result['description']}")
        
        if not result['success']:
            print(f"   Return code: {result['return_code']}")
            if result['stderr']:
                print(f"   Error: {result['stderr'][:100]}...")
        
        print()
        
        if result['success']:
            successful_tests += 1
    
    # Overall summary
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{'='*60}")
    print(f"📈 OVERALL RESULTS:")
    print(f"   Total test suites: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {total_tests - successful_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total execution time: {total_execution_time:.2f}s")
    print(f"{'='*60}")
    
    # Recommendations
    if successful_tests == total_tests:
        print("🎉 All tests passed! The system is ready for production.")
    elif successful_tests > 0:
        print("⚠️ Some tests failed. Review the errors above and fix issues before deployment.")
    else:
        print("❌ All tests failed. The system needs significant fixes before it can be used.")
    
    # Exit with appropriate code
    sys.exit(0 if successful_tests == total_tests else 1)


if __name__ == "__main__":
    main()
