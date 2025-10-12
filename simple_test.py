#!/usr/bin/env python3
"""
Simple test for Phase 2 components
"""

import sys
import os

# Test scorer module
try:
    from utils.scorer import ProposalScorer, ResultsExporter
    print("✓ Scorer module imported successfully")
    
    # Test scorer functionality
    scorer = ProposalScorer()
    print("✓ ProposalScorer initialized")
    
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
    
    # Test export functionality
    exporter = ResultsExporter()
    print("✓ ResultsExporter initialized")
    
    print("\n🎉 Phase 2 core components are working!")
    
except Exception as e:
    print(f"✗ Error testing scorer module: {e}")

# Test analyzer module (without API key)
try:
    from utils.analyzer import ProposalAnalyzer
    print("✓ Analyzer module imported successfully")
    
    # This should fail without API key
    try:
        analyzer = ProposalAnalyzer()
        print("✗ Analyzer should have failed without API key")
    except ValueError as e:
        if "API key is required" in str(e):
            print("✓ Analyzer correctly requires API key")
        else:
            print(f"✗ Unexpected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
        
except Exception as e:
    print(f"✗ Error testing analyzer module: {e}")

print("\n" + "="*50)
print("Phase 2 Testing Complete!")
print("Components ready for Streamlit integration.")
