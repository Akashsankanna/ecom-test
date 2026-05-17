# Quick AWS Deployment Guide

## One-Command Deployment (Fully Automated)

### Step 1: Configure AWS Credentials
```bash
aws configure
# Enter AWS Access Key ID
# Enter AWS Secret Access Key
# Default region: ap-south-1
# Default output: json
```

### Step 2: Deploy to AWS
```bash
cd /e/ecom/Team-Aryavarse
bash deploy_to_aws.sh
```

The script will:
- ✅ Create security group with open ports
- ✅ Create/use SSH key pair
- ✅ Launch t3.large EC2 instance (50GB storage)
- ✅ Clone your repository
- ✅ Install Docker & Docker Compose
- ✅ Build & start all containers
- ✅ Configure Nginx reverse proxy
- ✅ Show you the deployment details

### Step 3: Access Your Application

After deployment completes, you'll get:
- **Frontend**: `http://YOUR_EC2_IP:8081` or `http://YOUR_EC2_IP` (via Nginx)
- **API Docs**: `http://YOUR_EC2_IP:8000/docs`
- **Keycloak**: `http://YOUR_EC2_IP:8082`

---

## Manual Deployment (If You Prefer)

### 1. Create EC2 Instance via Console
- Go to AWS EC2 Dashboard
- Launch new instance (Ubuntu 22.04, t3.large or bigger)
- Create security group allowing ports: 22, 80, 443, 8000, 8081, 8082, 5432
- Download SSH key pair

### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 3. Install Dependencies
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y docker.io docker-compose git
sudo usermod -aG docker ubuntu
# Log out and log back in
```

### 4. Deploy Application
```bash
git clone https://github.com/YOUR_USERNAME/ecom.git
cd ecom/Team-Aryavarse

# Update backend/.env if needed
# Update CORS_ORIGINS with your EC2 IP

docker-compose -f docker-compose.prod.yml up -d
```

### 5. Setup Nginx 
```bash
sudo apt-get install -y nginx
# Copy nginx config from AWS_DEPLOYMENT_GUIDE.md
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## Monitoring & Maintenance

### View Container Logs
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
docker-compose logs backend -f
docker-compose logs adminpanel -f
docker-compose logs db -f
```

### Database Backup
```bash
# On EC2
docker exec team_db pg_dump -U postgres ecom8 > backup_$(date +%Y%m%d_%H%M%S).sql

# Download to local
scp -i your-key.pem ubuntu@YOUR_EC2_IP:/home/ubuntu/backup_*.sql ./
```

### Restart Containers
```bash
docker-compose restart backend
docker-compose restart adminpanel
docker-compose down
docker-compose up -d --build
```

---

## Production Checklist

- [ ] Change default database passwords
- [ ] Change Keycloak default credentials
- [ ] Update CORS_ORIGINS to your domain
- [ ] Setup SSL/TLS (Let's Encrypt)
- [ ] Configure domain DNS to point to EC2 IP
- [ ] Setup CloudWatch monitoring
- [ ] Enable automated backups
- [ ] Restrict security group CIDR to specific IPs (not 0.0.0.0/0)
- [ ] Setup Application Load Balancer (if multi-instance)
- [ ] Enable VPC Flow Logs for monitoring

---

## Cost Estimation (per month)

- **t3.micro**: ~free
- **50GB EBS storage**: ~$5
- **Data transfer**: ~$0.10-$1
- **Total estimated**: ~$65-$70/month

---

## Troubleshooting

### Cannot SSH to instance
```bash
# Check security group allows port 22
# Check key pair permissions: chmod 400 your-key.pem
# Verify instance status is "running"
```

### Docker containers not starting
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
docker-compose logs
docker-compose restart
```

### Port already in use
```bash
# Stop conflicting container or change docker-compose port mapping
```

### Out of disk space
```bash
docker system prune -a --volumes
df -h  # Check available space
```

---

## Scale Up in Future

### Add Load Balancer
- Create Application Load Balancer in AWS
- Point to EC2 instance
- Configure health checks

### Use RDS Instead of Container DB
```bash
# Create RDS PostgreSQL instance
# Update DB_HOST in backend/.env
# Remove db service from docker-compose
```

### Use ECR for Images
```bash
# Push images to Elastic Container Registry
# Use in docker-compose instead of local build
```
