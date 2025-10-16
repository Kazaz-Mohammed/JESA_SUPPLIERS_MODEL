# 🔧 JESA Tender Evaluation System - Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

This guide helps you resolve common problems when using the JESA Tender Evaluation System.

---

## 📱 **Application Issues**

### **App Won't Start**

#### **Problem**: Streamlit app fails to launch
```
Error: Port 8501 is already in use
```

#### **Solutions**:
1. **Kill existing process**:
   ```bash
   # Windows
   netstat -ano | findstr :8501
   taskkill /PID <PID_NUMBER> /F
   
   # macOS/Linux
   lsof -ti:8501 | xargs kill -9
   ```

2. **Use different port**:
   ```bash
   streamlit run app.py --server.port 8502
   ```

3. **Restart computer** (if processes persist)

#### **Problem**: Module import errors
```
ModuleNotFoundError: No module named 'streamlit'
```

#### **Solutions**:
1. **Check virtual environment**:
   ```bash
   # Activate virtual environment
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python path**:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### **App Loads But Shows Errors**

#### **Problem**: Import errors in app
```
ImportError: cannot import name 'ProposalAnalyzer'
```

#### **Solutions**:
1. **Check file structure**:
   ```
   JESA_SUPPLIERS_MODEL/
   ├── app.py
   ├── utils/
   │   ├── __init__.py
   │   ├── analyzer.py
   │   ├── pdf_processor.py
   │   └── scorer.py
   ```

2. **Verify imports in app.py**:
   ```python
   from utils.analyzer import ProposalAnalyzer
   from utils.scorer import ProposalScorer, ResultsExporter
   from utils.pdf_processor import PDFProcessor
   ```

3. **Run component test**:
   ```bash
   python test_app_components.py
   ```

---

## 🔑 **API Key Issues**

### **Invalid API Key**

#### **Problem**: API key not working
```
Error: Invalid API key provided
```

#### **Solutions**:
1. **Verify API key format**:
   - Should start with `sk-`
   - No spaces or extra characters
   - Copy-paste from OpenAI dashboard

2. **Check API key permissions**:
   - Go to: https://platform.openai.com/api-keys
   - Verify key is active
   - Check usage limits

3. **Test API key separately**:
   ```python
   import openai
   client = openai.OpenAI(api_key="your_key")
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response)
   ```

### **API Rate Limits**

#### **Problem**: Too many requests
```
Error: Rate limit exceeded
```

#### **Solutions**:
1. **Wait and retry**:
   - Rate limits reset every minute
   - Wait 60 seconds before retrying

2. **Upgrade API plan**:
   - Go to OpenAI billing settings
   - Increase rate limits
   - Consider GPT-4 if using GPT-3.5

3. **Optimize requests**:
   - Reduce document size
   - Use shorter prompts
   - Batch multiple analyses

### **Insufficient Credits**

#### **Problem**: Billing quota exceeded
```
Error: You exceeded your current quota
```

#### **Solutions**:
1. **Check usage dashboard**:
   - Visit: https://platform.openai.com/usage
   - Monitor current usage
   - Set up usage alerts

2. **Add payment method**:
   - Go to billing settings
   - Add credit card
   - Set spending limits

3. **Use Colab version**:
   - Switch to Google Colab version
   - Free local LLM analysis
   - No API costs

---

## 📄 **File Upload Issues**

### **File Upload Fails**

#### **Problem**: Cannot upload files
```
Error: File upload failed
```

#### **Solutions**:
1. **Check file format**:
   - Supported: PDF, TXT
   - Maximum size: 50MB
   - Avoid scanned images

2. **Verify file integrity**:
   - Try opening file locally
   - Check for corruption
   - Convert to different format

3. **Clear browser cache**:
   - Clear browser data
   - Try different browser
   - Disable browser extensions

### **PDF Processing Errors**

#### **Problem**: PDF text extraction fails
```
Error: Unable to extract text from PDF
```

#### **Solutions**:
1. **Convert PDF to text**:
   - Use online PDF converters
   - Save as .txt file
   - Upload text version

2. **Check PDF properties**:
   - Ensure PDF is searchable
   - Avoid image-only PDFs
   - Try different PDF reader

3. **Use alternative format**:
   - Convert to Word document
   - Save as plain text
   - Use OCR tools if needed

### **Empty Documents**

#### **Problem**: No text extracted
```
Warning: Document appears to be empty
```

#### **Solutions**:
1. **Check document content**:
   - Ensure document has text
   - Verify not password-protected
   - Check for hidden text

2. **Try different extraction**:
   - Use different PDF processor
   - Copy-paste text manually
   - Use online text extractors

---

## 🔍 **Analysis Issues**

### **Analysis Fails**

#### **Problem**: Analysis returns errors
```
Error: Analysis failed with error
```

#### **Solutions**:
1. **Check document quality**:
   - Ensure sufficient content
   - Verify text is readable
   - Check for special characters

2. **Reduce document size**:
   - Truncate very long documents
   - Focus on key sections
   - Remove unnecessary content

3. **Check API response**:
   - Verify API key is working
   - Check internet connection
   - Try with sample data

### **Poor Analysis Quality**

#### **Problem**: Analysis results don't make sense
```
Issue: Generic or incorrect analysis
```

#### **Solutions**:
1. **Improve document structure**:
   - Use clear headings
   - Include specific details
   - Provide concrete examples

2. **Adjust weights**:
   - Modify evaluation criteria
   - Test different configurations
   - Validate with manual review

3. **Use better prompts**:
   - Provide more context
   - Include evaluation examples
   - Specify output format

### **Slow Analysis**

#### **Problem**: Analysis takes too long
```
Issue: Analysis running for >5 minutes
```

#### **Solutions**:
1. **Reduce document size**:
   - Truncate long documents
   - Focus on key sections
   - Remove redundant content

2. **Check API status**:
   - Visit: https://status.openai.com
   - Wait for service restoration
   - Try different model

3. **Optimize configuration**:
   - Use faster model (GPT-3.5)
   - Reduce max tokens
   - Simplify prompts

---

## 📊 **Results Issues**

### **Incorrect Rankings**

#### **Problem**: Suppliers ranked incorrectly
```
Issue: Rankings don't match expectations
```

#### **Solutions**:
1. **Check weight configuration**:
   - Verify weights sum to 100%
   - Adjust based on priorities
   - Test different configurations

2. **Review analysis details**:
   - Check individual scores
   - Verify justifications
   - Compare with manual review

3. **Validate input data**:
   - Ensure complete proposals
   - Check document quality
   - Verify requirements clarity

### **Missing Data**

#### **Problem**: Incomplete analysis results
```
Issue: Some criteria not evaluated
```

#### **Solutions**:
1. **Check document content**:
   - Ensure all sections present
   - Verify information completeness
   - Add missing details

2. **Improve prompts**:
   - Make requirements clearer
   - Provide evaluation examples
   - Specify output format

3. **Manual review**:
   - Cross-check AI results
   - Fill in missing information
   - Validate against requirements

### **Export Issues**

#### **Problem**: Cannot download results
```
Error: Export failed
```

#### **Solutions**:
1. **Check file permissions**:
   - Ensure write access
   - Try different location
   - Check disk space

2. **Verify data integrity**:
   - Ensure analysis completed
   - Check for errors in results
   - Try with sample data

3. **Use alternative export**:
   - Try JSON export
   - Copy results manually
   - Use different browser

---

## 🖥️ **Google Colab Issues**

### **GPU Not Available**

#### **Problem**: No GPU detected
```
Warning: GPU not available, using CPU
```

#### **Solutions**:
1. **Enable GPU**:
   - Runtime → Change runtime type
   - Select T4 GPU
   - Save and restart

2. **Check availability**:
   - Colab free tier has limits
   - Try at different times
   - Consider Pro subscription

3. **Use CPU version**:
   - Modify code for CPU
   - Expect slower performance
   - Reduce model size

### **Memory Errors**

#### **Problem**: Out of memory
```
RuntimeError: CUDA out of memory
```

#### **Solutions**:
1. **Restart runtime**:
   - Runtime → Restart runtime
   - Re-run all cells
   - Clear memory

2. **Reduce model size**:
   - Use smaller model
   - Reduce batch size
   - Optimize memory usage

3. **Optimize code**:
   - Clear unused variables
   - Use garbage collection
   - Process smaller chunks

### **Model Loading Fails**

#### **Problem**: Cannot load model
```
Error: Failed to load model
```

#### **Solutions**:
1. **Check internet connection**:
   - Ensure stable connection
   - Try different network
   - Wait and retry

2. **Verify model availability**:
   - Check HuggingFace status
   - Try alternative model
   - Use cached version

3. **Clear cache**:
   - Delete cached models
   - Restart runtime
   - Re-download model

---

## 🔧 **System Issues**

### **Performance Problems**

#### **Problem**: System running slowly
```
Issue: App or analysis very slow
```

#### **Solutions**:
1. **Check system resources**:
   - Monitor CPU/Memory usage
   - Close unnecessary programs
   - Restart if needed

2. **Optimize configuration**:
   - Reduce document size
   - Use faster models
   - Implement caching

3. **Upgrade hardware**:
   - Add more RAM
   - Use faster CPU
   - Consider SSD storage

### **Browser Issues**

#### **Problem**: App not displaying correctly
```
Issue: Layout or functionality problems
```

#### **Solutions**:
1. **Clear browser cache**:
   - Clear browsing data
   - Disable extensions
   - Try incognito mode

2. **Update browser**:
   - Install latest version
   - Enable JavaScript
   - Check compatibility

3. **Try different browser**:
   - Chrome (recommended)
   - Firefox
   - Edge

### **Network Issues**

#### **Problem**: Connection problems
```
Error: Network timeout
```

#### **Solutions**:
1. **Check internet connection**:
   - Test other websites
   - Restart router
   - Try different network

2. **Configure firewall**:
   - Allow Streamlit ports
   - Check antivirus settings
   - Configure proxy if needed

3. **Use local version**:
   - Run app locally
   - Avoid network dependencies
   - Use offline mode

---

## 📞 **Getting Help**

### **Self-Help Resources**
1. **Documentation**: README.md, USER_MANUAL.md
2. **Test Suite**: Run `python test_app_components.py`
3. **Sample Data**: Use provided test files
4. **Logs**: Check console output for errors

### **Community Support**
1. **GitHub Issues**: Create issue on repository
2. **Documentation**: Check project wiki
3. **Examples**: Review sample implementations
4. **Forums**: Streamlit and OpenAI communities

### **Professional Support**
1. **Technical Support**: Contact development team
2. **Training**: Request system training
3. **Customization**: Discuss specific requirements
4. **Consulting**: Get expert assistance

---

## 📋 **Emergency Procedures**

### **System Recovery**
1. **Backup Data**: Save current results
2. **Restart Services**: Restart app and dependencies
3. **Restore Configuration**: Use backup settings
4. **Test Functionality**: Verify system works

### **Data Recovery**
1. **Check Exports**: Look for saved results
2. **Restore from Backup**: Use previous versions
3. **Re-run Analysis**: Process documents again
4. **Manual Entry**: Enter results manually

### **Rollback Procedures**
1. **Git Reset**: Return to previous version
2. **Restore Environment**: Use backup configuration
3. **Reinstall Dependencies**: Fresh installation
4. **Verify System**: Test all functionality

---

*This troubleshooting guide is part of the JESA Tender Evaluation System. For additional support, please refer to the project documentation or create an issue on GitHub.*
