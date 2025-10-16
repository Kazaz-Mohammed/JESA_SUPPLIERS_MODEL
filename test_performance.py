#!/usr/bin/env python3
"""
Performance Testing Suite for JESA Tender Evaluation System
Tests system performance with large datasets and stress conditions
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_processor import extract_text_from_pdf, extract_text_from_file
from utils.scorer import calculate_weighted_score, rank_suppliers, export_to_excel


def generate_large_proposal(size_kb=100):
    """Generate a large proposal text of specified size"""
    base_text = "This is a comprehensive proposal for the JESA construction project. "
    repeat_count = (size_kb * 1024) // len(base_text)
    return base_text * repeat_count


def generate_mock_analyses(count=100):
    """Generate mock analysis results for testing"""
    analyses = []
    for i in range(count):
        analysis = {
            "supplier_name": f"Supplier Company {i+1}",
            "criteria_scores": {
                "technical_compliance": {"score": 70 + (i % 30), "justification": f"Technical justification {i}"},
                "price_competitiveness": {"score": 75 + (i % 25), "justification": f"Price justification {i}"},
                "company_experience": {"score": 80 + (i % 20), "justification": f"Experience justification {i}"},
                "timeline_feasibility": {"score": 85 + (i % 15), "justification": f"Timeline justification {i}"},
                "risk_assessment": {"score": 90 + (i % 10), "justification": f"Risk justification {i}"}
            },
            "final_score": 75 + (i % 25),
            "overall_summary": f"Overall summary for supplier {i+1}",
            "red_flags": [],
            "recommendations": f"Recommendations for supplier {i+1}"
        }
        analyses.append(analysis)
    
    return analyses


def test_pdf_processing_performance():
    """Test PDF processing performance with various file sizes"""
    print("📄 Testing PDF Processing Performance...")
    
    test_sizes = [1, 10, 50, 100, 500]  # KB
    
    for size_kb in test_sizes:
        print(f"   Testing {size_kb}KB document...")
        
        # Generate large text content
        large_text = generate_large_proposal(size_kb)
        text_bytes = large_text.encode('utf-8')
        
        # Time the processing
        start_time = time.time()
        
        try:
            result = extract_text_from_file(text_bytes, "test.txt")
            processing_time = time.time() - start_time
            
            print(f"      ✅ {size_kb}KB processed in {processing_time:.3f}s")
            print(f"         Text length: {len(result):,} characters")
            
        except Exception as e:
            print(f"      ❌ Error processing {size_kb}KB: {str(e)}")


def test_scoring_performance():
    """Test scoring and ranking performance with large datasets"""
    print("\n📊 Testing Scoring Performance...")
    
    test_counts = [10, 50, 100, 200, 500]
    
    for count in test_counts:
        print(f"   Testing {count} suppliers...")
        
        # Generate mock data
        analyses = generate_mock_analyses(count)
        
        weights = {
            "technical_compliance": 30,
            "price_competitiveness": 25,
            "company_experience": 20,
            "timeline_feasibility": 15,
            "risk_assessment": 10
        }
        
        # Test weighted score calculation
        start_time = time.time()
        for analysis in analyses:
            calculate_weighted_score(analysis, weights)
        scoring_time = time.time() - start_time
        
        # Test ranking
        start_time = time.time()
        ranked = rank_suppliers(analyses)
        ranking_time = time.time() - start_time
        
        print(f"      ✅ {count} suppliers:")
        print(f"         Scoring: {scoring_time:.3f}s ({scoring_time/count*1000:.2f}ms per supplier)")
        print(f"         Ranking: {ranking_time:.3f}s")
        print(f"         Total: {scoring_time + ranking_time:.3f}s")


def test_excel_export_performance():
    """Test Excel export performance with large datasets"""
    print("\n📈 Testing Excel Export Performance...")
    
    test_counts = [10, 50, 100, 200]
    
    for count in test_counts:
        print(f"   Testing Excel export for {count} suppliers...")
        
        # Generate mock data
        analyses = generate_mock_analyses(count)
        
        # Test Excel export
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            try:
                start_time = time.time()
                export_to_excel(analyses, tmp_file.name)
                export_time = time.time() - start_time
                
                file_size = os.path.getsize(tmp_file.name)
                
                print(f"      ✅ {count} suppliers exported in {export_time:.3f}s")
                print(f"         File size: {file_size:,} bytes ({file_size/1024:.1f}KB)")
                
            except Exception as e:
                print(f"      ❌ Error exporting {count} suppliers: {str(e)}")
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass


def test_memory_usage():
    """Test memory usage with large datasets"""
    print("\n💾 Testing Memory Usage...")
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        
        # Test with increasing dataset sizes
        test_counts = [10, 50, 100, 200]
        
        for count in test_counts:
            print(f"   Testing memory usage with {count} suppliers...")
            
            # Measure memory before
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate and process data
            analyses = generate_mock_analyses(count)
            ranked = rank_suppliers(analyses)
            
            # Measure memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            print(f"      ✅ Memory usage: {memory_used:.1f}MB for {count} suppliers")
            print(f"         Per supplier: {memory_used/count*1024:.1f}KB")
            
    except ImportError:
        print("   ⚠️ psutil not available, skipping memory tests")


def test_concurrent_processing():
    """Test concurrent processing capabilities"""
    print("\n⚡ Testing Concurrent Processing...")
    
    try:
        import concurrent.futures
        import threading
        
        def process_supplier_batch(batch_id, batch_size=10):
            """Process a batch of suppliers"""
            analyses = generate_mock_analyses(batch_size)
            weights = {
                "technical_compliance": 30,
                "price_competitiveness": 25,
                "company_experience": 20,
                "timeline_feasibility": 15,
                "risk_assessment": 10
            }
            
            results = []
            for analysis in analyses:
                score = calculate_weighted_score(analysis, weights)
                results.append(score)
            
            return f"Batch {batch_id}: {len(results)} suppliers processed"
        
        # Test with different numbers of concurrent threads
        thread_counts = [1, 2, 4, 8]
        
        for thread_count in thread_counts:
            print(f"   Testing {thread_count} concurrent threads...")
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(process_supplier_batch, i, 10) for i in range(thread_count)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
            
            print(f"      ✅ {thread_count} threads completed in {total_time:.3f}s")
            print(f"         Results: {len(results)} batches processed")
            
    except ImportError:
        print("   ⚠️ concurrent.futures not available, skipping concurrent tests")


def run_performance_tests():
    """Run all performance tests"""
    print("🚀 Starting Performance Test Suite...")
    print("=" * 60)
    
    try:
        # Run all performance tests
        test_pdf_processing_performance()
        test_scoring_performance()
        test_excel_export_performance()
        test_memory_usage()
        test_concurrent_processing()
        
        print("\n" + "=" * 60)
        print("✅ Performance testing completed!")
        print("\n📋 Performance Test Summary:")
        print("   - PDF Processing: Tested various file sizes")
        print("   - Scoring & Ranking: Tested with up to 500 suppliers")
        print("   - Excel Export: Tested with up to 200 suppliers")
        print("   - Memory Usage: Monitored memory consumption")
        print("   - Concurrent Processing: Tested multi-threading")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)
