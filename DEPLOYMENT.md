# Production Deployment Guide

This guide covers deploying the Design Assistant to production.

## Pre-Deployment Checklist

- [ ] All API keys secured in environment variables
- [ ] Okta production app configured
- [ ] HTTPS certificate obtained
- [ ] Domain name configured
- [ ] Database backup strategy defined
- [ ] Monitoring and logging set up
- [ ] Security review completed

---

## Deployment Options

### Option 1: Docker (Recommended)

Simple, portable, consistent across environments.

### Option 2: Traditional Server

Direct deployment on VM or bare metal.

### Option 3: Cloud Services

AWS, GCP, Azure container services.

---

## Docker Deployment

### 1. Build the Image

```bash
# Build the combined image
docker build -t design-assistant:latest .

# Or build specific versions
docker build -t design-assistant:v1.0.0 .
```

### 2. Create Environment File

Create `production.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-prod-key

# Figma
FIGMA_ACCESS_TOKEN=figd_prod-token
FIGMA_TEAM_ID=your-team-id

# Google
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-prod.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id

# Okta
OKTA_DOMAIN=your-company.okta.com
OKTA_CLIENT_ID=prod-client-id
OKTA_CLIENT_SECRET=prod-client-secret
OKTA_ISSUER=https://your-company.okta.com/oauth2/default
OKTA_REDIRECT_URI=https://design-assistant.your-company.com/callback

# Application
ALLOWED_ORIGINS=https://design-assistant.your-company.com
DEBUG=False
```

### 3. Run Container

```bash
# Create data directory
mkdir -p /opt/design-assistant/data

# Run container
docker run -d \
  --name design-assistant \
  --env-file production.env \
  -v /opt/design-assistant/data:/app/data \
  -v /path/to/google-creds.json:/app/credentials/google-prod.json:ro \
  -p 8000:8000 \
  --restart unless-stopped \
  design-assistant:latest
```

### 4. Set Up Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt update
sudo apt install nginx
```

Create Nginx configuration `/etc/nginx/sites-available/design-assistant`:

```nginx
server {
    listen 80;
    server_name design-assistant.your-company.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name design-assistant.your-company.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/design-assistant.your-company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/design-assistant.your-company.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Frontend (if served separately)
    location / {
        root /var/www/design-assistant;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for streaming
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # Health check
    location /api/health {
        proxy_pass http://localhost:8000/api/health;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/design-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Obtain SSL Certificate

Using Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d design-assistant.your-company.com
```

---

## Frontend Build

### Build Production Frontend

```bash
cd frontend

# Update API URL
echo "REACT_APP_API_URL=https://design-assistant.your-company.com" > .env.production
echo "REACT_APP_OKTA_ISSUER=https://your-company.okta.com/oauth2/default" >> .env.production
echo "REACT_APP_OKTA_CLIENT_ID=prod-client-id" >> .env.production

# Build
npm run build

# Deploy to server
scp -r build/* user@server:/var/www/design-assistant/
```

---

## AWS Deployment

### Using ECS Fargate

**1. Push Image to ECR:**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag design-assistant:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/design-assistant:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/design-assistant:latest
```

**2. Create ECS Task Definition:**

Use AWS Console or CLI to create task definition with:
- Environment variables from production.env
- EFS volume for persistent data
- CloudWatch Logs for logging

**3. Create ECS Service:**

- Use Application Load Balancer
- Configure health checks
- Set up auto-scaling

**4. Configure Route53:**

Point domain to ALB.

---

## Google Cloud Platform

### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/design-assistant

# Deploy to Cloud Run
gcloud run deploy design-assistant \
  --image gcr.io/PROJECT-ID/design-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat production.env | xargs)"
```

---

## Database Management

### Backup ChromaDB

Schedule regular backups:

```bash
#!/bin/bash
# backup-chromadb.sh

BACKUP_DIR="/backups/chromadb"
DATE=$(date +%Y%m%d-%H%M%S)

# Create backup
tar -czf "$BACKUP_DIR/chromadb-$DATE.tar.gz" /opt/design-assistant/data/chromadb

# Keep only last 30 days
find $BACKUP_DIR -name "chromadb-*.tar.gz" -mtime +30 -delete
```

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup-chromadb.sh
```

### Restore from Backup

```bash
# Stop the application
docker stop design-assistant

# Restore data
tar -xzf /backups/chromadb/chromadb-20240101-020000.tar.gz -C /

# Restart application
docker start design-assistant
```

---

## Monitoring

### Application Monitoring

**Option 1: CloudWatch/Stackdriver**

Built-in cloud provider monitoring.

**Option 2: Prometheus + Grafana**

```bash
# Add metrics endpoint to FastAPI
pip install prometheus-fastapi-instrumentator

# In main.py
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

### Log Aggregation

**Using ELK Stack:**

```yaml
# docker-compose.yml addition
  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    volumes:
      - esdata:/usr/share/elasticsearch/data

  kibana:
    image: kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

---

## Scheduled Tasks

### Auto-Sync Design Data

Create cron job to sync Figma/Slides daily:

```bash
#!/bin/bash
# sync-design-data.sh

API_URL="https://design-assistant.your-company.com"
AUTH_TOKEN="your-service-account-token"

# Sync Figma
curl -X POST "$API_URL/api/sync/figma" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'

# Sync Slides
curl -X POST "$API_URL/api/sync/slides" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

Add to crontab:

```bash
# Daily at 3 AM
0 3 * * * /opt/scripts/sync-design-data.sh
```

---

## Security Hardening

### 1. Environment Variables

Never commit secrets. Use:
- AWS Secrets Manager
- GCP Secret Manager
- HashiCorp Vault
- Kubernetes Secrets

### 2. Network Security

```bash
# Firewall rules (UFW example)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Container Security

```dockerfile
# Use specific versions, not latest
FROM python:3.11.5-slim

# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only filesystem where possible
VOLUME ["/app/data"]
```

### 4. API Security

- Enable rate limiting
- Implement request validation
- Use CORS properly
- Keep dependencies updated

---

## Performance Optimization

### 1. Caching

Add Redis for caching:

```python
# In main.py
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/api/cached-endpoint")
async def cached_endpoint():
    cached = cache.get("key")
    if cached:
        return json.loads(cached)
    # ... compute result
    cache.setex("key", 3600, json.dumps(result))
    return result
```

### 2. Database Optimization

- Use ChromaDB with adequate resources
- Consider PostgreSQL for metadata
- Index frequently queried fields

### 3. Frontend Optimization

```bash
# Build with production optimizations
npm run build

# Serve with compression
# Nginx already handles gzip
```

---

## Disaster Recovery

### Recovery Plan

1. **Application Failure:**
   - Container auto-restart configured
   - Load balancer health checks
   - Backup container ready

2. **Data Loss:**
   - Daily backups
   - Point-in-time recovery
   - Offsite backup storage

3. **Region Failure:**
   - Multi-region deployment
   - DNS failover
   - Data replication

### Test Recovery Regularly

```bash
# Monthly DR drill
./scripts/test-recovery.sh
```

---

## Scaling

### Vertical Scaling

Increase container resources:

```bash
docker run -d \
  --cpus="4" \
  --memory="8g" \
  design-assistant:latest
```

### Horizontal Scaling

Deploy multiple instances behind load balancer:

```yaml
# docker-compose.yml
services:
  app:
    image: design-assistant:latest
    deploy:
      replicas: 3
```

Shared ChromaDB volume required.

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Health check
curl https://design-assistant.your-company.com/api/health

# Test authentication
# Login via browser and test all features
```

### 2. Monitor Logs

```bash
# Docker logs
docker logs -f design-assistant

# Or cloud provider logs
aws logs tail /ecs/design-assistant --follow
```

### 3. Update Documentation

- Update internal wiki
- Notify team
- Provide training if needed

---

## Maintenance

### Regular Updates

```bash
# Monthly: Update dependencies
cd backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

cd ../frontend
npm update
```

### Security Patches

- Subscribe to security advisories
- Test updates in staging first
- Apply critical patches immediately

---

## Rollback Plan

If deployment fails:

```bash
# Rollback to previous version
docker stop design-assistant
docker rm design-assistant
docker run -d \
  --name design-assistant \
  --env-file production.env \
  -v /opt/design-assistant/data:/app/data \
  -p 8000:8000 \
  design-assistant:v1.0.0  # Previous version
```

---

## Support Contacts

- **Infrastructure**: ops-team@company.com
- **Application**: dev-team@company.com
- **Security**: security@company.com

---

## Cost Optimization

### OpenAI API

- Monitor usage in OpenAI dashboard
- Set spending limits
- Cache frequent queries
- Use appropriate model sizes

### Cloud Resources

- Right-size instances
- Use spot/preemptible instances for non-critical
- Review and remove unused resources monthly

---

## Compliance

Ensure compliance with:
- GDPR (if applicable)
- SOC 2
- Company security policies
- Data retention policies

---

## Next Steps

After successful deployment:
1. Monitor performance for first week
2. Gather user feedback
3. Plan feature iterations
4. Schedule regular maintenance windows

