"""
PDF Processing Module for JESA Tender Evaluation System

This module handles PDF text extraction with robust error handling
and text cleaning capabilities.
"""

import pdfplumber
import PyPDF2
import logging
import re
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF text extraction with multiple fallback methods.
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_file_size_mb = 50  # Configurable limit
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file using multiple methods for robustness.
        
        Args:
            pdf_file_path (str): Path to the PDF file
            
        Returns:
            Dict containing extracted text, metadata, and processing info
        """
        try:
            # Validate file
            file_path = Path(pdf_file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")
            
            if not file_path.suffix.lower() == '.pdf':
                raise ValueError(f"File is not a PDF: {pdf_file_path}")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise ValueError(f"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB")
            
            logger.info(f"Processing PDF: {file_path.name} ({file_size_mb:.1f}MB)")
            
            # Try pdfplumber first (better for complex layouts)
            text = self._extract_with_pdfplumber(pdf_file_path)
            
            # If pdfplumber fails or returns minimal text, try PyPDF2
            if not text or len(text.strip()) < 100:
                logger.warning("pdfplumber extraction minimal, trying PyPDF2")
                text_pypdf2 = self._extract_with_pypdf2(pdf_file_path)
                if text_pypdf2 and len(text_pypdf2.strip()) > len(text.strip()):
                    text = text_pypdf2
            
            # Clean and validate extracted text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 50:
                raise ValueError("Unable to extract meaningful text from PDF")
            
            return {
                'text': cleaned_text,
                'file_name': file_path.name,
                'file_size_mb': file_size_mb,
                'text_length': len(cleaned_text),
                'page_count': self._get_page_count(pdf_file_path),
                'extraction_method': 'pdfplumber' if len(text.strip()) >= 100 else 'pypdf2',
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_file_path}: {str(e)}")
            return {
                'text': '',
                'file_name': Path(pdf_file_path).name if pdf_file_path else 'unknown',
                'file_size_mb': 0,
                'text_length': 0,
                'page_count': 0,
                'extraction_method': 'failed',
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_with_pdfplumber(self, pdf_file_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)."""
        try:
            text_parts = []
            with pdfplumber.open(pdf_file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_file_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)."""
        try:
            text_parts = []
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers (common patterns)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^--- Page \d+ ---$', '', text, flags=re.MULTILINE)
        
        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\%\$\@\#\&\*\+\=]', '', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _get_page_count(self, pdf_file_path: str) -> int:
        """Get the number of pages in the PDF."""
        try:
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception:
            return 0
    
    def validate_pdf(self, pdf_file_path: str) -> Dict[str, Any]:
        """
        Validate PDF file without extracting text.
        
        Args:
            pdf_file_path (str): Path to the PDF file
            
        Returns:
            Dict containing validation results
        """
        try:
            file_path = Path(pdf_file_path)
            
            # Basic file checks
            if not file_path.exists():
                return {'valid': False, 'error': 'File not found'}
            
            if not file_path.suffix.lower() == '.pdf':
                return {'valid': False, 'error': 'Not a PDF file'}
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {'valid': False, 'error': f'File too large ({file_size_mb:.1f}MB)'}
            
            # Try to open PDF
            try:
                with open(pdf_file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
                    
                    return {
                        'valid': True,
                        'file_name': file_path.name,
                        'file_size_mb': file_size_mb,
                        'page_count': page_count
                    }
            except Exception as e:
                return {'valid': False, 'error': f'Corrupted PDF: {str(e)}'}
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}


def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Simple wrapper function for backward compatibility.
    
    Args:
        pdf_file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted and cleaned text
    """
    processor = PDFProcessor()
    result = processor.extract_text_from_pdf(pdf_file_path)
    return result.get('text', '')


# Example usage and testing
if __name__ == "__main__":
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Example usage
    sample_pdf = "data/sample_tender.pdf"
    
    print("PDF Processor Test")
    print("=" * 50)
    
    # Validate first
    validation = processor.validate_pdf(sample_pdf)
    print(f"Validation: {validation}")
    
    if validation.get('valid'):
        # Extract text
        result = processor.extract_text_from_pdf(sample_pdf)
        print(f"\nExtraction Status: {result['status']}")
        print(f"File: {result['file_name']}")
        print(f"Size: {result['file_size_mb']:.1f}MB")
        print(f"Pages: {result['page_count']}")
        print(f"Text Length: {result['text_length']} characters")
        print(f"Method: {result['extraction_method']}")
        
        if result['status'] == 'success':
            print(f"\nFirst 200 characters of extracted text:")
            print("-" * 50)
            print(result['text'][:200] + "..." if len(result['text']) > 200 else result['text'])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print(f"Validation failed: {validation.get('error', 'Unknown error')}")
