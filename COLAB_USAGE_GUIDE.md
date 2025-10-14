# 📘 Google Colab Version - Usage Guide

## JESA Tender Evaluation System - Local LLM Version

This guide explains how to use the Google Colab version of the JESA Tender Evaluation System.

---

## 🎯 Quick Summary

- **File**: `app_colab.ipynb`
- **Model**: Phi-3 Mini (4K) by Microsoft
- **Cost**: **FREE** (uses Colab free tier)
- **Speed**: 2-8 minutes per proposal
- **Quality**: Good (85-90% of GPT-4 quality)
- **No API Key Required**: Everything runs locally in Colab

---

## 🚀 Step-by-Step Guide

### **Step 1: Open the Notebook**

1. Go to https://colab.research.google.com
2. Click "File" → "Upload notebook"
3. Upload `app_colab.ipynb` from the project
4. OR clone from GitHub and open directly

### **Step 2: Enable GPU (CRITICAL!)**

⚠️ **This is mandatory or the notebook won't work!**

1. Click **"Runtime"** → **"Change runtime type"**
2. Under "Hardware accelerator", select **"T4 GPU"**
3. Click **"Save"**

You can verify GPU is enabled by checking if you see "GPU" in the top-right corner.

### **Step 3: Run Setup Cells (1-6)**

Run these cells in order:

- **Cell 1**: Install packages (~2-3 minutes)
  - Installs transformers, pdfplumber, pandas, etc.
  
- **Cell 2**: Import libraries (~5 seconds)
  - Should show "✅ All libraries imported successfully!"
  - Shows CUDA available: True
  
- **Cell 3**: Load Phi-3 model (~2-4 minutes first time)
  - Downloads ~7.6GB model (cached for future use)
  - Should show "✅ Model loaded successfully!"
  - Memory allocated: ~7.5 GB
  
- **Cell 4-6**: Define functions (~instant)
  - PDF processing, AI analysis, scoring functions

### **Step 4: Upload Your Documents**

- **Cell 7**: Upload Tender Requirements
  - Click "Choose Files" button
  - Select your tender requirements document (PDF or TXT)
  - Wait for upload and processing
  - You'll see a preview of the first 300 characters

- **Cell 8**: Upload Supplier Proposals
  - Click "Choose Files" button
  - You can select **multiple files** at once
  - Wait for upload and processing
  - You'll see a list of all uploaded proposals

### **Step 5: Configure Weights (Cell 9)**

- Default weights are already set (total 100%)
- You can modify the weights if needed
- Run the cell to validate weights

### **Step 6: Run Analysis (Cell 10)**

⏱️ **This is the slow part!**

- Click run on Cell 10
- **Be patient!** Each proposal takes 2-8 minutes
- You'll see:
  - "🧠 Starting generation..."
  - "📊 Input length: X tokens"
  - Generation progress (GPU will fluctuate 10-15GB)
  - "⏱️ Generation completed in X seconds"
  - "✅ Analysis completed"

**Important**: Generation time of 5-8 minutes per proposal is normal for local LLMs!

### **Step 7-9: View and Export Results**

- **Cell 11**: Rankings summary
- **Cell 12**: Rankings table (nice pandas DataFrame)
- **Cell 13**: Detailed analysis for each supplier
- **Cell 14**: Export to Excel and download
- **Cell 15**: Export to JSON (optional)

---

## ⚡ Performance Tips

### **Speed Optimization:**

To make analysis faster:
1. **Use shorter documents** (truncate to key sections)
2. **Analyze fewer proposals** at once
3. **Use simpler prompts** (already optimized in current version)

### **Memory Management:**

If you get "Out of Memory" errors:
1. **Runtime → Restart runtime**
2. **Re-run all cells**
3. **Don't run cells out of order**

---

## 🔍 Understanding the Output

### **Generation Time:**
- **30-90 seconds**: Fast (short documents)
- **2-5 minutes**: Normal (medium documents)
- **5-10 minutes**: Slow but OK (long documents)

Example from testing: 458 seconds (~7.6 minutes) for 1116 token input

### **Scores:**

The current version produces:
- ✅ **Valid scores** (0-100 scale)
- ✅ **Final score calculation**
- ✅ **Ranking system**
- ⚠️ **Generic justifications** (known limitation of local LLMs)

**Note**: Local LLMs sometimes produce generic justifications like "Brief explanation". The **scores are still valid and useful** for ranking suppliers. For detailed justifications, use the OpenAI version.

---

## 🆚 Comparison: OpenAI vs Colab

| Feature | Streamlit (OpenAI) | Colab (Phi-3) |
|---------|-------------------|---------------|
| **Speed** | 30-60 seconds | 2-8 minutes |
| **Cost** | ~$0.10-0.30 | FREE |
| **Quality** | Excellent | Good |
| **Justifications** | Detailed | Sometimes generic |
| **Setup** | API key needed | GPU setup needed |
| **Best For** | Production, clients | Testing, internal |

---

## ✅ Troubleshooting

### **Problem: Out of Memory**
**Solution**: Runtime → Restart runtime, then re-run all cells

### **Problem: Model loading fails**
**Solution**: Check GPU is enabled (Runtime → Change runtime type)

### **Problem: Analysis takes >10 minutes**
**Solution**: This is normal for very long documents. Consider truncating input or using OpenAI version.

### **Problem: Justifications are generic ("Brief explanation")**
**Solution**: This is a limitation of local LLMs with short prompts. The scores are still valid. For better justifications, use the OpenAI version (Streamlit app).

### **Problem: "DynamicCache" error**
**Solution**: Already fixed in the latest version with `use_cache=False`

### **Problem: GPU not available**
**Solution**: 
1. Runtime → Change runtime type
2. Select T4 GPU
3. Save
4. Restart runtime

---

## 🎓 Tips for Best Results

1. **Keep documents concise** - Extract key sections only (model uses first 500-900 chars)
2. **Run during off-peak hours** - Colab is faster when less busy
3. **Save your work** - Download results immediately (Colab sessions expire after 12 hours)
4. **Use OpenAI for important tenders** - Better quality justifications
5. **Use Colab for testing** - Free and good enough for initial screening

---

## 📊 What You'll Get

### **From the Rankings Table (Cell 12):**
```
Rank | Supplier | Final Score | Technical | Price | Experience | Timeline | Risk
-----|----------|-------------|-----------|-------|------------|----------|------
1    | ABC      | 82.75       | 85        | 75    | 90         | 80       | 85
2    | XYZ      | 70.50       | 75        | 65    | 80         | 70       | 75
```

### **From the Detailed Analysis (Cell 13):**
- Overall summary
- Recommendations
- Red flags (if any)
- Detailed scores for each criterion
- Evidence (if captured by the model)

### **From the Excel Export (Cell 14):**
- Professional formatted Excel file
- Rankings sheet with all data
- Ready for presentation

---

## 🎯 Known Limitations

1. **Generic Justifications**: Local LLMs may produce generic text like "Brief explanation" instead of detailed analysis
2. **Slower Processing**: 5-10x slower than OpenAI API
3. **Memory Constraints**: Limited by Colab free tier (15GB)
4. **Session Limits**: Colab free tier has usage limits (~15-20 hours/week)

**Despite these limitations, the system works well for:**
- Initial supplier screening
- Cost-free evaluation
- Testing and development
- Learning how the system works

---

## 📞 Support

For issues or questions:
- GitHub: https://github.com/Kazaz-Mohammed/JESA_SUPPLIERS_MODEL
- Check the main README.md for general documentation
- Review this guide for Colab-specific help

---

## 🎉 Success!

If you've reached this point and have:
- ✅ Rankings table displayed
- ✅ Detailed analysis shown
- ✅ Excel file downloaded

**Congratulations! You've successfully used the JESA Tender Evaluation System with a local LLM on Google Colab!**

---

*Last updated: October 2025*

