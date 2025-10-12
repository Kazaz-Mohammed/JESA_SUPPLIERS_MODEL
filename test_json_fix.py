#!/usr/bin/env python3
"""
Test the JSON parsing fix
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.analyzer import ProposalAnalyzer

# Load environment variables
load_dotenv()

def test_json_parsing_fix():
    """Test the improved JSON parsing."""
    
    print("Testing JSON Parsing Fix")
    print("=" * 40)
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize analyzer
        print("1. Initializing analyzer...")
        analyzer = ProposalAnalyzer(api_key=api_key)
        print("✓ Analyzer initialized")
        
        # Load sample data
        print("\n2. Loading sample data...")
        with open("data/sample_tender.txt", "r", encoding="utf-8") as f:
            tender_requirements = f.read()
        
        with open("data/sample_proposal_1.txt", "r", encoding="utf-8") as f:
            proposal_text = f.read()
        
        print(f"✓ Tender requirements: {len(tender_requirements)} characters")
        print(f"✓ Sample proposal: {len(proposal_text)} characters")
        
        # Test analysis
        print("\n3. Testing analysis with improved JSON parsing...")
        print("   This may take 30-60 seconds...")
        
        result = analyzer.analyze_proposal(
            proposal_text=proposal_text,
            tender_requirements=tender_requirements,
            supplier_name="Test Supplier"
        )
        
        print(f"\n4. Analysis Results:")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Final Score: {result.get('final_score', 'N/A')}")
        
        if result.get('status') == 'success':
            print("✅ JSON parsing fix successful!")
            print(f"   Supplier: {result.get('supplier_name', 'Unknown')}")
            print(f"   Final Score: {result.get('final_score', 'N/A')}")
            
            # Show criteria scores
            criteria_scores = result.get('criteria_scores', {})
            print("\n   Criteria Scores:")
            for criterion, data in criteria_scores.items():
                if isinstance(data, dict):
                    score = data.get('score', 0)
                    print(f"   - {criterion.replace('_', ' ').title()}: {score}")
            
            return True
        else:
            print(f"❌ Analysis still failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_json_parsing_fix()
    if success:
        print("\n🎉 JSON parsing fix is working! You can now use the Streamlit app.")
    else:
        print("\n❌ JSON parsing fix needs more work.")
