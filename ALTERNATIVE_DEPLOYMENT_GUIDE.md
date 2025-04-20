# MixMaster AI - Alternative Deployment Guide

This comprehensive guide provides detailed instructions for deploying the MixMaster AI platform using Docker containers as an alternative to Replit deployment.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup Instructions](#detailed-setup-instructions)
5. [Configuration Options](#configuration-options)
6. [Monetization Features](#monetization-features)
7. [Maintenance and Updates](#maintenance-and-updates)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Overview

This deployment solution uses Docker and Docker Compose to create a containerized environment for running MixMaster AI. The solution includes:

- Backend API server (FastAPI)
- Frontend web application (Next.js)
- MongoDB database
- Nginx web server for production deployment
- SSL certificate management with Certbot

This approach offers several advantages over Replit deployment:
- Better performance for audio processing
- No resource limitations
- Full control over the environment
- Ability to scale horizontally
- Persistent data storage

## Prerequisites

Before you begin, ensure you have:

- A server or VM with at least 2GB RAM and 20GB storage
- Docker and Docker Compose installed
- Basic knowledge of terminal/command line
- Domain name (optional, but recommended for production)
- Stripe account for payment processing

## Quick Start

1. Clone the repository or download the deployment package:
   ```bash
   git clone https://github.com/yourusername/mixmaster-ai.git
   cd mixmaster-ai
   ```

2. Run the test deployment script to verify your environment:
   ```bash
   chmod +x test_deployment.sh
   ./test_deployment.sh
   ```

3. Create and configure your `.env` file:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your configuration values
   ```

4. Start the application:
   ```bash
   ./deploy.sh start
   ```

5. Access the application at http://localhost:3000

## Detailed Setup Instructions

### Installing Docker and Docker Compose

#### Ubuntu/Debian:
```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker repository
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package index again
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group
sudo usermod -aG docker ${USER}

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Apply group changes
newgrp docker
```

#### macOS:
1. Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Start Docker Desktop

#### Windows:
1. Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Start Docker Desktop
3. Ensure WSL 2 is enabled

### Setting Up the Environment

1. Create the necessary directories:
   ```bash
   mkdir -p data/uploads data/results data/mongodb nginx/conf nginx/certbot/conf nginx/certbot/www
   ```

2. Configure your environment variables in the `.env` file:
   ```
   # General Configuration
   ENVIRONMENT=production
   DEBUG=false

   # MongoDB Configuration
   MONGODB_URI=mongodb://mongodb:27017/mixmaster

   # JWT Authentication
   JWT_SECRET_KEY=your_secure_random_string_change_this_in_production
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # Stripe Configuration
   STRIPE_API_KEY=sk_test_your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_MONTHLY_SUBSCRIPTION_PRICE_ID=price_your_monthly_subscription_price_id
   STRIPE_LIFETIME_ACCESS_PRICE_ID=price_your_lifetime_access_price_id

   # Admin Configuration
   ADMIN_EMAILS=your_email@example.com

   # API URL for frontend
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Domain Configuration (for production)
   DOMAIN_NAME=yourdomain.com
   ```

3. Configure Nginx for your domain:
   - Edit `nginx/conf/default.conf` and replace `yourdomain.com` with your actual domain name

### Starting the Application

Use the deployment script to manage the application:

```bash
# Start all services
./deploy.sh start

# Stop all services
./deploy.sh stop

# Restart all services
./deploy.sh restart

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Set up SSL certificates (requires domain to be pointed to server)
./deploy.sh ssl
```

## Configuration Options

### Backend Configuration

The backend service can be configured through environment variables in the `.env` file:

- `ENVIRONMENT`: Set to `production` for production deployment, `development` for development
- `DEBUG`: Set to `true` to enable debug logging, `false` for production
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time in minutes

### Frontend Configuration

The frontend service can be configured through environment variables in the `.env` file:

- `NEXT_PUBLIC_API_URL`: URL of the backend API
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Stripe publishable key for frontend payment integration

### Nginx Configuration

The Nginx configuration is located in `nginx/conf/default.conf`. You can modify this file to:

- Change server names
- Configure SSL settings
- Add custom headers
- Set up caching
- Configure rate limiting

### MongoDB Configuration

MongoDB uses the default configuration. If you need to customize it, you can add a `mongod.conf` file and mount it in the `docker-compose.yml` file.

## Monetization Features

MixMaster AI includes a complete monetization system with the following features:

### Pricing Tiers

1. **Free Tier**
   - 1 song free
   - Basic mixing & mastering
   - WAV & MP3 export

2. **Pay-Per-Use**
   - $5 per mix/master
   - Advanced mixing & mastering
   - All export formats

3. **Monthly Subscription**
   - $40 per month
   - Unlimited songs
   - Advanced mixing & mastering
   - Priority processing
   - All export formats

4. **Lifetime Access**
   - $500 one-time payment
   - Unlimited songs forever
   - Premium mixing & mastering
   - Highest priority processing
   - All future updates included

### Stripe Integration

The monetization system uses Stripe for payment processing. To set up Stripe:

1. Create a Stripe account at [https://stripe.com](https://stripe.com)
2. Get your API keys from the Stripe Dashboard
3. Create products and prices for each tier:
   - Monthly Subscription ($40/month)
   - Lifetime Access ($500 one-time)
   - Pay-Per-Use Credits ($5 per credit)
4. Add the product and price IDs to your `.env` file
5. Set up a webhook in the Stripe Dashboard pointing to `https://yourdomain.com/api/payments/webhook`
6. Add the webhook secret to your `.env` file

## Maintenance and Updates

### Backing Up Data

To back up your MongoDB data:

```bash
# Create a backup directory
mkdir -p backups

# Backup MongoDB data
docker-compose exec -T mongodb mongodump --out=/data/db/backup

# Copy backup from container to host
docker cp $(docker-compose ps -q mongodb):/data/db/backup ./backups/mongodb_$(date +%Y%m%d)
```

### Updating the Application

To update the application:

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Rebuild and restart the containers:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Monitoring

You can monitor the application using Docker's built-in tools:

```bash
# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# View resource usage
docker stats
```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check logs: `docker-compose logs [service_name]`
   - Verify environment variables in `.env` file
   - Ensure ports are not already in use

2. **MongoDB connection issues**
   - Check if MongoDB container is running: `docker-compose ps mongodb`
   - Verify MongoDB connection string in `.env` file
   - Check MongoDB logs: `docker-compose logs mongodb`

3. **Stripe payment issues**
   - Verify Stripe API keys in `.env` file
   - Check webhook configuration in Stripe Dashboard
   - Examine backend logs: `docker-compose logs backend`

4. **SSL certificate issues**
   - Ensure your domain is correctly pointed to your server's IP
   - Check Certbot logs: `docker-compose logs certbot`
   - Verify Nginx configuration: `docker-compose exec nginx nginx -t`

### Logs

To view logs for specific services:

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# MongoDB logs
docker-compose logs mongodb

# Nginx logs
docker-compose logs nginx
```

## FAQ

**Q: Can I run this on a low-resource VPS?**
A: Yes, but performance may be limited. We recommend at least 2GB RAM for optimal performance, especially for audio processing.

**Q: How do I update my SSL certificates?**
A: Certbot will automatically renew certificates. You can manually trigger renewal with `docker-compose exec certbot certbot renew`.

**Q: Can I use a different database instead of MongoDB?**
A: The application is designed to work with MongoDB. Using a different database would require significant code changes.

**Q: How do I add an admin user?**
A: Add the admin's email to the `ADMIN_EMAILS` environment variable in the `.env` file.

**Q: How can I customize the audio processing parameters?**
A: The audio processing parameters can be modified in the backend code. See `mixmaster_ai_backend/app/audio/processing/processor.py` for details.

**Q: Is horizontal scaling supported?**
A: The basic setup is not configured for horizontal scaling. For high-load scenarios, you would need to implement a load balancer and ensure session persistence.
