# ALICE Deployment and Installation Package
# Complete deployment script for different platforms

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# requirements.txt content
REQUIREMENTS_TXT = """# ALICE Core Dependencies
torch>=2.0.0
transformers>=4.30.0
tokenizers>=0.13.0
accelerate>=0.20.0
bitsandbytes>=0.39.0
gradio>=4.0.0
pyyaml>=6.0
numpy>=1.24.0
psutil>=5.9.0
sqlite3

# Optional but recommended
sentence-transformers>=2.2.0
datasets>=2.12.0
safetensors>=0.3.0

# Web interface
fastapi>=0.100.0
uvicorn>=0.22.0
websockets>=11.0

# Development (optional)
pytest>=7.3.0
black>=23.0.0
flake8>=6.0.0
jupyter>=1.0.0

# Platform-specific
# Windows: pywin32>=306
# Linux: python-systemd>=235
"""

# Docker configuration
DOCKERFILE = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data models logs configs exports backups personas plugins

# Set environment variables
ENV PYTHONPATH=/app
ENV ALICE_DATA_DIR=/app/data
ENV ALICE_MODEL_DIR=/app/models

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:7860/health || exit 1

# Run application
CMD ["python", "start_web.py", "--host", "0.0.0.0", "--port", "7860"]
"""

# Docker Compose configuration
DOCKER_COMPOSE = """version: '3.8'

services:
  alice:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - alice_data:/app/data
      - alice_models:/app/models
      - alice_logs:/app/logs
    environment:
      - ALICE_MODEL=gpt2
      - ALICE_MODE=assistant
      - ALICE_SAFETY_LEVEL=moderate
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  alice-gpu:
    build: .
    ports:
      - "7861:7860"
    volumes:
      - alice_data:/app/data
      - alice_models:/app/models
      - alice_logs:/app/logs
    environment:
      - ALICE_MODEL=microsoft/DialoGPT-medium
      - ALICE_MODE=companion
      - CUDA_VISIBLE_DEVICES=0
    runtime: nvidia
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  alice_data:
  alice_models:
  alice_logs:
"""

# Systemd service file for Linux
SYSTEMD_SERVICE = """[Unit]
Description=ALICE AI Companion System
After=network.target
Wants=network.target

[Service]
Type=simple
User=alice
Group=alice
WorkingDirectory=/opt/alice
Environment=PYTHONPATH=/opt/alice
Environment=ALICE_CONFIG=/opt/alice/alice_config.yaml
ExecStart=/usr/bin/python3 /opt/alice/start_web.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=alice

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/alice/data /opt/alice/logs /opt/alice/models
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
"""

# Windows service configuration (using NSSM)
WINDOWS_SERVICE_INSTALL = """@echo off
echo Installing ALICE as Windows Service...

REM Download NSSM if not present
if not exist nssm.exe (
    echo Downloading NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    copy "nssm-2.24\\win64\\nssm.exe" .
    del nssm.zip
    rmdir /s /q nssm-2.24
)

REM Install service
nssm install ALICE "%~dp0\\start_web.py"
nssm set ALICE AppDirectory "%~dp0"
nssm set ALICE AppParameters ""
nssm set ALICE DisplayName "ALICE AI Companion"
nssm set ALICE Description "Local AI companion system"
nssm set ALICE Start SERVICE_AUTO_START

echo ALICE service installed. Use 'net start ALICE' to start.
pause
"""

class ALICEDeployer:
    """Deployment utility for ALICE system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.base_dir = Path.cwd()
        
    def create_deployment_files(self):
        """Create all deployment configuration files"""
        print("🚀 Creating deployment files...")
        
        # Create requirements.txt
        with open("requirements.txt", "w") as f:
            f.write(REQUIREMENTS_TXT)
        print("   ✅ requirements.txt")
        
        # Create Dockerfile
        with open("Dockerfile", "w") as f:
            f.write(DOCKERFILE)
        print("   ✅ Dockerfile")
        
        # Create docker-compose.yml
        with open("docker-compose.yml", "w") as f:
            f.write(DOCKER_COMPOSE)
        print("   ✅ docker-compose.yml")
        
        # Platform-specific files
        if self.system == "linux":
            with open("alice.service", "w") as f:
                f.write(SYSTEMD_SERVICE)
            print("   ✅ alice.service (systemd)")
            
        elif self.system == "windows":
            with open("install_service.bat", "w") as f:
                f.write(WINDOWS_SERVICE_INSTALL)
            print("   ✅ install_service.bat")
    
    def create_production_config(self):
        """Create production-ready configuration"""
        config = {
            "current_mode": "assistant",
            "max_context_length": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 200,
            "model_name": "microsoft/DialoGPT-medium",
            "safety_level": "moderate",
            "memory_retention_days": 90,
            "log_conversations": True,
            "web_interface_port": 7860,
            "production_mode": True,
            "auto_save_interval": 300,
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "max_concurrent_users": 5,
            "rate_limit_per_minute": 30
        }
        
        import yaml
        with open("alice_config_production.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print("   ✅ alice_config_production.yaml")
    
    def create_nginx_config(self):
        """Create Nginx reverse proxy configuration"""
        nginx_config = """# ALICE Nginx Configuration
server {
    listen 80;
    server_name alice.yourhost.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name alice.yourhost.com;
    
    # SSL Configuration (replace with your certificates)
    ssl_certificate /etc/ssl/certs/alice.crt;
    ssl_certificate_key /etc/ssl/private/alice.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=alice:10m rate=10r/m;
    limit_req zone=alice burst=20 nodelay;
    
    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias /opt/alice/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:7860/health;
    }
}
"""
        
        with open("nginx_alice.conf", "w") as f:
            f.write(nginx_config)
        print("   ✅ nginx_alice.conf")
    
    def create_monitoring_config(self):
        """Create monitoring and logging configuration"""
        
        # Prometheus monitoring
        prometheus_config = """# Prometheus configuration for ALICE
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'alice'
    static_configs:
      - targets: ['localhost:7860']
    scrape_interval: 30s
    metrics_path: /metrics
    
rule_files:
  - "alice_alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""
        
        with open("prometheus.yml", "w") as f:
            f.write(prometheus_config)
        
        # Alert rules
        alert_rules = """groups:
- name: alice_alerts
  rules:
  - alert: ALICEDown
    expr: up{job="alice"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "ALICE system is down"
      description: "ALICE has been down for more than 5 minutes"
      
  - alert: ALICEHighMemoryUsage
    expr: process_resident_memory_bytes{job="alice"} > 8e9
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "ALICE using high memory"
      description: "ALICE memory usage is above 8GB"
      
  - alert: ALICESlowResponses
    expr: avg_over_time(alice_response_time_seconds[5m]) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "ALICE responses are slow"
      description: "Average response time is above 10 seconds"
"""
        
        with open("alice_alerts.yml", "w") as f:
            f.write(alert_rules)
        
        print("   ✅ Monitoring configuration created")
    
    def create_backup_script(self):
        """Create automated backup script"""
        
        backup_script = """#!/bin/bash
# ALICE Backup Script

ALICE_DIR="/opt/alice"
BACKUP_DIR="/backup/alice"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="alice_backup_$DATE"

echo "Starting ALICE backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup configuration
echo "Backing up configuration..."
cp -r "$ALICE_DIR/configs" "$BACKUP_DIR/$BACKUP_NAME/"
cp "$ALICE_DIR/alice_config.yaml" "$BACKUP_DIR/$BACKUP_NAME/" 2>/dev/null || true

# Backup database
echo "Backing up database..."
mkdir -p "$BACKUP_DIR/$BACKUP_NAME/data"
sqlite3 "$ALICE_DIR/data/alice_memory.db" ".backup '$BACKUP_DIR/$BACKUP_NAME/data/alice_memory.db'" 2>/dev/null || true

# Backup personas
echo "Backing up personas..."
cp -r "$ALICE_DIR/personas" "$BACKUP_DIR/$BACKUP_NAME/" 2>/dev/null || true

# Backup logs (last 7 days)
echo "Backing up recent logs..."
find "$ALICE_DIR/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/$BACKUP_NAME/" \\;

# Create archive
echo "Creating archive..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Cleanup old backups (keep last 30)
echo "Cleaning up old backups..."
ls -t alice_backup_*.tar.gz | tail -n +31 | xargs -r rm

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Optional: Upload to cloud storage
# aws s3 cp "$BACKUP_DIR/$BACKUP_NAME.tar.gz" s3://your-bucket/alice-backups/
# rclone copy "$BACKUP_DIR/$BACKUP_NAME.tar.gz" remote:alice-backups/
"""
        
        with open("backup_alice.sh", "w") as f:
            f.write(backup_script)
        
        # Make executable
        if self.system != "windows":
            os.chmod("backup_alice.sh", 0o755)
        
        # Create cron job example
        cron_example = """# ALICE Backup Cron Job
# Run daily at 2 AM
0 2 * * * /opt/alice/backup_alice.sh >> /var/log/alice_backup.log 2>&1

# Run weekly full system backup
0 3 * * 0 /opt/alice/backup_alice.sh --full >> /var/log/alice_backup.log 2>&1
"""
        
        with open("alice_cron_example.txt", "w") as f:
            f.write(cron_example)
        
        print("   ✅ Backup scripts created")
    
    def create_installation_guide(self):
        """Create comprehensive installation guide"""
        
        guide = """# ALICE Installation & Deployment Guide

## Quick Start

### 1. Basic Installation
```bash
# Clone or download ALICE files
git clone <repository> alice
cd alice

# Run setup
python alice_setup.py

# Start console interface
python start_console.py

# Start web interface
python start_web.py
```

### 2. Docker Installation (Recommended for Production)
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f alice

# Access at http://localhost:7860
```

## Detailed Installation

### Prerequisites
- Python 3.8+ 
- 4GB+ RAM (8GB+ recommended)
- 20GB+ storage
- Optional: CUDA GPU with 6GB+ VRAM

### Platform-Specific Setup

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Create virtual environment
python3 -m venv alice_env
source alice_env/bin/activate

# Install ALICE
pip install -r requirements.txt
python alice_setup.py
```

#### CentOS/RHEL
```bash
# Install dependencies
sudo dnf install python3 python3-pip git

# Continue with virtual environment setup...
```

#### Windows
```cmd
# Install Python 3.8+ from python.org
# Install Git for Windows

# Create virtual environment
python -m venv alice_env
alice_env\\Scripts\\activate

# Install ALICE
pip install -r requirements.txt
python alice_setup.py
```

#### Raspberry Pi 4B
```bash
# Lightweight setup for Pi
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Use lightweight models only
export ALICE_MODEL=gpt2
export ALICE_MAX_TOKENS=100

python alice_setup.py
```

### Production Deployment

#### 1. Systemd Service (Linux)
```bash
# Copy service file
sudo cp alice.service /etc/systemd/system/

# Enable and start
sudo systemctl enable alice
sudo systemctl start alice
sudo systemctl status alice
```

#### 2. Docker Production Setup
```bash
# Production compose with GPU support
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale for multiple users
docker-compose up -d --scale alice=3
```

#### 3. Nginx Reverse Proxy
```bash
# Copy nginx configuration
sudo cp nginx_alice.conf /etc/nginx/sites-available/alice
sudo ln -s /etc/nginx/sites-available/alice /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

#### 4. SSL Setup with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d alice.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

### Model Configuration

#### Hardware Recommendations
- **Pi 4B (4GB)**: gpt2, distilgpt2
- **Desktop (8GB RAM)**: microsoft/DialoGPT-medium, gpt-neo-125M
- **Desktop (16GB+ RAM)**: gpt-neo-1.3B, flan-t5-large  
- **GPU (8GB+ VRAM)**: Mistral-7B, Llama-2-7B

#### Model Download
```python
# Auto-download on first use, or pre-download:
from transformers import AutoModel, AutoTokenizer

model_name = "microsoft/DialoGPT-medium"
AutoTokenizer.from_pretrained(model_name, cache_dir="./models")
AutoModel.from_pretrained(model_name, cache_dir="./models")
```

### Security Configuration

#### 1. Firewall Setup
```bash
# UFW (Ubuntu)
sudo ufw allow 7860/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=7860/tcp
sudo firewall-cmd --reload
```

#### 2. User Permissions
```bash
# Create dedicated user
sudo useradd -r -s /bin/false alice
sudo chown -R alice:alice /opt/alice
```

#### 3. Network Security
- Use HTTPS in production
- Implement rate limiting
- Consider VPN for remote access
- Regular security updates

### Monitoring & Maintenance

#### 1. Log Management
```bash
# View logs
tail -f /opt/alice/logs/alice.log

# Rotate logs
sudo logrotate -f /etc/logrotate.d/alice
```

#### 2. Performance Monitoring
```bash
# System resources
htop
nvidia-smi  # If using GPU

# ALICE metrics
curl http://localhost:7860/metrics
```

#### 3. Automated Backups
```bash
# Setup backup cron job
crontab -e
# Add: 0 2 * * * /opt/alice/backup_alice.sh
```

### Troubleshooting

#### Common Issues

**Model Loading Errors**
- Check available RAM/VRAM
- Try smaller model
- Clear cache: `rm -rf ~/.cache/huggingface`

**Web Interface Not Accessible**
- Check port binding: `netstat -ln | grep 7860`
- Verify firewall rules
- Check logs for errors

**Slow Performance**
- Reduce max_tokens in config
- Lower temperature
- Use GPU if available
- Close other applications

**Database Issues**
- Backup: `sqlite3 alice_memory.db ".backup backup.db"`
- Reset: Delete database file (will lose history)

#### Getting Help
- Check logs in `/opt/alice/logs/`
- Verify configuration in `alice_config.yaml`
- Test with minimal model (gpt2)
- Monitor system resources

### Advanced Configuration

#### Custom Personas
Edit `personas/custom_personas.json`:
```json
{
    "my_assistant": {
        "name": "My Custom Assistant",
        "personality": "Helpful and technical",
        "style": "Professional but friendly",
        "restrictions": ["Keep responses technical", "No personal opinions"]
    }
}
```

#### API Integration
```python
# Custom model integration
from alice_core import ModelInterface

class CustomModel(ModelInterface):
    def generate_response(self, prompt, system_prompt=""):
        # Your custom model logic
        return "Custom response"
```

#### Plugin System
```python
# Create plugins in plugins/ directory
class MyPlugin:
    def __init__(self, alice):
        self.alice = alice
    
    def process_input(self, text):
        # Custom processing
        return text
```

### Performance Optimization

#### Model Quantization
```python
# Enable 8-bit quantization for large models
config = {
    "load_in_8bit": True,
    "device_map": "auto"
}
```

#### Caching
- Models cached in `~/.cache/huggingface`
- Conversations cached in SQLite
- Enable response caching for repeated queries

#### Scaling
- Multiple ALICE instances with load balancer
- Shared database for consistency
- Redis for session management

---

For additional support, check the documentation or create an issue in the repository.
"""
        
        with open("INSTALLATION.md", "w") as f:
            f.write(guide)
        print("   ✅ Installation guide created")
    
    def create_health_check_endpoint(self):
        """Create health check endpoint for monitoring"""
        
        health_check = """# ALICE Health Check Endpoint
# Add this to alice_web_interface.py

from datetime import datetime
import json
import psutil
import sqlite3

class HealthChecker:
    def __init__(self, alice_instance):
        self.alice = alice_instance
    
    def get_health_status(self):
        \"\"\"Get comprehensive health status\"\"\"
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": self._get_uptime(),
            "system": self._get_system_info(),
            "alice": self._get_alice_info(),
            "database": self._check_database(),
            "model": self._check_model()
        }
        
        # Determine overall status
        if not status["database"]["healthy"] or not status["model"]["loaded"]:
            status["status"] = "unhealthy"
        elif status["system"]["memory_percent"] > 90:
            status["status"] = "degraded"
        
        return status
    
    def _get_uptime(self):
        \"\"\"Get system uptime\"\"\"
        import time
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return int(uptime_seconds)
    
    def _get_system_info(self):
        \"\"\"Get system resource information\"\"\"
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def _get_alice_info(self):
        \"\"\"Get ALICE-specific information\"\"\"
        return {
            "mode": self.alice.current_mode.value,
            "model": self.alice.config.model_name,
            "short_term_memory": len(self.alice.memory.short_term_memory),
            "running": self.alice.is_running
        }
    
    def _check_database(self):
        \"\"\"Check database connectivity\"\"\"
        try:
            conn = sqlite3.connect(self.alice.memory.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            conn.close()
            
            return {
                "healthy": True,
                "conversation_count": count,
                "path": self.alice.memory.db_path
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def _check_model(self):
        \"\"\"Check model status\"\"\"
        return {
            "loaded": self.alice.model.current_model is not None,
            "name": getattr(self.alice.model, 'model_name', None),
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }

# Add to web interface routes:
@app.route("/health")
def health_check():
    checker = HealthChecker(alice_instance)
    health = checker.get_health_status()
    
    status_code = 200
    if health["status"] == "unhealthy":
        status_code = 503
    elif health["status"] == "degraded":
        status_code = 200  # Still serving requests
    
    return jsonify(health), status_code

@app.route("/metrics")
def metrics():
    \"\"\"Prometheus-style metrics endpoint\"\"\"
    metrics_data = []
    
    # System metrics
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    metrics_data.extend([
        f"alice_cpu_usage_percent {cpu}",
        f"alice_memory_usage_percent {memory.percent}",
        f"alice_memory_used_bytes {memory.used}",
        f"alice_memory_available_bytes {memory.available}"
    ])
    
    # ALICE metrics
    if hasattr(alice_instance, 'model') and hasattr(alice_instance.model, 'inference_times'):
        if alice_instance.model.inference_times:
            avg_time = sum(alice_instance.model.inference_times) / len(alice_instance.model.inference_times)
            metrics_data.append(f"alice_response_time_seconds {avg_time}")
    
    metrics_data.append(f"alice_short_term_memory_count {len(alice_instance.memory.short_term_memory)}")
    metrics_data.append(f"alice_model_loaded {1 if alice_instance.model.current_model else 0}")
    
    return "\\n".join(metrics_data), 200, {"Content-Type": "text/plain"}
"""
        
        with open("health_check.py", "w") as f:
            f.write(health_check)
        print("   ✅ Health check endpoint created")
    
    def deploy_all(self):
        """Create all deployment files"""
        print("🚀 Creating complete ALICE deployment package...")
        
        self.create_deployment_files()
        self.create_production_config()
        self.create_nginx_config()
        self.create_monitoring_config()
        self.create_backup_script()
        self.create_installation_guide()
        self.create_health_check_endpoint()
        
        # Create deployment summary
        summary = """
# ALICE Deployment Package Created Successfully! 🎉

## Files Created:
- requirements.txt           # Python dependencies
- Dockerfile                 # Container configuration
- docker-compose.yml         # Docker orchestration
- alice_config_production.yaml # Production configuration
- nginx_alice.conf           # Reverse proxy setup
- prometheus.yml             # Monitoring configuration
- alice_alerts.yml           # Alert rules
- backup_alice.sh            # Automated backup script
- alice_cron_example.txt     # Scheduled tasks
- INSTALLATION.md            # Comprehensive setup guide
- health_check.py            # Health monitoring

## Platform-Specific Files:
"""
        
        if self.system == "linux":
            summary += "- alice.service              # Systemd service file\n"
        elif self.system == "windows":
            summary += "- install_service.bat        # Windows service installer\n"
        
        summary += """
## Next Steps:

1. **Development Setup:**
   ```bash
   python alice_setup.py
   python start_web.py
   ```

2. **Docker Deployment:**
   ```bash
   docker-compose up -d
   ```

3. **Production Setup:**
   - Follow INSTALLATION.md guide
   - Configure SSL certificates
   - Set up monitoring and backups
   - Configure firewall and security

4. **Customization:**
   - Edit alice_config_production.yaml
   - Customize personas in personas/
   - Add monitoring alerts

## Support:
- Read INSTALLATION.md for detailed instructions
- Check health endpoint: /health
- Monitor metrics: /metrics
- View logs in logs/ directory

Your ALICE deployment package is ready! 🤖
"""
        
        with open("DEPLOYMENT_README.txt", "w") as f:
            f.write(summary)
        
        print(summary)

def main():
    """Main deployment script"""
    deployer = ALICEDeployer()
    
    print("ALICE Deployment Package Creator")
    print("=" * 40)
    
    deployer.deploy_all()

if __name__ == "__main__":
    main()