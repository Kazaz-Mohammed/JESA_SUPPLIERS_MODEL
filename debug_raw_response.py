#!/usr/bin/env python3
"""
Debug script to capture raw OpenAI API response
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.analyzer import ProposalAnalyzer

# Load environment variables
load_dotenv()

def debug_raw_response():
    """Debug the raw API response to see what's causing the parsing issue."""
    
    print("Debug: Capturing Raw OpenAI API Response")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your API key in the Streamlit interface or as an environment variable")
        return
    
    try:
        # Initialize analyzer
        analyzer = ProposalAnalyzer(api_key=api_key)
        
        # Load sample data
        with open("data/sample_tender.txt", "r", encoding="utf-8") as f:
            tender_requirements = f.read()
        
        with open("data/sample_proposal_1.txt", "r", encoding="utf-8") as f:
            proposal_text = f.read()
        
        print(f"✓ Loaded tender requirements: {len(tender_requirements)} characters")
        print(f"✓ Loaded sample proposal: {len(proposal_text)} characters")
        
        # Prepare the prompt
        prompt = analyzer.prompt_template.format(
            tender_requirements=tender_requirements,
            supplier_proposal=proposal_text
        )
        
        print(f"\n📝 Prompt length: {len(prompt)} characters")
        print(f"📝 Prompt preview (first 200 chars):")
        print(prompt[:200] + "...")
        
        # Make API call and capture raw response
        print(f"\n🤖 Making API call...")
        raw_response = analyzer._make_api_call(prompt)
        
        print(f"\n📥 RAW API RESPONSE:")
        print("=" * 50)
        print(repr(raw_response))  # This shows the exact characters including newlines
        print("=" * 50)
        
        print(f"\n📥 RAW API RESPONSE (as displayed):")
        print("-" * 50)
        print(raw_response)
        print("-" * 50)
        
        # Try to parse it
        print(f"\n🔍 Attempting to parse JSON...")
        try:
            parsed = analyzer._parse_json_response(raw_response)
            print("✅ JSON parsing successful!")
            print(f"Parsed result keys: {list(parsed.keys())}")
        except Exception as parse_error:
            print(f"❌ JSON parsing failed: {parse_error}")
            
            # Try manual extraction
            print(f"\n🔧 Attempting manual JSON extraction...")
            response = raw_response.strip()
            
            # Remove markdown code blocks
            if response.startswith('```json'):
                response = response[7:]
            elif response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            print(f"Cleaned response: {repr(response[:100])}")
            
            # Find first { and last }
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_content = response[start_idx:end_idx]
                print(f"Extracted JSON content: {repr(json_content[:100])}")
                
                try:
                    parsed = json.loads(json_content)
                    print("✅ Manual extraction successful!")
                    print(f"Parsed result: {json.dumps(parsed, indent=2)[:200]}...")
                except Exception as manual_error:
                    print(f"❌ Manual extraction also failed: {manual_error}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_raw_response()
