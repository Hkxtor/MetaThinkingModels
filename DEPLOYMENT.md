# ThinkingModels Deployment Guide

This guide covers various deployment options for the ThinkingModels application, from local development to production deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- Python 3.8+ (3.11+ recommended)
- 1GB+ RAM (2GB+ recommended)
- 1GB+ disk space
- Internet connection for LLM API access

### Required Environment Variables

```bash
# Required
LLM_API_URL=https://your-llm-api-endpoint.com

# Optional but recommended
LLM_API_KEY=your-api-key
LLM_MODEL_NAME=gpt-3.5-turbo
```

---

## Local Development

### Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/your-username/ThinkingModels.git
   cd ThinkingModels
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # Create .env file
   echo "LLM_API_URL=https://your-api-endpoint.com" > .env
   echo "LLM_API_KEY=your-api-key" >> .env
   ```

3. **Start the application:**
   ```bash
   # Web interface
   python web_server.py
   
   # Or CLI interface
   python thinking_models.py interactive
   ```

### Development Server Options

```bash
# Basic server
python web_server.py

# Development mode with auto-reload
python web_server.py --reload

# Custom host and port
python web_server.py --host 0.0.0.0 --port 8080

# Debug mode
python web_server.py --log-level debug
```

---

## Docker Deployment

Docker provides the easiest deployment method with consistent environments.

### Using Docker Compose (Recommended)

1. **Create environment file:**
   ```bash
   # Create .env file for docker-compose
   cat > .env << EOF
   LLM_API_URL=https://your-llm-api-endpoint.com
   LLM_API_KEY=your-api-key
   LLM_MODEL_NAME=gpt-3.5-turbo
   LOG_LEVEL=INFO
   EOF
   ```

2. **Deploy with Docker Compose:**
   ```bash
   # Start the application
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop the application
   docker-compose down
   ```

3. **Access the application:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

### Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t thinking-models .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name thinking-models-app \
     -p 8000:8000 \
     -e LLM_API_URL="https://your-api-endpoint.com" \
     -e LLM_API_KEY="your-api-key" \
     thinking-models
   ```

3. **Manage the container:**
   ```bash
   # View logs
   docker logs -f thinking-models-app
   
   # Stop container
   docker stop thinking-models-app
   
   # Remove container
   docker rm thinking-models-app
   ```

---

## Production Deployment

### System Setup

1. **Server requirements:**
   - Ubuntu 20.04+ / CentOS 8+ / Debian 11+
   - 2GB+ RAM, 2+ CPU cores
   - 10GB+ disk space
   - Python 3.8+, Docker (optional)

2. **Install dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git curl
   
   # CentOS/RHEL
   sudo yum install python3 python3-pip git curl
   ```

### Production Deployment Steps

1. **Create application user:**
   ```bash
   sudo useradd --create-home --shell /bin/bash thinkingmodels
   sudo su - thinkingmodels
   ```

2. **Deploy application:**
   ```bash
   git clone https://github.com/your-username/ThinkingModels.git
   cd ThinkingModels
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create production environment file
   cat > .env << EOF
   LLM_API_URL=https://your-production-api-endpoint.com
   LLM_API_KEY=your-production-api-key
   LLM_MODEL_NAME=gpt-4
   LOG_LEVEL=INFO
   WEB_HOST=127.0.0.1
   WEB_PORT=8000
   EOF
   ```

4. **Create systemd service:**
   ```bash
   sudo tee /etc/systemd/system/thinking-models.service > /dev/null << EOF
   [Unit]
   Description=ThinkingModels Web Application
   After=network.target
   
   [Service]
   Type=exec
   User=thinkingmodels
   WorkingDirectory=/home/thinkingmodels/ThinkingModels
   Environment=PATH=/home/thinkingmodels/ThinkingModels/venv/bin
   EnvironmentFile=/home/thinkingmodels/ThinkingModels/.env
   ExecStart=/home/thinkingmodels/ThinkingModels/venv/bin/python web_server.py --host 127.0.0.1 --port 8000
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   ```

5. **Start and enable service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable thinking-models
   sudo systemctl start thinking-models
   sudo systemctl status thinking-models
   ```

### Reverse Proxy (Nginx)

1. **Install Nginx:**
   ```bash
   sudo apt install nginx
   ```

2. **Configure Nginx:**
   ```bash
   sudo tee /etc/nginx/sites-available/thinking-models << EOF
   server {
       listen 80;
       server_name your-domain.com;
   
       client_max_body_size 16M;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   
       location /ws {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade \$http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   }
   EOF
   ```

3. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/thinking-models /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 instance:**
   - Choose Ubuntu 20.04 LTS
   - t3.small or larger
   - Configure security group (HTTP, HTTPS, SSH)

2. **Deploy application:**
   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-ec2-instance.com
   
   # Follow production deployment steps above
   ```

#### Using ECS with Docker

1. **Create task definition:**
   ```json
   {
     "family": "thinking-models",
     "networkMode": "awsvpc",
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "thinking-models",
         "image": "your-account.dkr.ecr.region.amazonaws.com/thinking-models:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "LLM_API_URL",
             "value": "https://your-api-endpoint.com"
           },
           {
             "name": "LLM_API_KEY",
             "value": "your-api-key"
           }
         ]
       }
     ]
   }
   ```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push Docker image:**
   ```bash
   # Build image
   docker build -t gcr.io/your-project/thinking-models .
   
   # Push to Container Registry
   docker push gcr.io/your-project/thinking-models
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy thinking-models \
     --image gcr.io/your-project/thinking-models \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="LLM_API_URL=https://your-api-endpoint.com,LLM_API_KEY=your-api-key"
   ```

### DigitalOcean Droplet

1. **Create droplet:**
   - Ubuntu 20.04
   - 2GB RAM minimum
   - Enable monitoring and backups

2. **Deploy with Docker:**
   ```bash
   # Connect to droplet
   ssh root@your-droplet-ip
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Deploy application
   git clone https://github.com/your-username/ThinkingModels.git
   cd ThinkingModels
   
   # Configure environment
   echo "LLM_API_URL=https://your-api-endpoint.com" > .env
   echo "LLM_API_KEY=your-api-key" >> .env
   
   # Start with Docker Compose
   docker-compose up -d
   ```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_URL` | Yes | - | LLM API endpoint URL |
| `LLM_API_KEY` | No | - | API authentication key |
| `LLM_MODEL_NAME` | No | `gpt-3.5-turbo` | Model name |
| `LLM_TEMPERATURE` | No | `0.7` | Model temperature |
| `LLM_MAX_TOKENS` | No | `2000` | Maximum response tokens |
| `WEB_HOST` | No | `127.0.0.1` | Web server host |
| `WEB_PORT` | No | `8000` | Web server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Configuration Files

Create a `config.ini` file for advanced configuration:

```ini
[llm]
api_url = https://your-api-endpoint.com
api_key = your-api-key
model_name = gpt-3.5-turbo
temperature = 0.7
max_tokens = 2000
timeout = 30

[web]
host = 127.0.0.1
port = 8000
workers = 1

[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s

[models]
directory = models
cache_enabled = true
```

---

## Monitoring

### Health Checks

Monitor application health:

```bash
# Basic health check
curl http://localhost:8000/api/health

# Detailed status
curl http://localhost:8000/api/status

# Monitor with watch
watch -n 30 "curl -s http://localhost:8000/api/health | jq '.'"
```

### Logging

Application logs are available:

```bash
# View application logs (systemd)
sudo journalctl -u thinking-models -f

# View Docker logs
docker logs -f thinking-models-app

# View Docker Compose logs
docker-compose logs -f
```

### Metrics Collection

Add monitoring with Prometheus:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

#### Permission Denied
```bash
# Fix file permissions
sudo chown -R thinkingmodels:thinkingmodels /path/to/ThinkingModels
chmod +x web_server.py thinking_models.py
```

#### Models Not Loading
```bash
# Check models directory
ls -la models/

# Verify models count
python -c "from src.core.model_parser import ModelParser; mp = ModelParser(); print(f'Loaded {len(mp.models)} models')"
```

#### API Connection Issues
```bash
# Test API connectivity
curl -H "Authorization: Bearer $LLM_API_KEY" "$LLM_API_URL/models"

# Check environment variables
env | grep LLM_
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG

# Or use CLI flag
python web_server.py --log-level debug
```

### Performance Issues

1. **Increase resources:**
   - Add more RAM/CPU
   - Use SSD storage
   - Increase worker processes

2. **Optimize configuration:**
   ```bash
   # Use multiple workers (production)
   python web_server.py --workers 4
   
   # Adjust timeout
   export LLM_TIMEOUT=60
   ```

### Support and Issues

1. **Check logs first:**
   ```bash
   # Recent application logs
   sudo journalctl -u thinking-models --since "1 hour ago"
   ```

2. **Verify system health:**
   ```bash
   # Test all components
   python thinking_models.py test
   ```

3. **Reset and retry:**
   ```bash
   # Restart service
   sudo systemctl restart thinking-models
   
   # Or restart Docker container
   docker-compose restart
   ```

---

For additional help, refer to:
- [Main Documentation](README.md)
- [CLI Documentation](CLI_README.md) 
- [API Documentation](API_DOCUMENTATION.md)
