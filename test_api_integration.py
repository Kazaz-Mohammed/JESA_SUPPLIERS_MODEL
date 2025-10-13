#!/usr/bin/env python3
"""
Test API integration using environment variables
"""

import os
from utils.analyzer import ProposalAnalyzer
from utils.scorer import ProposalScorer

def test_api_integration():
    """Test the system with API key from environment variable."""
    
    print("Testing JESA Tender Evaluation System with API Integration")
    print("=" * 60)
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your API key: set OPENAI_API_KEY=your_key_here")
        return False
    
    try:
        # Initialize analyzer with API key from environment
        print("1. Initializing ProposalAnalyzer...")
        analyzer = ProposalAnalyzer(api_key=api_key)
        print("✓ Analyzer initialized successfully")
        
        # Load sample data
        print("\n2. Loading sample data...")
        with open("data/sample_tender.txt", "r", encoding="utf-8") as f:
            tender_requirements = f.read()
        
        with open("data/sample_proposal_1.txt", "r", encoding="utf-8") as f:
            proposal_text = f.read()
        
        print(f"✓ Tender requirements loaded: {len(tender_requirements)} characters")
        print(f"✓ Sample proposal loaded: {len(proposal_text)} characters")
        
        # Test API call with real proposal
        print("\n3. Making OpenAI API call...")
        print("   This may take 30-60 seconds...")
        
        result = analyzer.analyze_proposal(
            proposal_text=proposal_text,
            tender_requirements=tender_requirements,
            supplier_name="ABC Construction"
        )
        
        print(f"✓ Analysis completed!")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Final Score: {result.get('final_score', 'N/A')}")
        
        if result.get('status') == 'success':
            print("\n4. Testing scoring system...")
            scorer = ProposalScorer()
            
            # Calculate weighted score
            weighted_score = scorer.calculate_weighted_score(result)
            print(f"✓ Weighted score calculated: {weighted_score}")
            
            # Test ranking
            ranked_suppliers = scorer.rank_suppliers([result])
            print(f"✓ Supplier ranked: #{ranked_suppliers[0].get('rank', 'N/A')}")
            
            print("\n🎉 API integration test successful! System is working correctly.")
            return True
            
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_integration()
    if success:
        print("\n✅ System is ready for production use!")
    else:
        print("\n❌ System needs configuration before use.")

