# JESA Tender Evaluation System

An AI-powered system for automatically analyzing and scoring supplier proposals in construction tenders.

## 🎯 Overview

The JESA Tender Evaluation System uses artificial intelligence to analyze supplier proposals against tender requirements, providing objective scoring and ranking of suppliers. The system evaluates proposals on five key criteria:

- **Technical Compliance** (30%): Does the proposal meet all technical specifications?
- **Price Competitiveness** (25%): Is the pricing reasonable and competitive?
- **Company Experience** (20%): Past projects, references, and qualifications
- **Timeline Feasibility** (15%): Can they deliver on time?
- **Risk Assessment** (10%): Overall risk level assessment

## 🚀 Features

- **Dual Implementation**: OpenAI API version and Google Colab local LLM version
- **PDF Processing**: Robust text extraction from PDF documents
- **AI Analysis**: Intelligent evaluation using GPT-4 or local Llama models
- **Flexible Weighting**: Customizable evaluation criteria weights
- **Comprehensive Reporting**: Detailed analysis with evidence-based scoring
- **Export Capabilities**: Excel export with formatted results
- **Web Interface**: User-friendly Streamlit application

## 📁 Project Structure

```
tender-evaluation/
├── app.py                    # Main Streamlit app (OpenAI version)
├── app_colab.ipynb          # Google Colab notebook (LLM version)
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py     # PDF text extraction
│   ├── analyzer.py          # Core analysis logic
│   ├── scorer.py           # Scoring and ranking
│   └── prompt_templates.py # LLM prompt engineering
├── data/
│   ├── sample_tender.txt   # Sample tender requirements
│   ├── sample_proposal_1.txt # Sample supplier proposals
│   └── sample_proposal_2.txt
├── prompts/
│   └── evaluation_prompt.txt # Main prompt template
├── requirements.txt        # Python dependencies
├── requirements_colab.txt  # Colab-specific requirements
├── env.example            # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (for API version)
- Google account (for Colab version)

### Local Installation (OpenAI Version)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kazaz-Mohammed/JESA_SUPPLIERS_MODEL.git
   cd JESA_SUPPLIERS_MODEL
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env file and add your OpenAI API key
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### Google Colab Installation (Local LLM Version)

1. **Open the notebook:**
   - Upload `app_colab.ipynb` to Google Colab
   - Or clone the repository in Colab

2. **Run the installation cell:**
   - The notebook includes all necessary installation commands
   - No API keys required (uses local models)

3. **Follow the notebook instructions:**
   - Each cell is well-documented
   - Upload files directly in Colab interface

## 🔑 Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## 📖 Usage

### Streamlit Web Interface

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Upload documents:**
   - Upload tender requirements document (PDF or text)
   - Upload supplier proposals (multiple PDFs)

3. **Configure evaluation:**
   - Adjust weights for each criterion (must sum to 100%)
   - Enter your OpenAI API key

4. **Analyze proposals:**
   - Click "Analyze Proposals" button
   - Wait for AI analysis to complete

5. **Review results:**
   - View ranked supplier list
   - Expand details for each supplier
   - Export results to Excel

### Google Colab Interface

1. **Open the notebook** in Google Colab
2. **Run installation cells** to set up the environment
3. **Upload files** using Colab's file upload interface
4. **Configure weights** and run analysis
5. **Download results** as Excel file

## 🧪 Testing

The system includes sample data for testing:

- `data/sample_tender.txt`: Sample tender requirements
- `data/sample_proposal_1.txt`: High-quality supplier proposal
- `data/sample_proposal_2.txt`: Moderate-quality supplier proposal

### Running Tests

```bash
# Test PDF processing
python utils/pdf_processor.py

# Test the full system with sample data
streamlit run app.py
# Then upload the sample files in the interface
```

## 📊 Output Format

The system provides detailed analysis for each supplier:

```json
{
  "supplier_name": "Supplier Company Name",
  "criteria_scores": {
    "technical_compliance": {
      "score": 85,
      "justification": "Detailed explanation...",
      "evidence": ["Quote from proposal..."]
    }
    // ... other criteria
  },
  "final_score": 80.0,
  "overall_summary": "Overall assessment...",
  "red_flags": ["Issues identified..."],
  "recommendations": "Specific recommendations..."
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
MAX_FILE_SIZE_MB=50
MAX_SUPPLIERS=20
DEFAULT_TECHNICAL_WEIGHT=30
DEFAULT_PRICE_WEIGHT=25
DEFAULT_EXPERIENCE_WEIGHT=20
DEFAULT_TIMELINE_WEIGHT=15
DEFAULT_RISK_WEIGHT=10
```

### Customizing Evaluation Weights

You can adjust the default weights in the `.env` file or use the web interface sliders. Weights must sum to 100%.

## 🚨 Troubleshooting

### Common Issues

1. **PDF Processing Errors:**
   - Ensure PDFs are not password-protected
   - Check file size limits (default: 50MB)
   - Try different PDF formats if extraction fails

2. **OpenAI API Issues:**
   - Verify API key is correct and active
   - Check API usage limits and billing
   - Ensure internet connection is stable

3. **Memory Issues (Colab):**
   - Use smaller models (Llama 3.2 3B instead of 8B)
   - Process fewer documents at once
   - Restart runtime if needed

4. **Streamlit Issues:**
   - Clear browser cache
   - Restart the application
   - Check port availability (default: 8501)

### Getting Help

- Check the logs for detailed error messages
- Ensure all dependencies are properly installed
- Verify file formats and sizes
- Contact support with specific error details

## 🔒 Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive data
- Validate file uploads (PDF only, size limits)
- Implement proper error handling

## 📈 Performance Optimization

### OpenAI API Version
- Use efficient prompting to minimize token usage
- Implement caching for repeated analyses
- Batch processing for multiple documents

### Colab Version
- Optimize for free tier GPU limits
- Use quantization for smaller models
- Implement progress indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation and troubleshooting guide

## 🔄 Version History

- **v1.0.0**: Initial release with OpenAI API and Colab versions
- Basic PDF processing and AI analysis
- Streamlit web interface
- Excel export functionality

## 📚 Documentation

### **📖 User Documentation**
- **[User Manual](USER_MANUAL.md)** - Comprehensive guide for using the system
- **[Google Colab Guide](COLAB_USAGE_GUIDE.md)** - Step-by-step Colab instructions  
- **[Business Guide](BUSINESS_GUIDE.md)** - Business value and implementation strategy

### **🚀 Technical Documentation**
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- **[Test Results](TEST_RESULTS_SUMMARY.md)** - Comprehensive testing analysis

### **📊 Project Documentation**
- **[Phase 6 Testing](TEST_RESULTS_SUMMARY.md)** - Complete testing suite results
- **[Sample Data](data/)** - Test files for system validation

---

**JESA Tender Evaluation System** - Making tender evaluation objective, efficient, and transparent.
