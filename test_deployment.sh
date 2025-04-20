#!/bin/bash
# MixMaster AI - Docker Deployment Test Script

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting MixMaster AI Docker Deployment Test...${NC}"

# Check if Docker is installed
echo -e "\n${YELLOW}Checking if Docker is installed...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}Docker is installed.${NC}"
else
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
echo -e "\n${YELLOW}Checking if Docker Compose is installed...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}Docker Compose is installed.${NC}"
else
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
echo -e "\n${YELLOW}Checking if .env file exists...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}.env file exists.${NC}"
else
    echo -e "${YELLOW}.env file does not exist. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please edit it with your configuration values.${NC}"
    else
        echo -e "${RED}.env.example file not found. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p data/uploads data/results data/mongodb nginx/conf nginx/certbot/conf nginx/certbot/www
echo -e "${GREEN}Directories created.${NC}"

# Copy Nginx configuration if it doesn't exist
echo -e "\n${YELLOW}Checking Nginx configuration...${NC}"
if [ ! -f nginx/conf/default.conf ]; then
    echo -e "${YELLOW}Nginx configuration not found. Creating...${NC}"
    if [ ! -d nginx/conf ]; then
        mkdir -p nginx/conf
    fi
    cp /home/ubuntu/nginx/conf/default.conf nginx/conf/default.conf
    echo -e "${GREEN}Nginx configuration created.${NC}"
else
    echo -e "${GREEN}Nginx configuration exists.${NC}"
fi

# Test Docker Compose configuration
echo -e "\n${YELLOW}Testing Docker Compose configuration...${NC}"
if docker-compose config > /dev/null; then
    echo -e "${GREEN}Docker Compose configuration is valid.${NC}"
else
    echo -e "${RED}Docker Compose configuration is invalid. Please check your docker-compose.yml file.${NC}"
    exit 1
fi

# Start containers
echo -e "\n${YELLOW}Starting containers...${NC}"
docker-compose up -d

# Check if containers are running
echo -e "\n${YELLOW}Checking if containers are running...${NC}"
sleep 10
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}Containers are running.${NC}"
else
    echo -e "${RED}Containers failed to start. Please check the logs.${NC}"
    docker-compose logs
    exit 1
fi

# Test backend API
echo -e "\n${YELLOW}Testing backend API...${NC}"
if curl -s http://localhost:8000/api/health | grep -q "status"; then
    echo -e "${GREEN}Backend API is working.${NC}"
else
    echo -e "${RED}Backend API is not responding. Please check the logs.${NC}"
    docker-compose logs backend
    exit 1
fi

# Test frontend
echo -e "\n${YELLOW}Testing frontend...${NC}"
if curl -s http://localhost:3000 | grep -q "html"; then
    echo -e "${GREEN}Frontend is working.${NC}"
else
    echo -e "${RED}Frontend is not responding. Please check the logs.${NC}"
    docker-compose logs frontend
    exit 1
fi

# Test MongoDB connection
echo -e "\n${YELLOW}Testing MongoDB connection...${NC}"
if docker-compose exec -T mongodb mongosh --eval "db.stats()" | grep -q "collections"; then
    echo -e "${GREEN}MongoDB connection is working.${NC}"
else
    echo -e "${RED}MongoDB connection failed. Please check the logs.${NC}"
    docker-compose logs mongodb
    exit 1
fi

# Test Stripe configuration
echo -e "\n${YELLOW}Testing Stripe configuration...${NC}"
source .env
if [ -z "$STRIPE_API_KEY" ] || [ -z "$NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY" ]; then
    echo -e "${YELLOW}Stripe API keys not configured. Monetization features will not work.${NC}"
else
    echo -e "${GREEN}Stripe API keys are configured.${NC}"
fi

# Print success message
echo -e "\n${GREEN}All tests passed! MixMaster AI is running successfully.${NC}"
echo -e "${YELLOW}You can access the application at:${NC}"
echo -e "  - Frontend: http://localhost:3000"
echo -e "  - Backend API: http://localhost:8000"

# Print cleanup instructions
echo -e "\n${YELLOW}To stop the containers, run:${NC}"
echo -e "  docker-compose down"

echo -e "\n${YELLOW}To view logs, run:${NC}"
echo -e "  docker-compose logs -f"

exit 0
