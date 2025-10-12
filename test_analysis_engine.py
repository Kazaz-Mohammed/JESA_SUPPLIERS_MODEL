#!/usr/bin/env python3
"""
Test script for the AI Analysis Engine (Phase 2)

This script tests the complete analysis pipeline without requiring
actual API calls, using mock data to validate the system architecture.
"""

import sys
import os
import json
from pathlib import Path

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from analyzer import ProposalAnalyzer
from scorer import ProposalScorer, ResultsExporter


def create_mock_analysis_result(supplier_name: str, base_score: int = 70) -> dict:
    """Create a mock analysis result for testing."""
    return {
        'supplier_name': supplier_name,
        'criteria_scores': {
            'technical_compliance': {
                'score': base_score + 5,
                'justification': f'{supplier_name} meets most technical requirements with minor gaps.',
                'evidence': ['ISO certification mentioned', 'Technical specifications provided']
            },
            'price_competitiveness': {
                'score': base_score - 10,
                'justification': f'{supplier_name} pricing is competitive but could be lower.',
                'evidence': ['Detailed cost breakdown provided', 'Market rate comparison included']
            },
            'company_experience': {
                'score': base_score + 15,
                'justification': f'{supplier_name} has strong relevant experience.',
                'evidence': ['5+ similar projects completed', 'Client references provided']
            },
            'timeline_feasibility': {
                'score': base_score,
                'justification': f'{supplier_name} timeline appears realistic.',
                'evidence': ['Detailed project schedule provided', 'Risk mitigation plans included']
            },
            'risk_assessment': {
                'score': base_score + 8,
                'justification': f'{supplier_name} presents low to moderate risk.',
                'evidence': ['Adequate insurance coverage', 'Financial stability demonstrated']
            }
        },
        'final_score': base_score + 3.6,  # Will be recalculated
        'overall_summary': f'{supplier_name} presents a solid proposal with good technical compliance and experience, but pricing could be more competitive.',
        'red_flags': ['Minor documentation gaps', 'Pricing slightly above market'],
        'recommendations': f'Consider {supplier_name} for the project, but negotiate pricing.',
        'key_strengths': ['Strong technical expertise', 'Good project experience'],
        'areas_for_improvement': ['Pricing competitiveness', 'Documentation completeness'],
        'analysis_timestamp': '2024-03-15 10:30:00',
        'model_used': 'gpt-4-turbo-preview',
        'status': 'success'
    }


def test_analyzer_initialization():
    """Test analyzer initialization without API key."""
    print("Testing Analyzer Initialization...")
    
    try:
        # This should fail without API key
        analyzer = ProposalAnalyzer()
        print("✗ Analyzer initialization should have failed without API key")
        return False
    except ValueError as e:
        if "API key is required" in str(e):
            print("✓ Analyzer correctly requires API key")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
        return False


def test_scorer_functionality():
    """Test the scoring and ranking functionality."""
    print("\nTesting Scorer Functionality...")
    
    try:
        scorer = ProposalScorer()
        
        # Test weight validation
        valid_weights = {
            'technical_compliance': 30,
            'price_competitiveness': 25,
            'company_experience': 20,
            'timeline_feasibility': 15,
            'risk_assessment': 10
        }
        
        is_valid, error_msg = scorer.validate_weights(valid_weights)
        if is_valid:
            print("✓ Weight validation works correctly")
        else:
            print(f"✗ Weight validation failed: {error_msg}")
            return False
        
        # Test invalid weights
        invalid_weights = {
            'technical_compliance': 30,
            'price_competitiveness': 25,
            'company_experience': 20,
            'timeline_feasibility': 15,
            'risk_assessment': 5  # Total = 95, not 100
        }
        
        is_valid, error_msg = scorer.validate_weights(invalid_weights)
        if not is_valid and "must sum to 100%" in error_msg:
            print("✓ Invalid weight detection works correctly")
        else:
            print(f"✗ Invalid weight detection failed: {error_msg}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Scorer test failed: {e}")
        return False


def test_scoring_calculations():
    """Test weighted score calculations."""
    print("\nTesting Scoring Calculations...")
    
    try:
        scorer = ProposalScorer()
        
        # Create mock analysis
        mock_analysis = create_mock_analysis_result("Test Supplier", 75)
        
        # Test weighted score calculation
        weighted_score = scorer.calculate_weighted_score(mock_analysis)
        
        # Expected calculation: (80*0.30 + 65*0.25 + 90*0.20 + 75*0.15 + 83*0.10) = 77.55
        expected_score = 77.55
        
        if abs(weighted_score - expected_score) < 0.1:
            print(f"✓ Weighted score calculation correct: {weighted_score:.2f}")
        else:
            print(f"✗ Weighted score calculation incorrect: {weighted_score:.2f} (expected {expected_score:.2f})")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Scoring calculation test failed: {e}")
        return False


def test_supplier_ranking():
    """Test supplier ranking functionality."""
    print("\nTesting Supplier Ranking...")
    
    try:
        scorer = ProposalScorer()
        
        # Create multiple mock analyses
        analyses = [
            create_mock_analysis_result("Supplier A", 70),
            create_mock_analysis_result("Supplier B", 80),
            create_mock_analysis_result("Supplier C", 65)
        ]
        
        # Rank suppliers
        ranked_suppliers = scorer.rank_suppliers(analyses)
        
        if len(ranked_suppliers) == 3:
            print(f"✓ Correct number of ranked suppliers: {len(ranked_suppliers)}")
        else:
            print(f"✗ Incorrect number of ranked suppliers: {len(ranked_suppliers)}")
            return False
        
        # Check ranking order (should be highest score first)
        if (ranked_suppliers[0]['weighted_score'] >= 
            ranked_suppliers[1]['weighted_score'] >= 
            ranked_suppliers[2]['weighted_score']):
            print("✓ Suppliers ranked correctly by score")
        else:
            print("✗ Suppliers not ranked correctly by score")
            return False
        
        # Check rank assignment
        for i, supplier in enumerate(ranked_suppliers):
            if supplier['rank'] == i + 1:
                continue
            else:
                print(f"✗ Incorrect rank assignment for supplier {i+1}")
                return False
        
        print("✓ Rank assignment correct")
        return True
        
    except Exception as e:
        print(f"✗ Supplier ranking test failed: {e}")
        return False


def test_summary_statistics():
    """Test summary statistics generation."""
    print("\nTesting Summary Statistics...")
    
    try:
        scorer = ProposalScorer()
        
        # Create mock analyses
        analyses = [
            create_mock_analysis_result("Supplier A", 70),
            create_mock_analysis_result("Supplier B", 80),
            create_mock_analysis_result("Supplier C", 65)
        ]
        
        ranked_suppliers = scorer.rank_suppliers(analyses)
        stats = scorer.generate_summary_statistics(ranked_suppliers)
        
        required_fields = ['total_suppliers', 'average_score', 'highest_score', 'lowest_score', 'top_supplier']
        
        for field in required_fields:
            if field in stats:
                print(f"✓ {field} included in statistics")
            else:
                print(f"✗ {field} missing from statistics")
                return False
        
        if stats['total_suppliers'] == 3:
            print("✓ Correct supplier count in statistics")
        else:
            print(f"✗ Incorrect supplier count: {stats['total_suppliers']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Summary statistics test failed: {e}")
        return False


def test_export_functionality():
    """Test export functionality (without actually creating files)."""
    print("\nTesting Export Functionality...")
    
    try:
        exporter = ResultsExporter()
        scorer = ProposalScorer()
        
        # Create test data
        analyses = [
            create_mock_analysis_result("Supplier A", 70),
            create_mock_analysis_result("Supplier B", 80)
        ]
        
        ranked_suppliers = scorer.rank_suppliers(analyses)
        stats = scorer.generate_summary_statistics(ranked_suppliers)
        weights = {
            'technical_compliance': 30,
            'price_competitiveness': 25,
            'company_experience': 20,
            'timeline_feasibility': 15,
            'risk_assessment': 10
        }
        
        # Test Excel export (this will create a file)
        try:
            excel_file = exporter.export_to_excel(ranked_suppliers, stats, weights, "test_results.xlsx")
            if os.path.exists(excel_file):
                print(f"✓ Excel export successful: {excel_file}")
                # Clean up test file
                os.remove(excel_file)
            else:
                print(f"✗ Excel export failed: file not created")
                return False
        except Exception as e:
            print(f"✗ Excel export failed: {e}")
            return False
        
        # Test JSON export
        try:
            json_file = exporter.export_to_json(ranked_suppliers, stats, weights, "test_results.json")
            if os.path.exists(json_file):
                print(f"✓ JSON export successful: {json_file}")
                # Clean up test file
                os.remove(json_file)
            else:
                print(f"✗ JSON export failed: file not created")
                return False
        except Exception as e:
            print(f"✗ JSON export failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Export functionality test failed: {e}")
        return False


def test_sample_data_processing():
    """Test processing of sample data files."""
    print("\nTesting Sample Data Processing...")
    
    try:
        # Check if sample files exist
        sample_files = [
            "data/sample_tender.txt",
            "data/sample_proposal_1.txt", 
            "data/sample_proposal_2.txt"
        ]
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                print(f"✓ Sample file exists: {file_path}")
                
                # Test file reading
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) > 100:
                    print(f"✓ File content loaded: {len(content)} characters")
                else:
                    print(f"✗ File content too short: {len(content)} characters")
                    return False
            else:
                print(f"✗ Sample file missing: {file_path}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Sample data processing test failed: {e}")
        return False


def main():
    """Run all tests for the analysis engine."""
    print("JESA Tender Evaluation System - Phase 2 Testing")
    print("=" * 60)
    
    tests = [
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Scorer Functionality", test_scorer_functionality),
        ("Scoring Calculations", test_scoring_calculations),
        ("Supplier Ranking", test_supplier_ranking),
        ("Summary Statistics", test_summary_statistics),
        ("Export Functionality", test_export_functionality),
        ("Sample Data Processing", test_sample_data_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 2 components are working correctly.")
        print("\nNext steps:")
        print("1. Set up OpenAI API key for actual analysis testing")
        print("2. Proceed to Phase 3: Streamlit Web Interface")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
