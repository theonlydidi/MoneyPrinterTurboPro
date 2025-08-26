# 🚀 MoneyPrinterTurboPro Production Deployment Guide

This guide covers the complete production deployment of the MoneyPrinterTurboPro platform, including all services, monitoring, and scaling considerations.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Detailed Deployment](#detailed-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Scaling & Performance](#scaling--performance)
8. [Security](#security)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 100GB+ SSD storage
- **Network**: Stable internet connection

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **OpenSSL**: For SSL certificate generation

### API Keys Required
- OpenAI API Key
- Anthropic API Key (optional)
- Google API Key (optional)
- Azure Speech Key (optional)
- ElevenLabs API Key (optional)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (443)   │    │   Prometheus    │    │     Grafana     │
│   Reverse Proxy │    │   Monitoring    │    │   Dashboard     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit      │    │   FastAPI       │    │   PostgreSQL    │
│  Frontend       │    │   Backend       │    │   Database      │
│  (Port 8501)    │    │  (Port 8000)    │    │  (Port 5432)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │     Cache       │
                        │   (Port 6379)   │
                        └─────────────────┘
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/theonlydidi/MoneyPrinterTurboPro.git
cd MoneyPrinterTurboPro
```

### 2. Setup Environment
```bash
# Copy environment template
cp env.template .env

# Edit .env file with your API keys and configuration
nano .env
```

### 3. Deploy Platform
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### 4. Access Services
- **WebUI**: https://localhost
- **API**: https://localhost/api
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

## 📚 Detailed Deployment

### Manual Deployment Steps

#### 1. Create Required Directories
```bash
mkdir -p data logs nginx/logs nginx/ssl monitoring/grafana/dashboards monitoring/grafana/datasources database
```

#### 2. Generate SSL Certificate
```bash
# For development (self-signed)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# For production (use Let's Encrypt or your CA)
# Let's Encrypt example:
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

#### 3. Configure Environment Variables
```bash
# Copy and edit environment template
cp env.template .env
nano .env

# Required variables to set:
# - OPENAI_API_KEY
# - SECRET_KEY
# - JWT_SECRET_KEY
# - Database passwords
```

#### 4. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

#### Core Application
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

#### Database
```bash
DATABASE_URL=postgresql://mptp_user:mptp_password@postgres:5432/mptp_db
POSTGRES_DB=mptp_db
POSTGRES_USER=mptp_user
POSTGRES_PASSWORD=mptp_password
```

#### Redis
```bash
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=mptp_redis_password
```

#### API Keys
```bash
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Nginx Configuration
The Nginx configuration includes:
- SSL/TLS termination
- Reverse proxy to backend services
- Rate limiting
- Security headers
- Gzip compression
- WebSocket support for Streamlit

### Database Configuration
PostgreSQL is configured with:
- Connection pooling
- Optimized settings for production
- Automated backups
- Health monitoring

## 📊 Monitoring & Observability

### Prometheus Metrics
- **Application Metrics**: Request rates, response times, error rates
- **System Metrics**: CPU, memory, disk usage
- **Database Metrics**: Connection counts, query performance
- **Custom Metrics**: Video generation stats, AI model performance

### Grafana Dashboards
Pre-configured dashboards for:
- **System Overview**: Overall platform health
- **Application Performance**: API and frontend metrics
- **Database Performance**: PostgreSQL monitoring
- **Video Generation**: Processing statistics and trends

### Logging
- **Structured Logging**: JSON format for easy parsing
- **Log Rotation**: Automatic log file management
- **Centralized Logging**: All services log to shared location

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale backend workers
docker-compose up -d --scale worker=4

# Scale frontend instances
docker-compose up -d --scale frontend=2
```

### Load Balancing
- **Nginx**: Round-robin load balancing
- **Database**: Connection pooling
- **Redis**: Cluster mode support

### Performance Optimization
- **Caching**: Redis for session and data caching
- **CDN**: Static asset delivery
- **Database**: Query optimization and indexing
- **Video Processing**: GPU acceleration support

## 🔒 Security

### Network Security
- **Firewall**: Restrict access to necessary ports only
- **SSL/TLS**: HTTPS enforcement
- **Rate Limiting**: Prevent abuse and DDoS
- **IP Whitelisting**: Restrict access to trusted sources

### Application Security
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Input Validation**: Sanitize all user inputs
- **SQL Injection**: Parameterized queries

### Data Security
- **Encryption**: Data at rest and in transit
- **Backup Encryption**: Secure backup storage
- **Access Logging**: Audit trail for all operations

## 💾 Backup & Recovery

### Database Backups
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U mptp_user mptp_db > "$BACKUP_DIR/backup_$DATE.sql"

# Keep last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### File Storage Backups
- **S3**: Cross-region replication
- **Azure**: Geo-redundant storage
- **Local**: Automated backup to external storage

### Recovery Procedures
1. **Database Recovery**: Restore from latest backup
2. **Application Recovery**: Redeploy containers
3. **Data Recovery**: Restore from cloud storage
4. **Full System Recovery**: Complete platform redeployment

## 🐛 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs [service_name]

# Check resource usage
docker stats

# Verify configuration
docker-compose config
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://mptp_user:mptp_password@postgres:5432/mptp_db')
print('Connected successfully')
conn.close()
"
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor database performance
docker-compose exec postgres psql -U mptp_user -d mptp_db -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"
```

### Health Checks
```bash
# Check all services
curl -f https://localhost/health

# Check individual services
curl -f http://localhost:8000/health
curl -f http://localhost:8501/_stcore/health
```

### Maintenance Mode
```bash
# Enable maintenance mode
docker-compose exec nginx nginx -s reload

# Disable maintenance mode
docker-compose exec nginx nginx -s reload
```

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and project README
- **Issues**: Report bugs on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our Discord/Telegram groups

### Contributing
We welcome contributions! Please see our contributing guidelines for:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements

---

**🎉 Congratulations!** You've successfully deployed MoneyPrinterTurboPro to production. The platform is now ready to handle real-world video generation workloads with enterprise-grade reliability and performance.

**Next Steps:**
1. Configure your domain and SSL certificates
2. Set up monitoring alerts
3. Implement backup automation
4. Plan for scaling as your user base grows
5. Consider implementing CI/CD pipelines

For additional support or questions, please refer to our documentation or reach out to our community.
