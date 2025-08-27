# 🚀 MoneyPrinterTurboPro Setup Guide

## 🔐 **API Key Configuration**

### **Step 1: Create Your .env File**
```bash
# Copy the template
copy env.template .env

# Edit the .env file with your actual API keys
notepad .env
```

### **Step 2: Configure Your API Keys**

#### **Required API Keys (Choose at least one):**

**OpenAI (Recommended)**
- Get your API key from: https://platform.openai.com/api-keys
- Add to `.env`: `OPENAI_API_KEY=sk-your-actual-key-here`

**Anthropic Claude**
- Get your API key from: https://console.anthropic.com/
- Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-your-actual-key-here`

#### **Optional API Keys:**

**Google API**
- Get your API key from: https://console.cloud.google.com/
- Add to `.env`: `GOOGLE_API_KEY=your-actual-key-here`

**Azure Speech Services**
- Get your key from: https://portal.azure.com/
- Add to `.env`: `AZURE_SPEECH_KEY=your-actual-key-here`

**ElevenLabs Voice**
- Get your API key from: https://elevenlabs.io/
- Add to `.env`: `ELEVENLABS_API_KEY=your-actual-key-here`

### **Step 3: Test Your Configuration**
```bash
python test_config.py
```

### **Step 4: Start the Application**
```bash
# Start WebUI
streamlit run webui/main.py

# Or start backend API
python run.py
```

## 🔒 **Security Notes**

- **NEVER commit your .env file to Git**
- **NEVER share your API keys publicly**
- **Use environment variables in production**
- **Rotate your API keys regularly**

## 🎯 **Minimum Configuration**

For basic functionality, you need at least:
```bash
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=sqlite:///./moneyprinter_pro.db
```

## 🚨 **Troubleshooting**

### **API Key Not Working?**
1. Check if the key is correct
2. Verify the key has sufficient credits
3. Check your internet connection
4. Ensure the key is not expired

### **Configuration Test Fails?**
1. Make sure `.env` file exists
2. Check file permissions
3. Verify no extra spaces in values
4. Restart your terminal after changes

---

**Need Help?** Check the main README.md or create an issue on GitHub.
