# 🎬 MoneyPrinterTurboPro

**AI-Powered Professional Video Generation Platform**

Transform your ideas into engaging, professional videos with AI-generated content, industry-specific templates, and voice synthesis.

## ✨ **Features**

### 🤖 **AI Content Generation**
- **OpenAI GPT-4 Integration** - Generate professional video scripts
- **Anthropic Claude Support** - Alternative AI content creation
- **Smart Fallback System** - Works even without API keys
- **Multi-language Support** - English, Spanish, French, German, Chinese, Japanese

### 🎨 **Professional Video Templates**
- **Business Professional** - Corporate-style videos with clean design
- **Educational** - Learning-focused content with clear visuals
- **Creative** - Artistic videos with dynamic effects
- **Marketing** - Promotional content with conversion elements
- **Social Media** - Platform-optimized square format
- **Corporate** - Enterprise communications and training

### 🎤 **Voice Synthesis**
- **Edge TTS** - Microsoft's high-quality, free text-to-speech
- **Multiple Voices** - Male/Female, different accents
- **Speed Control** - Adjustable narration pace
- **Multi-language Audio** - Generate narration in target language

### 🎬 **Video Generation**
- **Full HD Quality** - 1920x1080 @ 30fps
- **Professional Graphics** - Gradients, animations, overlays
- **AI-Enhanced Content** - Dynamic text and visual elements
- **Multiple Formats** - MP4, AVI, GIF support

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- OpenCV (for video generation)
- FFmpeg (optional, for advanced video processing)

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MoneyPrinterTurboPro.git
cd MoneyPrinterTurboPro
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional)
```bash
cp env.template .env
# Edit .env with your API keys
```

4. **Start the application**
```bash
# Start WebUI
streamlit run webui/main.py

# Or start backend API
python run.py
```

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file based on `env.template`:

```bash
# AI Services
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database
DATABASE_URL=sqlite:///./moneyprinter_pro.db

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### **AI Provider Setup**
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)
- **Edge TTS**: Free, no API key required

## 📱 **Usage**

### **Web Interface**
1. Open your browser to `http://localhost:8501`
2. Navigate to "Video Generator"
3. Enter your video topic
4. Choose style and duration
5. Enable AI content generation
6. Click "Generate AI Video"

### **API Endpoints**
- `GET /` - API status
- `GET /health` - Health check
- `GET /api/v1/status` - Service information

## 🏗️ **Architecture**

```
MoneyPrinterTurboPro/
├── app/                    # Backend services
│   ├── core/              # Core configuration
│   ├── services/          # Business logic
│   ├── api/               # FastAPI endpoints
│   └── webui/             # Streamlit interface
├── webui/                 # Frontend application
│   ├── pages/             # Streamlit pages
│   └── components/        # Reusable components
├── output/                # Generated videos
├── temp/                  # Temporary files
└── logs/                  # Application logs
```

## 🎯 **Use Cases**

### **Business & Marketing**
- Product demonstrations
- Corporate presentations
- Marketing campaigns
- Training videos

### **Education & Training**
- Online courses
- Tutorial videos
- Educational content
- Skill development

### **Content Creation**
- Social media content
- YouTube videos
- Podcast intros
- Brand storytelling

## 🔒 **Security Features**

- **Environment-based configuration** - No hardcoded secrets
- **Input validation** - Sanitized user inputs
- **Rate limiting** - API abuse prevention
- **CORS protection** - Cross-origin security

## 📊 **Performance**

- **Fast video generation** - 15-45 seconds for typical videos
- **Efficient AI processing** - Optimized content generation
- **Memory management** - Automatic cleanup of temporary files
- **Scalable architecture** - Ready for production deployment

## 🚀 **Deployment**

### **Local Development**
```bash
python run.py
```

### **Streamlit Cloud**
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy automatically

### **Docker Deployment**
```bash
docker build -t moneyprinter-pro .
docker run -p 8000:8000 moneyprinter-pro
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI** - GPT-4 API for content generation
- **Anthropic** - Claude API for alternative AI
- **Microsoft** - Edge TTS for voice synthesis
- **OpenCV** - Computer vision and video processing
- **Streamlit** - Web application framework

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/yourusername/MoneyPrinterTurboPro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/MoneyPrinterTurboPro/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/MoneyPrinterTurboPro/wiki)

## 🔮 **Roadmap**

- [ ] **Advanced Video Effects** - More transitions and animations
- [ ] **Batch Processing** - Generate multiple videos simultaneously
- [ ] **Cloud Storage** - AWS S3, Google Cloud integration
- [ ] **Analytics Dashboard** - Video performance metrics
- [ ] **Team Collaboration** - Multi-user support
- [ ] **API Rate Limiting** - Production-ready throttling
- [ ] **Webhook Support** - External integrations
- [ ] **Mobile App** - iOS and Android applications

---

**Made with ❤️ by the MoneyPrinterTurboPro Team**

*Transform your ideas into professional videos with the power of AI!*
