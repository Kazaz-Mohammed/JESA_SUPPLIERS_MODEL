#!/usr/bin/env python3
"""
Comprehensive Test Suite for JESA Tender Evaluation System
Tests all components, edge cases, and error conditions
"""

import os
import sys
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import io
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_processor import extract_text_from_pdf, extract_text_from_file
from utils.analyzer import analyze_proposal
from utils.scorer import calculate_weighted_score, rank_suppliers, export_to_excel


class TestPDFProcessor(unittest.TestCase):
    """Test PDF processing functionality"""
    
    def test_extract_text_from_pdf_valid(self):
        """Test extracting text from a valid PDF"""
        # Create a mock PDF content
        mock_pdf_content = b"Mock PDF content for testing"
        
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_pdf.pages = [Mock()]
            mock_pdf.pages[0].extract_text.return_value = "Sample text from PDF"
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = extract_text_from_pdf(mock_pdf_content)
            self.assertEqual(result, "Sample text from PDF")
    
    def test_extract_text_from_pdf_empty(self):
        """Test handling of empty PDF"""
        empty_pdf = b""
        
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_pdf.pages = []
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = extract_text_from_pdf(empty_pdf)
            self.assertEqual(result, "")
    
    def test_extract_text_from_pdf_error(self):
        """Test handling of corrupted PDF"""
        corrupted_pdf = b"Not a PDF file"
        
        with patch('pdfplumber.open', side_effect=Exception("Invalid PDF")):
            result = extract_text_from_pdf(corrupted_pdf)
            self.assertIn("Error extracting text", result)
    
    def test_extract_text_from_file_txt(self):
        """Test extracting text from TXT file"""
        txt_content = b"This is a text file content"
        result = extract_text_from_file(txt_content, "test.txt")
        self.assertEqual(result, "This is a text file content")
    
    def test_extract_text_from_file_encoding_error(self):
        """Test handling of encoding errors"""
        # Create content with invalid encoding
        invalid_content = b'\xff\xfe\x00\x00'  # Invalid UTF-8
        
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            result = extract_text_from_file(invalid_content, "test.txt")
            self.assertIn("Error extracting text", result)


class TestAnalyzer(unittest.TestCase):
    """Test AI analysis functionality"""
    
    def setUp(self):
        self.sample_tender = "Sample tender requirements for testing"
        self.sample_proposal = "Sample proposal content for testing"
    
    @patch('utils.analyzer.OpenAI')
    def test_analyze_proposal_success(self, mock_openai):
        """Test successful proposal analysis"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "supplier_name": "Test Supplier",
            "criteria_scores": {
                "technical_compliance": {"score": 85, "justification": "Good technical approach", "evidence": ["Evidence 1"]},
                "price_competitiveness": {"score": 75, "justification": "Reasonable pricing", "evidence": []},
                "company_experience": {"score": 90, "justification": "Strong experience", "evidence": []},
                "timeline_feasibility": {"score": 80, "justification": "Feasible timeline", "evidence": []},
                "risk_assessment": {"score": 85, "justification": "Low risk", "evidence": []}
            },
            "final_score": 83.0,
            "overall_summary": "Good proposal overall",
            "red_flags": [],
            "recommendations": "Recommended"
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = analyze_proposal(self.sample_proposal, self.sample_tender)
        
        self.assertEqual(result['supplier_name'], 'Test Supplier')
        self.assertEqual(result['final_score'], 83.0)
        self.assertIn('criteria_scores', result)
    
    @patch('utils.analyzer.OpenAI')
    def test_analyze_proposal_api_error(self, mock_openai):
        """Test handling of API errors"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = analyze_proposal(self.sample_proposal, self.sample_tender)
        
        self.assertIn('error', result)
        self.assertIn('Analysis failed', result['overall_summary'])
    
    def test_analyze_proposal_empty_inputs(self):
        """Test handling of empty inputs"""
        result = analyze_proposal("", "")
        self.assertIn('error', result)
        
        result = analyze_proposal(None, None)
        self.assertIn('error', result)
    
    def test_analyze_proposal_long_document(self):
        """Test handling of very long documents"""
        # Create a very long document
        long_proposal = "This is a very long proposal. " * 1000  # ~30KB
        
        with patch('utils.analyzer.OpenAI') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"supplier_name": "Test", "final_score": 50}'
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = analyze_proposal(long_proposal, self.sample_tender)
            
            # Should truncate the input
            self.assertLess(len(long_proposal), len(result.get('original_proposal', '')))


class TestScorer(unittest.TestCase):
    """Test scoring and ranking functionality"""
    
    def setUp(self):
        self.sample_analysis = {
            "supplier_name": "Test Supplier",
            "criteria_scores": {
                "technical_compliance": {"score": 85},
                "price_competitiveness": {"score": 75},
                "company_experience": {"score": 90},
                "timeline_feasibility": {"score": 80},
                "risk_assessment": {"score": 85}
            },
            "final_score": 83.0
        }
        
        self.weights = {
            "technical_compliance": 30,
            "price_competitiveness": 25,
            "company_experience": 20,
            "timeline_feasibility": 15,
            "risk_assessment": 10
        }
    
    def test_calculate_weighted_score_valid(self):
        """Test valid weighted score calculation"""
        score = calculate_weighted_score(self.sample_analysis, self.weights)
        
        # Expected: (85*0.3 + 75*0.25 + 90*0.2 + 80*0.15 + 85*0.1) = 82.75
        self.assertEqual(score, 82.75)
    
    def test_calculate_weighted_score_invalid_weights(self):
        """Test handling of invalid weights"""
        invalid_weights = {"technical_compliance": 50, "price_competitiveness": 60}  # Sum > 100
        
        with self.assertRaises(ValueError):
            calculate_weighted_score(self.sample_analysis, invalid_weights)
    
    def test_calculate_weighted_score_missing_criteria(self):
        """Test handling of missing criteria in analysis"""
        incomplete_analysis = {
            "supplier_name": "Test Supplier",
            "criteria_scores": {
                "technical_compliance": {"score": 85},
                "price_competitiveness": {"score": 75}
                # Missing other criteria
            }
        }
        
        with self.assertRaises(KeyError):
            calculate_weighted_score(incomplete_analysis, self.weights)
    
    def test_rank_suppliers_valid(self):
        """Test valid supplier ranking"""
        # Create analyses with different criteria scores to ensure different weighted scores
        supplier_a = {
            "supplier_name": "Supplier A",
            "criteria_scores": {
                "technical_compliance": {"score": 70},
                "price_competitiveness": {"score": 80},
                "company_experience": {"score": 75},
                "timeline_feasibility": {"score": 85},
                "risk_assessment": {"score": 90}
            },
            "final_score": 80
        }
        
        supplier_b = {
            "supplier_name": "Supplier B",
            "criteria_scores": {
                "technical_compliance": {"score": 90},
                "price_competitiveness": {"score": 75},
                "company_experience": {"score": 85},
                "timeline_feasibility": {"score": 80},
                "risk_assessment": {"score": 95}
            },
            "final_score": 85
        }
        
        supplier_c = {
            "supplier_name": "Supplier C",
            "criteria_scores": {
                "technical_compliance": {"score": 60},
                "price_competitiveness": {"score": 70},
                "company_experience": {"score": 65},
                "timeline_feasibility": {"score": 75},
                "risk_assessment": {"score": 80}
            },
            "final_score": 70
        }
        
        analyses = [supplier_a, supplier_b, supplier_c]
        ranked = rank_suppliers(analyses, self.weights)
        
        # Supplier B should have the highest weighted score (90*0.3 + 75*0.25 + 85*0.2 + 80*0.15 + 95*0.1 = 82.5)
        # Supplier A should be second (70*0.3 + 80*0.25 + 75*0.2 + 85*0.15 + 90*0.1 = 77.75)
        # Supplier C should be third (60*0.3 + 70*0.25 + 65*0.2 + 75*0.15 + 80*0.1 = 68.25)
        
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0]["supplier_name"], "Supplier B")
        self.assertEqual(ranked[1]["supplier_name"], "Supplier A")
        self.assertEqual(ranked[2]["supplier_name"], "Supplier C")
    
    def test_rank_suppliers_empty(self):
        """Test ranking empty list"""
        ranked = rank_suppliers([])
        self.assertEqual(ranked, [])
    
    def test_export_to_excel_valid(self):
        """Test valid Excel export"""
        analyses = [self.sample_analysis]
        summary_stats = {"total_suppliers": 1, "average_score": 83.0}
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            try:
                export_to_excel(analyses, summary_stats, self.weights, tmp_file.name)
                self.assertTrue(os.path.exists(tmp_file.name))
                self.assertGreater(os.path.getsize(tmp_file.name), 0)
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
    
    def test_export_to_excel_invalid_path(self):
        """Test Excel export with invalid path"""
        analyses = [self.sample_analysis]
        summary_stats = {"total_suppliers": 1, "average_score": 83.0}
        
        with self.assertRaises(Exception):
            export_to_excel(analyses, summary_stats, self.weights, "/invalid/path/file.xlsx")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_malformed_json_response(self):
        """Test handling of malformed JSON from AI"""
        malformed_json = '''
        {
            "supplier_name": "Test Supplier",
            "criteria_scores": {
                "technical_compliance": {"score": 85, "justification": "Good
            // Missing closing braces and quotes
        }
        '''
        
        with patch('utils.analyzer.OpenAI') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = malformed_json
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = analyze_proposal("test proposal", "test tender")
            
            # Should handle gracefully
            self.assertIn('error', result)
    
    def test_weights_not_summing_to_100(self):
        """Test weights that don't sum to 100"""
        weights = {
            "technical_compliance": 20,
            "price_competitiveness": 30,
            "company_experience": 20,
            "timeline_feasibility": 15,
            "risk_assessment": 10
        }  # Sum = 95
        
        analysis = {
            "supplier_name": "Test",
            "criteria_scores": {
                "technical_compliance": {"score": 85},
                "price_competitiveness": {"score": 75},
                "company_experience": {"score": 90},
                "timeline_feasibility": {"score": 80},
                "risk_assessment": {"score": 85}
            }
        }
        
        with self.assertRaises(ValueError):
            calculate_weighted_score(analysis, weights)
    
    def test_negative_scores(self):
        """Test handling of negative scores"""
        analysis_with_negative = {
            "supplier_name": "Test",
            "criteria_scores": {
                "technical_compliance": {"score": -10},  # Negative score
                "price_competitiveness": {"score": 75},
                "company_experience": {"score": 90},
                "timeline_feasibility": {"score": 80},
                "risk_assessment": {"score": 85}
            }
        }
        
        weights = {
            "technical_compliance": 30,
            "price_competitiveness": 25,
            "company_experience": 20,
            "timeline_feasibility": 15,
            "risk_assessment": 10
        }
        
        # Should still calculate (negative scores are valid)
        score = calculate_weighted_score(analysis_with_negative, weights)
        self.assertIsInstance(score, (int, float))


class TestPerformance(unittest.TestCase):
    """Test performance with large datasets"""
    
    def test_large_number_of_proposals(self):
        """Test handling of many proposals"""
        # Create 50 mock analyses
        analyses = []
        for i in range(50):
            analysis = {
                "supplier_name": f"Supplier {i}",
                "criteria_scores": {
                    "technical_compliance": {"score": 70 + (i % 30)},
                    "price_competitiveness": {"score": 75 + (i % 25)},
                    "company_experience": {"score": 80 + (i % 20)},
                    "timeline_feasibility": {"score": 85 + (i % 15)},
                    "risk_assessment": {"score": 90 + (i % 10)}
                },
                "final_score": 75 + (i % 25)
            }
            analyses.append(analysis)
        
        # Should handle large datasets efficiently
        ranked = rank_suppliers(analyses)
        self.assertEqual(len(ranked), 50)
        
        # Should be sorted correctly
        scores = [a['final_score'] for a in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🧪 Starting Comprehensive Test Suite...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPDFProcessor,
        TestAnalyzer,
        TestScorer,
        TestEdgeCases,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
