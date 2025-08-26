#!/bin/bash

# MoneyPrinterTurboPro Production Deployment Script
# This script deploys the entire platform to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="mptp"

echo -e "${BLUE}🚀 MoneyPrinterTurboPro Production Deployment${NC}"
echo -e "${BLUE}=============================================${NC}"
echo -e "Environment: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Compose file: ${GREEN}${COMPOSE_FILE}${NC}"
echo -e "Project name: ${GREEN}${PROJECT_NAME}${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${YELLOW}📋 Loading environment variables from .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. Using default environment variables.${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p data logs nginx/logs nginx/ssl monitoring/grafana/dashboards monitoring/grafana/datasources database

# Generate self-signed SSL certificate for development
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo -e "${YELLOW}🔐 Generating self-signed SSL certificate...${NC}"
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} down --remove-orphans

# Remove old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker system prune -f

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} up -d --build

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🏥 Checking service health...${NC}"
services=("backend" "frontend" "postgres" "redis" "nginx" "prometheus" "grafana")

for service in "${services[@]}"; do
    if docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} ps | grep -q "${service}.*Up"; then
        echo -e "  ✅ ${service}: ${GREEN}Running${NC}"
    else
        echo -e "  ❌ ${service}: ${RED}Failed${NC}"
    fi
done

# Initialize database
echo -e "${YELLOW}🗄️  Initializing database...${NC}"
sleep 10
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} exec -T postgres psql -U mptp_user -d mptp_db -c "SELECT version();" > /dev/null 2>&1 && \
    echo -e "  ✅ Database: ${GREEN}Initialized${NC}" || \
    echo -e "  ⚠️  Database: ${YELLOW}Still initializing...${NC}"

# Show service URLs
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📱 Service URLs:${NC}"
echo -e "  🌐 WebUI: ${GREEN}https://localhost${NC}"
echo -e "  🔌 API: ${GREEN}https://localhost/api${NC}"
echo -e "  📊 Grafana: ${GREEN}http://localhost:3000${NC}"
echo -e "  📈 Prometheus: ${GREEN}http://localhost:9090${NC}"
echo ""
echo -e "${BLUE}🔑 Default Credentials:${NC}"
echo -e "  Grafana: admin / mptp_grafana_password"
echo -e "  PostgreSQL: mptp_user / mptp_password"
echo -e "  Redis: (no auth required)"
echo ""

# Show logs
echo -e "${YELLOW}📋 Recent logs (press Ctrl+C to exit):${NC}"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} logs -f --tail=50
