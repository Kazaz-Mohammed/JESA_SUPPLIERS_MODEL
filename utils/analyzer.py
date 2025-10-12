"""
AI Analysis Engine for JESA Tender Evaluation System

This module handles the core analysis logic using OpenAI API
to evaluate supplier proposals against tender requirements.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProposalAnalyzer:
    """
    Main class for analyzing supplier proposals using OpenAI API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the analyzer with OpenAI API configuration.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, will try to load from environment.
            model (str): OpenAI model to use for analysis.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
        
        logger.info(f"ProposalAnalyzer initialized with model: {self.model}")
    
    def _load_prompt_template(self) -> str:
        """Load the evaluation prompt template."""
        try:
            prompt_path = Path(__file__).parent.parent / "prompts" / "evaluation_prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error("Prompt template not found. Using default template.")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Fallback default prompt template."""
        return """
        You are an expert tender evaluation specialist. Analyze the supplier proposal against the tender requirements and provide scores (0-100) for each criterion:
        
        1. Technical Compliance (0-100)
        2. Price Competitiveness (0-100) 
        3. Company Experience (0-100)
        4. Timeline Feasibility (0-100)
        5. Risk Assessment (0-100)
        
        Provide your analysis in JSON format with scores, justifications, and evidence.
        
        Tender Requirements:
        {tender_requirements}
        
        Supplier Proposal:
        {supplier_proposal}
        """
    
    def analyze_proposal(self, proposal_text: str, tender_requirements: str, supplier_name: str = "Unknown") -> Dict[str, Any]:
        """
        Analyze a single supplier proposal against tender requirements.
        
        Args:
            proposal_text (str): The supplier proposal text
            tender_requirements (str): The tender requirements text
            supplier_name (str): Name of the supplier (for logging)
            
        Returns:
            Dict[str, Any]: Analysis results with scores and justifications
        """
        logger.info(f"Starting analysis for supplier: {supplier_name}")
        
        try:
            # Prepare the prompt
            prompt = self.prompt_template.format(
                tender_requirements=tender_requirements,
                supplier_proposal=proposal_text
            )
            
            # Make API call
            response = self._make_api_call(prompt)
            
            # Parse response
            analysis_result = self._parse_json_response(response)
            
            # Add metadata
            analysis_result['supplier_name'] = supplier_name
            analysis_result['analysis_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            analysis_result['model_used'] = self.model
            analysis_result['status'] = 'success'
            
            logger.info(f"Analysis completed for {supplier_name}. Final score: {analysis_result.get('final_score', 'N/A')}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {supplier_name}: {e}")
            return {
                'supplier_name': supplier_name,
                'criteria_scores': {
                    "technical_compliance": {"score": 0, "justification": "Analysis failed", "evidence": []},
                    "price_competitiveness": {"score": 0, "justification": "Analysis failed", "evidence": []},
                    "company_experience": {"score": 0, "justification": "Analysis failed", "evidence": []},
                    "timeline_feasibility": {"score": 0, "justification": "Analysis failed", "evidence": []},
                    "risk_assessment": {"score": 0, "justification": "Analysis failed", "evidence": []}
                },
                'final_score': 0.0,
                'overall_summary': f"Analysis failed: {str(e)}",
                'red_flags': ["Analysis system error"],
                'recommendations': "Manual review required due to system error",
                'status': 'error',
                'error': str(e),
                'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'model_used': self.model
            }
    
    def _make_api_call(self, prompt: str, max_retries: int = None) -> str:
        """Make API call to OpenAI with retry logic."""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making API call (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert tender evaluation specialist. Always respond with valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    timeout=60
                )
                
                content = response.choices[0].message.content
                logger.info("API call successful")
                return content
                
            except Exception as e:
                logger.error(f"API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"API error after {max_retries} attempts: {e}")
        
        raise Exception("All retry attempts failed")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from API, handling common formatting issues."""
        try:
            # Clean the response
            response = response.strip()
            
            # Find JSON content if wrapped in markdown
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Try to parse directly
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            
            # Return a fallback structure
            logger.warning("Returning fallback analysis structure")
            return {
                "supplier_name": "Unknown",
                "criteria_scores": {
                    "technical_compliance": {"score": 50, "justification": "Analysis failed", "evidence": []},
                    "price_competitiveness": {"score": 50, "justification": "Analysis failed", "evidence": []},
                    "company_experience": {"score": 50, "justification": "Analysis failed", "evidence": []},
                    "timeline_feasibility": {"score": 50, "justification": "Analysis failed", "evidence": []},
                    "risk_assessment": {"score": 50, "justification": "Analysis failed", "evidence": []}
                },
                "final_score": 50.0,
                "overall_summary": "Analysis failed due to parsing error",
                "red_flags": ["Unable to parse AI response"],
                "recommendations": "Manual review required",
                "error": str(e)
            }
