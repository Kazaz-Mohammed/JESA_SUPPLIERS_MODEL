#!/usr/bin/env python3
"""
Test script to verify app components work correctly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from utils.analyzer import ProposalAnalyzer
        print("   ✅ ProposalAnalyzer imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import ProposalAnalyzer: {e}")
        return False
    
    try:
        from utils.scorer import ProposalScorer, ResultsExporter
        print("   ✅ ProposalScorer and ResultsExporter imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import scorer modules: {e}")
        return False
    
    try:
        from utils.pdf_processor import PDFProcessor
        print("   ✅ PDFProcessor imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import PDFProcessor: {e}")
        return False
    
    try:
        import streamlit as st
        print("   ✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import Streamlit: {e}")
        return False
    
    return True


def test_pdf_processing():
    """Test PDF processing with sample data"""
    print("\n📄 Testing PDF processing...")
    
    try:
        from utils.pdf_processor import extract_text_from_file
        
        # Test with sample text file
        sample_text = "This is a test tender document with requirements."
        sample_bytes = sample_text.encode('utf-8')
        
        result = extract_text_from_file(sample_bytes, "test.txt")
        
        if result == sample_text:
            print("   ✅ PDF processing works correctly")
            return True
        else:
            print(f"   ❌ PDF processing failed. Expected: '{sample_text}', Got: '{result}'")
            return False
            
    except Exception as e:
        print(f"   ❌ PDF processing failed with error: {e}")
        return False


def test_scoring_system():
    """Test scoring system with sample data"""
    print("\n📊 Testing scoring system...")
    
    try:
        from utils.scorer import calculate_weighted_score
        
        # Sample analysis
        sample_analysis = {
            "supplier_name": "Test Supplier",
            "criteria_scores": {
                "technical_compliance": {"score": 85},
                "price_competitiveness": {"score": 75},
                "company_experience": {"score": 90},
                "timeline_feasibility": {"score": 80},
                "risk_assessment": {"score": 85}
            }
        }
        
        # Sample weights
        weights = {
            "technical_compliance": 30,
            "price_competitiveness": 25,
            "company_experience": 20,
            "timeline_feasibility": 15,
            "risk_assessment": 10
        }
        
        score = calculate_weighted_score(sample_analysis, weights)
        expected_score = 82.75  # (85*0.3 + 75*0.25 + 90*0.2 + 80*0.15 + 85*0.1)
        
        if abs(score - expected_score) < 0.01:
            print(f"   ✅ Scoring system works correctly. Score: {score}")
            return True
        else:
            print(f"   ❌ Scoring system failed. Expected: {expected_score}, Got: {score}")
            return False
            
    except Exception as e:
        print(f"   ❌ Scoring system failed with error: {e}")
        return False


def test_sample_data():
    """Test with sample data files"""
    print("\n📁 Testing sample data...")
    
    sample_files = [
        "data/sample_tender.txt",
        "data/sample_proposal_1.txt", 
        "data/sample_proposal_2.txt"
    ]
    
    all_exist = True
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} exists")
            # Test reading the file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"      Content length: {len(content)} characters")
            except Exception as e:
                print(f"      ❌ Error reading file: {e}")
                all_exist = False
        else:
            print(f"   ❌ {file_path} not found")
            all_exist = False
    
    return all_exist


def test_analyzer_without_api():
    """Test analyzer initialization without API key"""
    print("\n🤖 Testing analyzer initialization...")
    
    try:
        from utils.analyzer import ProposalAnalyzer
        
        # This should fail without API key, which is expected
        try:
            analyzer = ProposalAnalyzer()
            print("   ⚠️ Analyzer initialized without API key (unexpected)")
            return False
        except ValueError as e:
            if "API key is required" in str(e):
                print("   ✅ Analyzer correctly requires API key")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"   ❌ Analyzer test failed: {e}")
        return False


def test_app_file_structure():
    """Test that app.py can be read and has expected structure"""
    print("\n📱 Testing app file structure...")
    
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            "streamlit",
            "ProposalAnalyzer",
            "ProposalScorer", 
            "ResultsExporter",
            "PDFProcessor",
            "st.set_page_config",
            "st.title"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if not missing_components:
            print("   ✅ App file has all required components")
            return True
        else:
            print(f"   ❌ Missing components: {missing_components}")
            return False
            
    except Exception as e:
        print(f"   ❌ App file test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 JESA Tender Evaluation System - Component Testing")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("PDF Processing Test", test_pdf_processing),
        ("Scoring System Test", test_scoring_system),
        ("Sample Data Test", test_sample_data),
        ("Analyzer Test", test_analyzer_without_api),
        ("App Structure Test", test_app_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All components working correctly! App should run successfully.")
        print("\nTo start the app, run: streamlit run app.py")
        print("Then open: http://localhost:8501")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before running the app.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
