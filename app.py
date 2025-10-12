#!/usr/bin/env python3
"""
JESA Tender Evaluation System - Streamlit Web Interface

This is the main Streamlit application for the JESA Tender Evaluation System.
It provides a user-friendly web interface for uploading documents, configuring
evaluation weights, and viewing analysis results.
"""

import streamlit as st
import os
import tempfile
import time
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any

# Import our custom modules
from utils.analyzer import ProposalAnalyzer
from utils.scorer import ProposalScorer, ResultsExporter
from utils.pdf_processor import PDFProcessor

# Configure page
st.set_page_config(
    page_title="JESA Tender Evaluation System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    if 'tender_requirements' not in st.session_state:
        st.session_state.tender_requirements = ""
    if 'supplier_proposals' not in st.session_state:
        st.session_state.supplier_proposals = []
    if 'evaluation_weights' not in st.session_state:
        st.session_state.evaluation_weights = {
            'technical_compliance': 30,
            'price_competitiveness': 25,
            'company_experience': 20,
            'timeline_feasibility': 15,
            'risk_assessment': 10
        }


def validate_weights(weights: Dict[str, float]) -> bool:
    """Validate that weights sum to 100%."""
    total = sum(weights.values())
    return abs(total - 100.0) < 0.01


def display_header():
    """Display the application header."""
    st.markdown('<h1 class="main-header">🏗️ JESA Tender Evaluation System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            AI-Powered Supplier Proposal Analysis and Ranking
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display the sidebar with configuration options."""
    st.sidebar.header("⚙️ Configuration")
    
    # API Key Input
    st.sidebar.subheader("🔑 OpenAI API Key")
    api_key = st.sidebar.text_input(
        "Enter your OpenAI API Key",
        type="password",
        help="Your OpenAI API key for AI analysis"
    )
    
    # Evaluation Weights
    st.sidebar.subheader("📊 Evaluation Weights")
    st.sidebar.markdown("*Adjust the importance of each evaluation criterion (must total 100%)*")
    
    weights = {}
    weight_names = {
        'technical_compliance': 'Technical Compliance',
        'price_competitiveness': 'Price Competitiveness', 
        'company_experience': 'Company Experience',
        'timeline_feasibility': 'Timeline Feasibility',
        'risk_assessment': 'Risk Assessment'
    }
    
    for key, name in weight_names.items():
        weights[key] = st.sidebar.slider(
            name,
            min_value=0,
            max_value=100,
            value=st.session_state.evaluation_weights[key],
            step=1
        )
    
    # Validate weights
    if validate_weights(weights):
        st.sidebar.success("✅ Weights total 100%")
        st.session_state.evaluation_weights = weights
    else:
        total = sum(weights.values())
        st.sidebar.error(f"❌ Weights total {total}% (must be 100%)")
    
    return api_key


def display_file_upload():
    """Display file upload sections."""
    st.header("📁 Document Upload")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Tender Requirements")
        tender_file = st.file_uploader(
            "Upload Tender Requirements Document",
            type=['pdf', 'txt'],
            help="Upload the original tender/call for proposals document"
        )
        
        if tender_file is not None:
            # Process tender requirements file
            if tender_file.type == "text/plain":
                content = tender_file.read().decode("utf-8")
            else:
                # Handle PDF files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(tender_file.read())
                    processor = PDFProcessor()
                    result = processor.extract_text_from_pdf(tmp_file.name)
                    content = result.get('text', '')
                    os.unlink(tmp_file.name)
            
            st.session_state.tender_requirements = content
            st.success(f"✅ Tender requirements loaded ({len(content)} characters)")
            st.text_area("Preview:", content[:500] + "..." if len(content) > 500 else content, height=100)
    
    with col2:
        st.subheader("📄 Supplier Proposals")
        proposal_files = st.file_uploader(
            "Upload Supplier Proposals",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple supplier proposal documents"
        )
        
        if proposal_files:
            st.session_state.supplier_proposals = []
            for i, proposal_file in enumerate(proposal_files):
                # Process each proposal file
                if proposal_file.type == "text/plain":
                    content = proposal_file.read().decode("utf-8")
                else:
                    # Handle PDF files
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(proposal_file.read())
                        processor = PDFProcessor()
                        result = processor.extract_text_from_pdf(tmp_file.name)
                        content = result.get('text', '')
                        os.unlink(tmp_file.name)
                
                st.session_state.supplier_proposals.append({
                    'name': proposal_file.name,
                    'content': content
                })
            
            st.success(f"✅ {len(proposal_files)} proposal(s) loaded")
            for i, proposal in enumerate(st.session_state.supplier_proposals):
                st.text(f"• {proposal['name']}: {len(proposal['content'])} characters")


def display_analysis_section(api_key: str):
    """Display the analysis section."""
    st.header("🔍 AI Analysis")
    
    # Check if we have required data
    if not st.session_state.tender_requirements:
        st.warning("⚠️ Please upload tender requirements document first")
        return
    
    if not st.session_state.supplier_proposals:
        st.warning("⚠️ Please upload at least one supplier proposal")
        return
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
        return
    
    if not validate_weights(st.session_state.evaluation_weights):
        st.warning("⚠️ Please adjust evaluation weights to total 100%")
        return
    
    # Analysis button
    if st.button("🚀 Start AI Analysis", type="primary"):
        with st.spinner("🤖 AI is analyzing proposals... This may take a few minutes."):
            try:
                # Initialize analyzer
                analyzer = ProposalAnalyzer(api_key=api_key)
                
                # Analyze each proposal
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, proposal in enumerate(st.session_state.supplier_proposals):
                    status_text.text(f"Analyzing {proposal['name']}... ({i+1}/{len(st.session_state.supplier_proposals)})")
                    
                    result = analyzer.analyze_proposal(
                        proposal_text=proposal['content'],
                        tender_requirements=st.session_state.tender_requirements,
                        supplier_name=proposal['name']
                    )
                    
                    results.append(result)
                    progress_bar.progress((i + 1) / len(st.session_state.supplier_proposals))
                    time.sleep(1)  # Brief pause between analyses
                
                # Score and rank suppliers
                status_text.text("Calculating scores and ranking suppliers...")
                scorer = ProposalScorer()
                ranked_suppliers = scorer.rank_suppliers(results, st.session_state.evaluation_weights)
                
                st.session_state.analysis_results = ranked_suppliers
                status_text.text("✅ Analysis complete!")
                
                st.success("🎉 Analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.error("Please check your API key and try again.")


def display_results():
    """Display analysis results."""
    if not st.session_state.analysis_results:
        return
    
    st.header("📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Suppliers", len(st.session_state.analysis_results))
    
    with col2:
        top_score = st.session_state.analysis_results[0]['weighted_score']
        st.metric("Top Score", f"{top_score:.1f}")
    
    with col3:
        avg_score = sum(s['weighted_score'] for s in st.session_state.analysis_results) / len(st.session_state.analysis_results)
        st.metric("Average Score", f"{avg_score:.1f}")
    
    with col4:
        score_range = max(s['weighted_score'] for s in st.session_state.analysis_results) - min(s['weighted_score'] for s in st.session_state.analysis_results)
        st.metric("Score Range", f"{score_range:.1f}")
    
    # Results table
    st.subheader("🏆 Supplier Rankings")
    
    # Prepare data for display
    display_data = []
    for supplier in st.session_state.analysis_results:
        criteria_scores = supplier.get('criteria_scores', {})
        display_data.append({
            'Rank': supplier.get('rank', 0),
            'Supplier': supplier.get('supplier_name', 'Unknown'),
            'Final Score': f"{supplier.get('weighted_score', 0):.1f}",
            'Technical': criteria_scores.get('technical_compliance', {}).get('score', 0),
            'Price': criteria_scores.get('price_competitiveness', {}).get('score', 0),
            'Experience': criteria_scores.get('company_experience', {}).get('score', 0),
            'Timeline': criteria_scores.get('timeline_feasibility', {}).get('score', 0),
            'Risk': criteria_scores.get('risk_assessment', {}).get('score', 0)
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)
    
    # Detailed results
    st.subheader("📋 Detailed Analysis")
    
    for supplier in st.session_state.analysis_results:
        with st.expander(f"#{supplier.get('rank', 0)} - {supplier.get('supplier_name', 'Unknown')} (Score: {supplier.get('weighted_score', 0):.1f})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Overall Summary:**")
                st.write(supplier.get('overall_summary', 'N/A'))
                
                st.write("**Recommendations:**")
                st.write(supplier.get('recommendations', 'N/A'))
            
            with col2:
                st.write("**Key Strengths:**")
                strengths = supplier.get('key_strengths', [])
                if strengths:
                    for strength in strengths:
                        st.write(f"• {strength}")
                else:
                    st.write("None identified")
                
                st.write("**Red Flags:**")
                red_flags = supplier.get('red_flags', [])
                if red_flags:
                    for flag in red_flags:
                        st.write(f"⚠️ {flag}")
                else:
                    st.write("None identified")
            
            # Criteria breakdown
            st.write("**Detailed Criteria Scores:**")
            criteria_scores = supplier.get('criteria_scores', {})
            
            for criterion, data in criteria_scores.items():
                if isinstance(data, dict):
                    criterion_name = criterion.replace('_', ' ').title()
                    score = data.get('score', 0)
                    justification = data.get('justification', 'N/A')
                    
                    st.write(f"**{criterion_name}:** {score}/100")
                    st.write(f"*{justification}*")
                    
                    evidence = data.get('evidence', [])
                    if evidence:
                        st.write("Evidence:")
                        for item in evidence:
                            st.write(f"• {item}")
                    st.write("---")


def display_export_section():
    """Display export options."""
    if not st.session_state.analysis_results:
        return
    
    st.header("📤 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to Excel", type="secondary"):
            try:
                exporter = ResultsExporter()
                scorer = ProposalScorer()
                
                # Generate summary statistics
                stats = scorer.generate_summary_statistics(st.session_state.analysis_results)
                
                # Export to Excel
                filename = exporter.export_to_excel(
                    st.session_state.analysis_results,
                    stats,
                    st.session_state.evaluation_weights
                )
                
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=f.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.success("✅ Excel file generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    with col2:
        if st.button("📄 Export to JSON", type="secondary"):
            try:
                exporter = ResultsExporter()
                scorer = ProposalScorer()
                
                # Generate summary statistics
                stats = scorer.generate_summary_statistics(st.session_state.analysis_results)
                
                # Export to JSON
                filename = exporter.export_to_json(
                    st.session_state.analysis_results,
                    stats,
                    st.session_state.evaluation_weights
                )
                
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download JSON File",
                        data=f.read(),
                        file_name=filename,
                        mime="application/json"
                    )
                
                st.success("✅ JSON file generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Display sidebar
    api_key = display_sidebar()
    
    # Main content
    display_file_upload()
    display_analysis_section(api_key)
    display_results()
    display_export_section()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>JESA Tender Evaluation System | Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
