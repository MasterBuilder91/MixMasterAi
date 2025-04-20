# MixMaster AI - Cloud Deployment Guide

This guide provides instructions for deploying the MixMaster AI platform on various cloud providers using Docker.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [AWS Deployment](#aws-deployment)
4. [DigitalOcean Deployment](#digitalocean-deployment)
5. [Google Cloud Platform Deployment](#google-cloud-platform-deployment)
6. [Microsoft Azure Deployment](#microsoft-azure-deployment)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying MixMaster AI to any cloud platform, ensure you have:

- Docker and Docker Compose installed on your local machine
- A Stripe account with API keys configured
- Domain name (optional, but recommended for production)
- SSH key pair for secure server access

## Deployment Options

MixMaster AI can be deployed in several ways:

1. **Single VM Deployment**: Deploy all services on a single virtual machine
2. **Managed Kubernetes**: Deploy using Kubernetes on managed services like EKS, GKE, or AKS
3. **Container Services**: Deploy using managed container services like AWS ECS or Azure Container Instances

This guide focuses on the single VM deployment option, which is the simplest and most cost-effective for small to medium workloads.

## AWS Deployment

### Step 1: Launch an EC2 Instance

1. Log in to the AWS Management Console
2. Navigate to EC2 and click "Launch Instance"
3. Choose an Ubuntu Server 22.04 LTS AMI
4. Select an instance type (recommended: t3.medium or larger for audio processing)
5. Configure instance details as needed
6. Add storage (recommended: at least 30GB)
7. Add tags as needed
8. Configure security group to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
9. Review and launch the instance
10. Select your SSH key pair

### Step 2: Connect to Your Instance

```bash
ssh -i /path/to/your-key.pem ubuntu@your-instance-public-ip
```

### Step 3: Install Docker and Docker Compose

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

### Step 4: Deploy MixMaster AI

1. Clone or upload your MixMaster AI files to the server
2. Navigate to the project directory
3. Create and configure your `.env` file
4. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

### Step 5: Set Up Domain and SSL (Optional)

1. Point your domain to your EC2 instance's public IP
2. Run the SSL setup script:

```bash
./deploy.sh ssl
```

## DigitalOcean Deployment

### Step 1: Create a Droplet

1. Log in to your DigitalOcean account
2. Click "Create" and select "Droplets"
3. Choose Ubuntu 22.04 LTS
4. Select a plan (recommended: Basic with 4GB RAM / 2 CPUs or higher)
5. Choose a datacenter region close to your users
6. Add your SSH key
7. Click "Create Droplet"

### Step 2: Connect to Your Droplet

```bash
ssh root@your-droplet-ip
```

### Step 3: Install Docker and Docker Compose

```bash
# Update package index
apt update

# Install required packages
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

# Add Docker repository
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package index again
apt update

# Install Docker
apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 4: Deploy MixMaster AI

1. Clone or upload your MixMaster AI files to the server
2. Navigate to the project directory
3. Create and configure your `.env` file
4. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

### Step 5: Set Up Domain and SSL (Optional)

1. Point your domain to your Droplet's IP address
2. Run the SSL setup script:

```bash
./deploy.sh ssl
```

## Google Cloud Platform Deployment

### Step 1: Create a VM Instance

1. Log in to the Google Cloud Console
2. Navigate to Compute Engine > VM instances
3. Click "Create Instance"
4. Name your instance
5. Select a region and zone
6. Choose a machine type (e2-medium or higher recommended)
7. Select Ubuntu 22.04 LTS as the boot disk
8. Allow HTTP and HTTPS traffic in the firewall settings
9. Click "Create"

### Step 2: Connect to Your VM

You can connect directly from the GCP Console by clicking the "SSH" button, or use your own SSH client:

```bash
ssh -i /path/to/your-key username@external-ip
```

### Step 3: Install Docker and Docker Compose

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

### Step 4: Deploy MixMaster AI

1. Clone or upload your MixMaster AI files to the server
2. Navigate to the project directory
3. Create and configure your `.env` file
4. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

### Step 5: Set Up Domain and SSL (Optional)

1. Point your domain to your VM's external IP
2. Run the SSL setup script:

```bash
./deploy.sh ssl
```

## Microsoft Azure Deployment

### Step 1: Create a Virtual Machine

1. Log in to the Azure Portal
2. Click "Create a resource" and search for "Virtual Machine"
3. Fill in the basic details:
   - Select your subscription and resource group
   - Name your VM
   - Choose a region close to your users
   - Select Ubuntu Server 22.04 LTS
   - Choose a VM size (Standard_D2s_v3 or higher recommended)
4. Set up administrator account and SSH key
5. Allow inbound ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)
6. Review and create the VM

### Step 2: Connect to Your VM

```bash
ssh azureuser@your-vm-public-ip
```

### Step 3: Install Docker and Docker Compose

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

### Step 4: Deploy MixMaster AI

1. Clone or upload your MixMaster AI files to the server
2. Navigate to the project directory
3. Create and configure your `.env` file
4. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

### Step 5: Set Up Domain and SSL (Optional)

1. Point your domain to your VM's public IP
2. Run the SSL setup script:

```bash
./deploy.sh ssl
```

## Post-Deployment Configuration

After deploying MixMaster AI, you should:

1. **Update Stripe Webhook URL**: In your Stripe Dashboard, update the webhook URL to `https://yourdomain.com/api/payments/webhook`

2. **Test the Application**: Visit your domain or server IP to ensure everything is working correctly

3. **Monitor Logs**: Use `./deploy.sh logs` to monitor application logs for any issues

4. **Set Up Backups**: Configure regular backups of your MongoDB data directory

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Docker containers are running: `docker-compose ps`
   - Check container logs: `docker-compose logs [service_name]`
   - Verify firewall settings allow traffic on ports 80 and 443

2. **SSL Certificate Issues**
   - Ensure your domain is correctly pointed to your server's IP
   - Check Certbot logs: `docker-compose logs certbot`
   - Verify Nginx configuration: `docker-compose exec nginx nginx -t`

3. **Payment Processing Issues**
   - Verify Stripe API keys in your `.env` file
   - Check webhook configuration in Stripe Dashboard
   - Examine backend logs: `docker-compose logs backend`

4. **Audio Processing Errors**
   - Ensure ffmpeg is correctly installed in the backend container
   - Check for sufficient disk space and memory
   - Examine backend logs for specific error messages

For additional help, please refer to the documentation or contact support.
