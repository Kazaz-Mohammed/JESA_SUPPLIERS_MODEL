"""
Scoring and Ranking System for JESA Tender Evaluation

This module handles weighted scoring calculations, supplier ranking,
and result export functionality.
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProposalScorer:
    """
    Handles scoring calculations and supplier ranking.
    """
    
    def __init__(self):
        """Initialize the scorer with default weights."""
        self.default_weights = {
            'technical_compliance': 30,
            'price_competitiveness': 25,
            'company_experience': 20,
            'timeline_feasibility': 15,
            'risk_assessment': 10
        }
        
        logger.info("ProposalScorer initialized")
    
    def validate_weights(self, weights: Dict[str, float]) -> Tuple[bool, str]:
        """
        Validate that weights sum to 100 and are non-negative.
        
        Args:
            weights (Dict[str, float]): Weights for each criterion
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            total_weight = sum(weights.values())
            
            if abs(total_weight - 100.0) > 0.01:  # Allow small floating point errors
                return False, f"Weights must sum to 100%, got {total_weight:.2f}%"
            
            for criterion, weight in weights.items():
                if weight < 0:
                    return False, f"Weight for {criterion} cannot be negative: {weight}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating weights: {str(e)}"
    
    def calculate_weighted_score(self, analysis: Dict[str, Any], weights: Dict[str, float] = None) -> float:
        """
        Calculate weighted final score for a supplier.
        
        Args:
            analysis (Dict[str, Any]): Analysis results from the analyzer
            weights (Dict[str, float], optional): Custom weights. Uses defaults if None.
            
        Returns:
            float: Weighted final score (0-100)
        """
        try:
            weights = weights or self.default_weights
            
            # Validate weights
            is_valid, error_msg = self.validate_weights(weights)
            if not is_valid:
                logger.error(f"Weight validation failed: {error_msg}")
                return 0.0
            
            # Extract scores
            criteria_scores = analysis.get('criteria_scores', {})
            weighted_sum = 0.0
            total_weight = 0.0
            
            for criterion, weight in weights.items():
                criterion_data = criteria_scores.get(criterion, {})
                if isinstance(criterion_data, dict):
                    score = criterion_data.get('score', 0)
                    weighted_sum += score * (weight / 100.0)
                    total_weight += weight
            
            if total_weight == 0:
                logger.warning("No valid weights found, returning 0")
                return 0.0
            
            final_score = weighted_sum / (total_weight / 100.0)
            
            # Ensure score is within bounds
            final_score = max(0.0, min(100.0, final_score))
            
            logger.debug(f"Calculated weighted score: {final_score:.2f}")
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating weighted score: {e}")
            return 0.0
    
    def rank_suppliers(self, analyses: List[Dict[str, Any]], weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Rank suppliers based on their weighted scores.
        
        Args:
            analyses (List[Dict[str, Any]]): List of analysis results
            weights (Dict[str, float], optional): Custom weights. Uses defaults if None.
            
        Returns:
            List[Dict[str, Any]]: Ranked list of suppliers (highest score first)
        """
        try:
            logger.info(f"Ranking {len(analyses)} suppliers")
            
            # Calculate weighted scores for all suppliers
            ranked_suppliers = []
            
            for i, analysis in enumerate(analyses):
                weighted_score = self.calculate_weighted_score(analysis, weights)
                
                # Add ranking information
                supplier_data = analysis.copy()
                supplier_data['weighted_score'] = weighted_score
                supplier_data['rank'] = 0  # Will be set after sorting
                
                ranked_suppliers.append(supplier_data)
            
            # Sort by weighted score (descending)
            ranked_suppliers.sort(key=lambda x: x['weighted_score'], reverse=True)
            
            # Assign ranks
            for i, supplier in enumerate(ranked_suppliers):
                supplier['rank'] = i + 1
            
            logger.info(f"Ranking completed. Top supplier: {ranked_suppliers[0].get('supplier_name', 'Unknown')} (Score: {ranked_suppliers[0].get('weighted_score', 0):.2f})")
            
            return ranked_suppliers
            
        except Exception as e:
            logger.error(f"Error ranking suppliers: {e}")
            return []
    
    def generate_summary_statistics(self, ranked_suppliers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for the evaluation results.
        
        Args:
            ranked_suppliers (List[Dict[str, Any]]): Ranked list of suppliers
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        try:
            if not ranked_suppliers:
                return {
                    'total_suppliers': 0,
                    'average_score': 0,
                    'highest_score': 0,
                    'lowest_score': 0,
                    'score_range': 0
                }
            
            scores = [s.get('weighted_score', 0) for s in ranked_suppliers]
            
            stats = {
                'total_suppliers': len(ranked_suppliers),
                'average_score': round(sum(scores) / len(scores), 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'score_range': round(max(scores) - min(scores), 2),
                'top_supplier': ranked_suppliers[0].get('supplier_name', 'Unknown'),
                'top_score': ranked_suppliers[0].get('weighted_score', 0),
                'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add score distribution
            score_ranges = {
                'excellent': len([s for s in scores if s >= 80]),
                'good': len([s for s in scores if 60 <= s < 80]),
                'fair': len([s for s in scores if 40 <= s < 60]),
                'poor': len([s for s in scores if s < 40])
            }
            stats['score_distribution'] = score_ranges
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating summary statistics: {e}")
            return {}


class ResultsExporter:
    """
    Handles export of evaluation results to various formats.
    """
    
    def __init__(self):
        """Initialize the exporter."""
        logger.info("ResultsExporter initialized")
    
    def export_to_excel(self, ranked_suppliers: List[Dict[str, Any]], 
                       summary_stats: Dict[str, Any], 
                       weights: Dict[str, float],
                       filename: str = None) -> str:
        """
        Export results to Excel file with multiple sheets.
        
        Args:
            ranked_suppliers (List[Dict[str, Any]]): Ranked list of suppliers
            summary_stats (Dict[str, Any]): Summary statistics
            weights (Dict[str, float]): Weights used for evaluation
            filename (str, optional): Output filename. Auto-generated if None.
            
        Returns:
            str: Path to the exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"tender_evaluation_results_{timestamp}.xlsx"
            
            # Ensure .xlsx extension
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            logger.info(f"Exporting results to: {filename}")
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Summary sheet
                self._create_summary_sheet(writer, summary_stats, weights)
                
                # Rankings sheet
                self._create_rankings_sheet(writer, ranked_suppliers)
                
                # Detailed analysis sheet
                self._create_detailed_sheet(writer, ranked_suppliers)
                
                # Criteria breakdown sheet
                self._create_criteria_sheet(writer, ranked_suppliers, weights)
            
            logger.info(f"Export completed successfully: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, 
                            summary_stats: Dict[str, Any], 
                            weights: Dict[str, float]):
        """Create summary sheet with evaluation overview."""
        summary_data = {
            'Metric': [
                'Total Suppliers Evaluated',
                'Top Supplier',
                'Top Score',
                'Average Score',
                'Score Range',
                'Evaluation Date',
                '',
                'Evaluation Weights:',
                'Technical Compliance',
                'Price Competitiveness', 
                'Company Experience',
                'Timeline Feasibility',
                'Risk Assessment'
            ],
            'Value': [
                summary_stats.get('total_suppliers', 0),
                summary_stats.get('top_supplier', 'N/A'),
                summary_stats.get('top_score', 0),
                summary_stats.get('average_score', 0),
                summary_stats.get('score_range', 0),
                summary_stats.get('evaluation_timestamp', 'N/A'),
                '',
                '',
                f"{weights.get('technical_compliance', 0)}%",
                f"{weights.get('price_competitiveness', 0)}%",
                f"{weights.get('company_experience', 0)}%",
                f"{weights.get('timeline_feasibility', 0)}%",
                f"{weights.get('risk_assessment', 0)}%"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    def _create_rankings_sheet(self, writer: pd.ExcelWriter, 
                             ranked_suppliers: List[Dict[str, Any]]):
        """Create rankings sheet with supplier scores."""
        rankings_data = []
        
        for supplier in ranked_suppliers:
            criteria_scores = supplier.get('criteria_scores', {})
            
            rankings_data.append({
                'Rank': supplier.get('rank', 0),
                'Supplier Name': supplier.get('supplier_name', 'Unknown'),
                'Final Score': supplier.get('weighted_score', 0),
                'Technical Compliance': criteria_scores.get('technical_compliance', {}).get('score', 0),
                'Price Competitiveness': criteria_scores.get('price_competitiveness', {}).get('score', 0),
                'Company Experience': criteria_scores.get('company_experience', {}).get('score', 0),
                'Timeline Feasibility': criteria_scores.get('timeline_feasibility', {}).get('score', 0),
                'Risk Assessment': criteria_scores.get('risk_assessment', {}).get('score', 0),
                'Overall Summary': supplier.get('overall_summary', 'N/A')
            })
        
        df_rankings = pd.DataFrame(rankings_data)
        df_rankings.to_excel(writer, sheet_name='Rankings', index=False)
    
    def _create_detailed_sheet(self, writer: pd.ExcelWriter, 
                             ranked_suppliers: List[Dict[str, Any]]):
        """Create detailed analysis sheet with full justifications."""
        detailed_data = []
        
        for supplier in ranked_suppliers:
            criteria_scores = supplier.get('criteria_scores', {})
            
            for criterion, data in criteria_scores.items():
                if isinstance(data, dict):
                    detailed_data.append({
                        'Supplier': supplier.get('supplier_name', 'Unknown'),
                        'Rank': supplier.get('rank', 0),
                        'Criterion': criterion.replace('_', ' ').title(),
                        'Score': data.get('score', 0),
                        'Justification': data.get('justification', 'N/A'),
                        'Evidence': '; '.join(data.get('evidence', [])),
                        'Red Flags': '; '.join(supplier.get('red_flags', [])),
                        'Recommendations': supplier.get('recommendations', 'N/A')
                    })
        
        df_detailed = pd.DataFrame(detailed_data)
        df_detailed.to_excel(writer, sheet_name='Detailed Analysis', index=False)
    
    def _create_criteria_sheet(self, writer: pd.ExcelWriter, 
                             ranked_suppliers: List[Dict[str, Any]], 
                             weights: Dict[str, float]):
        """Create criteria breakdown sheet."""
        criteria_data = []
        
        for criterion in ['technical_compliance', 'price_competitiveness', 
                         'company_experience', 'timeline_feasibility', 'risk_assessment']:
            
            criterion_name = criterion.replace('_', ' ').title()
            weight = weights.get(criterion, 0)
            
            scores = []
            for supplier in ranked_suppliers:
                criterion_data_supplier = supplier.get('criteria_scores', {}).get(criterion, {})
                if isinstance(criterion_data_supplier, dict):
                    scores.append(criterion_data_supplier.get('score', 0))
            
            if scores:
                criteria_data.append({
                    'Criterion': criterion_name,
                    'Weight': f"{weight}%",
                    'Average Score': round(sum(scores) / len(scores), 2),
                    'Highest Score': max(scores),
                    'Lowest Score': min(scores),
                    'Score Range': max(scores) - min(scores)
                })
        
        df_criteria = pd.DataFrame(criteria_data)
        df_criteria.to_excel(writer, sheet_name='Criteria Breakdown', index=False)
    
    def export_to_json(self, ranked_suppliers: List[Dict[str, Any]], 
                      summary_stats: Dict[str, Any], 
                      weights: Dict[str, float],
                      filename: str = None) -> str:
        """
        Export results to JSON file.
        
        Args:
            ranked_suppliers (List[Dict[str, Any]]): Ranked list of suppliers
            summary_stats (Dict[str, Any]): Summary statistics
            weights (Dict[str, float]): Weights used for evaluation
            filename (str, optional): Output filename. Auto-generated if None.
            
        Returns:
            str: Path to the exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"tender_evaluation_results_{timestamp}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            export_data = {
                'evaluation_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'weights_used': weights,
                    'total_suppliers': len(ranked_suppliers)
                },
                'summary_statistics': summary_stats,
                'ranked_suppliers': ranked_suppliers
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON export completed: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise


# Convenience functions
def calculate_weighted_score(analysis: Dict[str, Any], weights: Dict[str, float] = None) -> float:
    """Convenience function to calculate weighted score."""
    scorer = ProposalScorer()
    return scorer.calculate_weighted_score(analysis, weights)


def rank_suppliers(analyses: List[Dict[str, Any]], weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
    """Convenience function to rank suppliers."""
    scorer = ProposalScorer()
    return scorer.rank_suppliers(analyses, weights)


def export_to_excel(ranked_suppliers: List[Dict[str, Any]], 
                   summary_stats: Dict[str, Any], 
                   weights: Dict[str, float],
                   filename: str = None) -> str:
    """Convenience function to export to Excel."""
    exporter = ResultsExporter()
    return exporter.export_to_excel(ranked_suppliers, summary_stats, weights, filename)
