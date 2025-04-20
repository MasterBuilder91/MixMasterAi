#!/bin/bash
# MixMaster AI - Docker Deployment Script

# Create necessary directories
mkdir -p data/uploads data/results data/mongodb nginx/conf nginx/certbot/conf nginx/certbot/www

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
    echo "Please edit the .env file with your configuration values"
  else
    echo "Error: .env.example file not found"
    exit 1
  fi
fi

# Function to display help
show_help() {
  echo "MixMaster AI Docker Deployment Script"
  echo ""
  echo "Usage: ./deploy.sh [command]"
  echo ""
  echo "Commands:"
  echo "  start       Start all services"
  echo "  stop        Stop all services"
  echo "  restart     Restart all services"
  echo "  logs        Show logs from all services"
  echo "  status      Show status of all services"
  echo "  ssl         Set up SSL certificates (requires domain to be pointed to server)"
  echo "  help        Show this help message"
  echo ""
}

# Function to set up SSL certificates
setup_ssl() {
  # Load domain from .env file
  if [ -f .env ]; then
    source .env
  fi
  
  if [ -z "$DOMAIN_NAME" ]; then
    echo "Error: DOMAIN_NAME not set in .env file"
    exit 1
  fi
  
  echo "Setting up SSL certificates for $DOMAIN_NAME"
  
  # Replace domain in nginx config
  sed -i "s/yourdomain.com/$DOMAIN_NAME/g" nginx/conf/default.conf
  
  # Start nginx for certbot challenge
  docker-compose up -d nginx
  
  # Get SSL certificates
  docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
    --email ${ADMIN_EMAILS:-admin@example.com} --agree-tos --no-eff-email \
    -d $DOMAIN_NAME -d www.$DOMAIN_NAME
  
  # Restart nginx to apply SSL certificates
  docker-compose restart nginx
  
  echo "SSL certificates have been set up for $DOMAIN_NAME"
}

# Process command line arguments
case "$1" in
  start)
    echo "Starting MixMaster AI services..."
    docker-compose up -d
    ;;
  stop)
    echo "Stopping MixMaster AI services..."
    docker-compose down
    ;;
  restart)
    echo "Restarting MixMaster AI services..."
    docker-compose restart
    ;;
  logs)
    echo "Showing logs from MixMaster AI services..."
    docker-compose logs -f
    ;;
  status)
    echo "Status of MixMaster AI services:"
    docker-compose ps
    ;;
  ssl)
    setup_ssl
    ;;
  help|*)
    show_help
    ;;
esac
