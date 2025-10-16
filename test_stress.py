#!/usr/bin/env python3
"""
Stress Testing Suite for JESA Tender Evaluation System
Tests system behavior under extreme conditions and error scenarios
"""

import os
import sys
import time
import random
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_processor import extract_text_from_pdf, extract_text_from_file
from utils.scorer import calculate_weighted_score, rank_suppliers, export_to_excel


def generate_corrupted_data():
    """Generate various types of corrupted data for testing"""
    return {
        "empty_bytes": b"",
        "null_bytes": b"\x00\x00\x00\x00",
        "invalid_utf8": b"\xff\xfe\x00\x00",
        "extremely_long": b"A" * (10 * 1024 * 1024),  # 10MB of 'A's
        "binary_data": bytes(range(256)),
        "malformed_json": b'{"invalid": json without proper closing}',
        "unicode_bombs": "💣" * 1000,
        "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" * 100
    }


def test_extreme_file_sizes():
    """Test with extremely large and small files"""
    print("📁 Testing Extreme File Sizes...")
    
    # Test very small files
    print("   Testing very small files...")
    tiny_files = [b"", b"A", b"AB", b"ABC"]
    
    for i, content in enumerate(tiny_files):
        try:
            result = extract_text_from_file(content, f"tiny_{i}.txt")
            print(f"      ✅ Tiny file {i}: '{result}'")
        except Exception as e:
            print(f"      ❌ Tiny file {i} failed: {str(e)}")
    
    # Test very large files
    print("   Testing very large files...")
    large_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
    
    for size in large_sizes:
        large_content = ("A" * size).encode('utf-8')
        try:
            start_time = time.time()
            result = extract_text_from_file(large_content, "large.txt")
            processing_time = time.time() - start_time
            
            print(f"      ✅ Large file ({size} bytes): {processing_time:.3f}s")
            print(f"         Result length: {len(result):,} characters")
        except Exception as e:
            print(f"      ❌ Large file ({size} bytes) failed: {str(e)}")


def test_corrupted_data_handling():
    """Test handling of corrupted and malformed data"""
    print("\n💥 Testing Corrupted Data Handling...")
    
    corrupted_data = generate_corrupted_data()
    
    for data_type, content in corrupted_data.items():
        print(f"   Testing {data_type}...")
        
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            result = extract_text_from_file(content, f"test_{data_type}.txt")
            print(f"      ✅ {data_type}: Handled gracefully")
            print(f"         Result length: {len(result)}")
            
        except Exception as e:
            print(f"      ⚠️ {data_type}: Expected error - {str(e)}")


def test_invalid_scoring_data():
    """Test scoring with invalid data"""
    print("\n📊 Testing Invalid Scoring Data...")
    
    # Test with missing criteria
    incomplete_analysis = {
        "supplier_name": "Incomplete Supplier",
        "criteria_scores": {
            "technical_compliance": {"score": 85}
            # Missing other criteria
        }
    }
    
    weights = {
        "technical_compliance": 30,
        "price_competitiveness": 25,
        "company_experience": 20,
        "timeline_feasibility": 15,
        "risk_assessment": 10
    }
    
    try:
        score = calculate_weighted_score(incomplete_analysis, weights)
        print(f"   ❌ Should have failed but got score: {score}")
    except KeyError as e:
        print(f"   ✅ Correctly caught missing criteria: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ Unexpected error: {str(e)}")
    
    # Test with invalid score types
    invalid_score_analysis = {
        "supplier_name": "Invalid Score Supplier",
        "criteria_scores": {
            "technical_compliance": {"score": "not_a_number"},
            "price_competitiveness": {"score": None},
            "company_experience": {"score": [1, 2, 3]},
            "timeline_feasibility": {"score": 80},
            "risk_assessment": {"score": 85}
        }
    }
    
    try:
        score = calculate_weighted_score(invalid_score_analysis, weights)
        print(f"   ❌ Should have failed but got score: {score}")
    except (TypeError, ValueError) as e:
        print(f"   ✅ Correctly caught invalid score types: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ Unexpected error: {str(e)}")
    
    # Test with extreme scores
    extreme_analysis = {
        "supplier_name": "Extreme Score Supplier",
        "criteria_scores": {
            "technical_compliance": {"score": -1000},
            "price_competitiveness": {"score": 10000},
            "company_experience": {"score": float('inf')},
            "timeline_feasibility": {"score": float('-inf')},
            "risk_assessment": {"score": float('nan')}
        }
    }
    
    try:
        score = calculate_weighted_score(extreme_analysis, weights)
        print(f"   ⚠️ Extreme scores handled: {score}")
    except Exception as e:
        print(f"   ✅ Correctly caught extreme scores: {str(e)}")


def test_invalid_weights():
    """Test with invalid weight configurations"""
    print("\n⚖️ Testing Invalid Weight Configurations...")
    
    valid_analysis = {
        "supplier_name": "Test Supplier",
        "criteria_scores": {
            "technical_compliance": {"score": 85},
            "price_competitiveness": {"score": 75},
            "company_experience": {"score": 90},
            "timeline_feasibility": {"score": 80},
            "risk_assessment": {"score": 85}
        }
    }
    
    invalid_weight_configs = [
        # Weights don't sum to 100
        {"technical_compliance": 50, "price_competitiveness": 60},
        {"technical_compliance": 20, "price_competitiveness": 30},
        # Negative weights
        {"technical_compliance": -30, "price_competitiveness": 130},
        # Missing criteria
        {"technical_compliance": 100},
        # Extra criteria
        {"technical_compliance": 30, "price_competitiveness": 25, "extra_criteria": 45},
        # Non-numeric weights
        {"technical_compliance": "30", "price_competitiveness": 25},
        # None values
        {"technical_compliance": None, "price_competitiveness": 100}
    ]
    
    for i, weights in enumerate(invalid_weight_configs):
        print(f"   Testing invalid weight config {i+1}...")
        
        try:
            score = calculate_weighted_score(valid_analysis, weights)
            print(f"      ❌ Should have failed but got score: {score}")
        except (ValueError, KeyError, TypeError) as e:
            print(f"      ✅ Correctly caught invalid weights: {str(e)}")
        except Exception as e:
            print(f"      ⚠️ Unexpected error: {str(e)}")


def test_massive_datasets():
    """Test with massive datasets to find performance limits"""
    print("\n🚀 Testing Massive Datasets...")
    
    # Test with 1000 suppliers
    print("   Testing with 1000 suppliers...")
    
    try:
        start_time = time.time()
        
        # Generate 1000 mock analyses
        analyses = []
        for i in range(1000):
            analysis = {
                "supplier_name": f"Supplier {i:04d}",
                "criteria_scores": {
                    "technical_compliance": {"score": random.randint(0, 100)},
                    "price_competitiveness": {"score": random.randint(0, 100)},
                    "company_experience": {"score": random.randint(0, 100)},
                    "timeline_feasibility": {"score": random.randint(0, 100)},
                    "risk_assessment": {"score": random.randint(0, 100)}
                },
                "final_score": random.randint(0, 100)
            }
            analyses.append(analysis)
        
        generation_time = time.time() - start_time
        print(f"      ✅ Generated 1000 analyses in {generation_time:.3f}s")
        
        # Test ranking
        start_time = time.time()
        ranked = rank_suppliers(analyses)
        ranking_time = time.time() - start_time
        
        print(f"      ✅ Ranked 1000 suppliers in {ranking_time:.3f}s")
        print(f"         Top supplier: {ranked[0]['supplier_name']} (score: {ranked[0]['final_score']})")
        
        # Test Excel export
        start_time = time.time()
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            try:
                export_to_excel(analyses[:100], tmp_file.name)  # Export first 100 to avoid huge files
                export_time = time.time() - start_time
                
                file_size = os.path.getsize(tmp_file.name)
                print(f"      ✅ Exported 100 suppliers to Excel in {export_time:.3f}s")
                print(f"         File size: {file_size:,} bytes")
                
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
        
    except Exception as e:
        print(f"      ❌ Massive dataset test failed: {str(e)}")


def test_concurrent_stress():
    """Test concurrent access and potential race conditions"""
    print("\n⚡ Testing Concurrent Stress...")
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    errors_queue = queue.Queue()
    
    def worker_thread(thread_id, num_iterations=10):
        """Worker thread for concurrent testing"""
        try:
            for i in range(num_iterations):
                # Generate and process data
                analysis = {
                    "supplier_name": f"Thread{thread_id}_Supplier{i}",
                    "criteria_scores": {
                        "technical_compliance": {"score": random.randint(0, 100)},
                        "price_competitiveness": {"score": random.randint(0, 100)},
                        "company_experience": {"score": random.randint(0, 100)},
                        "timeline_feasibility": {"score": random.randint(0, 100)},
                        "risk_assessment": {"score": random.randint(0, 100)}
                    },
                    "final_score": random.randint(0, 100)
                }
                
                weights = {
                    "technical_compliance": 30,
                    "price_competitiveness": 25,
                    "company_experience": 20,
                    "timeline_feasibility": 15,
                    "risk_assessment": 10
                }
                
                score = calculate_weighted_score(analysis, weights)
                results_queue.put(f"Thread{thread_id}_Iter{i}: {score}")
                
                # Small delay to simulate real processing
                time.sleep(0.001)
                
        except Exception as e:
            errors_queue.put(f"Thread{thread_id}: {str(e)}")
    
    # Test with multiple threads
    thread_counts = [2, 5, 10]
    
    for thread_count in thread_counts:
        print(f"   Testing {thread_count} concurrent threads...")
        
        threads = []
        start_time = time.time()
        
        # Start threads
        for i in range(thread_count):
            thread = threading.Thread(target=worker_thread, args=(i, 5))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        errors = []
        while not errors_queue.empty():
            errors.append(errors_queue.get())
        
        print(f"      ✅ {thread_count} threads completed in {total_time:.3f}s")
        print(f"         Results: {len(results)} successful operations")
        print(f"         Errors: {len(errors)} errors")
        
        if errors:
            print(f"         Error details: {errors[:3]}")  # Show first 3 errors


def run_stress_tests():
    """Run all stress tests"""
    print("🔥 Starting Stress Test Suite...")
    print("=" * 60)
    
    try:
        # Run all stress tests
        test_extreme_file_sizes()
        test_corrupted_data_handling()
        test_invalid_scoring_data()
        test_invalid_weights()
        test_massive_datasets()
        test_concurrent_stress()
        
        print("\n" + "=" * 60)
        print("✅ Stress testing completed!")
        print("\n📋 Stress Test Summary:")
        print("   - Extreme File Sizes: Tested very small and very large files")
        print("   - Corrupted Data: Tested various corrupted data types")
        print("   - Invalid Scoring: Tested invalid analysis data")
        print("   - Invalid Weights: Tested invalid weight configurations")
        print("   - Massive Datasets: Tested with 1000+ suppliers")
        print("   - Concurrent Stress: Tested multi-threading scenarios")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Stress testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_stress_tests()
    sys.exit(0 if success else 1)
