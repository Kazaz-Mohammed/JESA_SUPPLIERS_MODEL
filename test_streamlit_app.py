#!/usr/bin/env python3
"""
Test script for the Streamlit application
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from utils.analyzer import ProposalAnalyzer
        print("✓ ProposalAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ ProposalAnalyzer import failed: {e}")
        return False
    
    try:
        from utils.scorer import ProposalScorer, ResultsExporter
        print("✓ ProposalScorer and ResultsExporter imported successfully")
    except ImportError as e:
        print(f"❌ Scorer imports failed: {e}")
        return False
    
    try:
        from utils.pdf_processor import PDFProcessor
        print("✓ PDFProcessor imported successfully")
    except ImportError as e:
        print(f"❌ PDFProcessor import failed: {e}")
        return False
    
    return True

def test_app_file():
    """Test if the main app file exists and is valid."""
    print("\nTesting app file...")
    
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py file not found")
        return False
    
    print("✓ app.py file exists")
    
    # Try to compile the app file
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, app_file, 'exec')
        print("✓ app.py compiles successfully")
    except SyntaxError as e:
        print(f"❌ app.py has syntax errors: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False
    
    return True

def test_sample_data():
    """Test if sample data files exist."""
    print("\nTesting sample data...")
    
    sample_files = [
        "data/sample_tender.txt",
        "data/sample_proposal_1.txt",
        "data/sample_proposal_2.txt"
    ]
    
    for file_path in sample_files:
        if not Path(file_path).exists():
            print(f"❌ Sample file not found: {file_path}")
            return False
        print(f"✓ {file_path} exists")
    
    return True

def main():
    """Run all tests."""
    print("JESA Tender Evaluation System - Streamlit App Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_app_file,
        test_sample_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Streamlit app is ready to run.")
        print("\nTo run the app:")
        print("  streamlit run app.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the app.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
