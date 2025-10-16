# 🚀 JESA Tender Evaluation System - Deployment Guide

## 📋 **Overview**

This guide provides step-by-step instructions for deploying the JESA Tender Evaluation System in various environments, from local development to production deployment.

---

## 🏠 **Local Deployment**

### **Prerequisites**

#### **System Requirements**
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **Python**: Version 3.9 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Required for OpenAI API access

#### **Required Software**
- Python 3.9+
- Git
- OpenAI API account
- Google account (for Colab version)

### **Installation Steps**

#### **1. Clone the Repository**
```bash
git clone https://github.com/Kazaz-Mohammed/JESA_SUPPLIERS_MODEL.git
cd JESA_SUPPLIERS_MODEL
```

#### **2. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your API key
# OPENAI_API_KEY="your_api_key_here"
# OPENAI_MODEL="gpt-4-turbo-preview"
```

#### **5. Test Installation**
```bash
python test_app_components.py
```

#### **6. Start the Application**
```bash
streamlit run app.py
```

Open: `http://localhost:8501`

---

## ☁️ **Cloud Deployment Options**

### **Option 1: Streamlit Cloud (Recommended)**

#### **Advantages**
- Free hosting for public repositories
- Automatic deployment from GitHub
- Built-in Streamlit integration
- Easy updates via Git push

#### **Deployment Steps**
1. **Prepare Repository**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `JESA_SUPPLIERS_MODEL`
   - Main file path: `app.py`
   - Branch: `main`

3. **Configure Secrets**
   - In Streamlit Cloud dashboard
   - Go to "Settings" → "Secrets"
   - Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your_api_key_here"
   OPENAI_MODEL = "gpt-4-turbo-preview"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait for deployment to complete
   - Access your app at the provided URL

#### **Post-Deployment**
- Test all functionality
- Verify API key is working
- Check file upload capabilities
- Test with sample data

### **Option 2: Heroku**

#### **Prerequisites**
- Heroku account
- Heroku CLI installed

#### **Deployment Steps**
1. **Create Heroku App**
   ```bash
   heroku create jesa-tender-evaluation
   ```

2. **Create Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

3. **Configure Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY="your_api_key_here"
   heroku config:set OPENAI_MODEL="gpt-4-turbo-preview"
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

### **Option 3: AWS EC2**

#### **Prerequisites**
- AWS account
- EC2 instance (t3.medium or larger recommended)

#### **Deployment Steps**
1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Instance type: t3.medium or larger
   - Configure security group for port 8501

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install -r requirements.txt
   ```

4. **Clone and Run**
   ```bash
   git clone https://github.com/Kazaz-Mohammed/JESA_SUPPLIERS_MODEL.git
   cd JESA_SUPPLIERS_MODEL
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

5. **Access Application**
   - Open browser to: `http://your-instance-ip:8501`

### **Option 4: Docker Deployment**

#### **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

#### **Build and Run**
```bash
docker build -t jesa-tender-evaluation .
docker run -p 8501:8501 -e OPENAI_API_KEY="your_key" jesa-tender-evaluation
```

---

## 🔧 **Production Configuration**

### **Security Considerations**

#### **API Key Management**
- Use environment variables for API keys
- Never commit API keys to version control
- Rotate API keys regularly
- Use different keys for different environments

#### **Access Control**
- Implement authentication if needed
- Use HTTPS in production
- Configure CORS policies
- Set up rate limiting

#### **Data Privacy**
- Ensure uploaded documents are not stored permanently
- Implement data retention policies
- Use secure file handling
- Consider data encryption

### **Performance Optimization**

#### **Caching**
```python
# Add to app.py for better performance
@st.cache_data
def load_sample_data():
    # Cache expensive operations
    pass
```

#### **Resource Management**
- Monitor memory usage
- Implement file size limits
- Add timeout handling
- Use connection pooling

#### **Scaling**
- Use load balancers for multiple instances
- Implement horizontal scaling
- Monitor resource utilization
- Set up auto-scaling policies

---

## 📊 **Monitoring and Maintenance**

### **Health Checks**
```python
# Add to app.py
@st.cache_data(ttl=300)  # Cache for 5 minutes
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### **Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### **Error Monitoring**
- Set up error tracking (Sentry, LogRocket)
- Monitor API usage and costs
- Track user interactions
- Set up alerts for failures

---

## 🔄 **Update and Maintenance**

### **Regular Updates**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
# (Method depends on deployment)
```

### **Backup Strategy**
- Regular database backups (if applicable)
- Configuration file backups
- API key rotation schedule
- Document retention policies

### **Version Control**
- Tag releases: `git tag v1.0.0`
- Document changes in CHANGELOG.md
- Maintain backward compatibility
- Test updates in staging environment

---

## 🧪 **Testing Deployment**

### **Pre-Deployment Checklist**
- [ ] All tests pass locally
- [ ] Environment variables configured
- [ ] API keys are valid
- [ ] Sample data works correctly
- [ ] Error handling is robust
- [ ] Performance is acceptable

### **Post-Deployment Testing**
- [ ] Application starts successfully
- [ ] File uploads work
- [ ] Analysis completes successfully
- [ ] Results are displayed correctly
- [ ] Export functionality works
- [ ] Error messages are clear

### **Load Testing**
```bash
# Install artillery for load testing
npm install -g artillery

# Create load test configuration
artillery quick --count 10 --num 5 http://localhost:8501
```

---

## 🆘 **Troubleshooting**

### **Common Deployment Issues**

#### **Port Already in Use**
```bash
# Find process using port 8501
netstat -tulpn | grep :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

#### **Import Errors**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **API Key Issues**
- Verify key is correctly set
- Check API key permissions
- Ensure sufficient credits
- Test API key separately

#### **Memory Issues**
- Increase available memory
- Optimize file processing
- Implement chunking for large files
- Add memory monitoring

### **Performance Issues**
- Check server resources
- Monitor API response times
- Optimize document processing
- Implement caching

---

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- Use load balancer (nginx, HAProxy)
- Deploy multiple app instances
- Implement session management
- Use shared storage for files

### **Vertical Scaling**
- Increase server resources
- Optimize application code
- Use faster storage (SSD)
- Implement database optimization

### **Microservices Architecture**
- Split into separate services
- Use API gateway
- Implement service discovery
- Add monitoring and logging

---

## 🎯 **Best Practices**

### **Development**
- Use version control (Git)
- Implement CI/CD pipelines
- Write comprehensive tests
- Document all changes

### **Security**
- Keep dependencies updated
- Use secure coding practices
- Implement input validation
- Regular security audits

### **Performance**
- Monitor resource usage
- Implement caching strategies
- Optimize database queries
- Use CDN for static assets

### **Maintenance**
- Regular updates and patches
- Monitor system health
- Backup critical data
- Plan for disaster recovery

---

*This deployment guide is part of the JESA Tender Evaluation System. For additional support, please refer to the project documentation or create an issue on GitHub.*
