# AWS EC2 Deployment 

## Prerequisites
- AWS Account with billing enabled
- AWS CLI installed locally (`aws --version`)
- AWS credentials configured (`aws configure`)
- Git installed

## Step 1: Create EC2 Instance

### Via AWS CLI
```bash
# Set variables
AWS_REGION="ap-south-1"  # Change to your region
INSTANCE_TYPE="t3.micro"
KEY_NAME="ecom-key"

# Create key pair (one-time)
aws ec2 create-key-pair --key-name $KEY_NAME --region $AWS_REGION --query 'KeyMaterial' --output text > $KEY_NAME.pem
chmod 400 $KEY_NAME.pem

# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name ecom-sg \
  --description "E-commerce app security group" \
  --region $AWS_REGION \
  --query 'GroupId' \
  --output text)

# Add inbound rules
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8081 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 5432 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8082 --cidr 0.0.0.0/0 --region $AWS_REGION

# Launch EC2 instance (Ubuntu 22.04)
INSTANCE_ID=$(aws ec2 run-instances \
  --image-ids ami-0c55b159cbfafe1f0 \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --region $AWS_REGION \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3}' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Security Group: $SG_ID"

# Get public IP
aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $AWS_REGION --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

### Via AWS Console
1. Go to EC2 Dashboard
2. Click "Launch Instances"
3. Select Ubuntu 22.04 LTS (t3.large or larger)
4. Create/select security group with ports: 22, 8000, 8081, 5432, 8082
5. Launch and download key pair

## Step 2: Connect to EC2

```bash
EC2_IP="YOUR_EC2_PUBLIC_IP"
chmod 400 ecom-key.pem
ssh -i ecom-key.pem ubuntu@$EC2_IP
```

## Step 3: Setup EC2 Instance

Run this script on the EC2 instance:

```bash
#!/bin/bash
set -e

echo "=== Updating system ==="
sudo apt-get update && sudo apt-get upgrade -y

echo "=== Installing Docker ==="
sudo apt-get install -y docker.io docker-compose git

echo "=== Adding user to docker group ==="
sudo usermod -aG docker $USER
newgrp docker

echo "=== Cloning repository ==="
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/ecom.git
cd ecom/Team-Aryavarse

echo "=== Creating .env files ==="
# Backend .env
cat > backend/.env << 'EOF'
KEYCLOAK_CLIENT_ID=fastapi-backend
KEYCLOAK_CLIENT_SECRET=3W3z2ZDTgBJJsGxHQzP1Npl7A5TasTQO
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=healthcare
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=admin
RAZORPAY_KEY_ID=rzp_test_SiOwSNyPMiHeZN
RAZORPAY_KEY_SECRET=6ePNLiA1wZMz63xixH0ssmYF
DB_HOST=db
DB_PORT=5432
DB_NAME=ecom8
DB_USER=postgres
DB_PASSWORD=akash45
PAYMENT_ENCRYPTION_KEY=oJ27qvq6r7tBC1StTCrYOV_AnjAyCUPNcdhA0nGmpK4=
CORS_ORIGINS=http://localhost:8081,http://YOUR_EC2_IP:8081
EOF

echo "=== Creating docker-compose.prod.yml ==="
# (Copy production-ready docker-compose config)

echo "=== Starting containers ==="
docker-compose up -d

echo "=== Setup complete ==="
docker-compose ps
```

## Step 4: Update DNS (Optional)

If you have a domain:
```bash
# Point your domain to EC2 public IP
# In your DNS provider (Route53, GoDaddy, etc.):
# A record: yourdomain.com -> EC2_PUBLIC_IP
```

## Step 5: Setup Nginx Reverse Proxy (Recommended)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/ecom > /dev/null <<'EOF'
upstream backend {
    server localhost:8000;
}

upstream adminpanel {
    server localhost:8081;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://adminpanel;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable config
sudo ln -sf /etc/nginx/sites-available/ecom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## Monitoring & Logs

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend -f
docker-compose logs adminpanel -f
docker-compose logs db -f

# Database backup
docker exec team_db pg_dump -U postgres ecom8 > backup.sql

# Restore database
docker exec -i team_db psql -U postgres ecom8 < backup.sql
```

## Troubleshooting

### Containers not starting
```bash
docker-compose down
docker-compose up --build -d
```

### Out of disk space
```bash
docker system prune -a
docker volume prune
```

### Port already in use
```bash
# Change docker-compose ports
# Edit docker-compose.yml and restart
```

## Security Best Practices

1. ✅ Change default passwords (DB, Keycloak)
2. ✅ Use restricted security group CIDR (not 0.0.0.0/0)
3. ✅ Setup SSL/TLS (Let's Encrypt + Certbot)
4. ✅ Enable CloudWatch monitoring
5. ✅ Regular backups of database
6. ✅ Use RDS instead of container database for production

## SSL Certificate Setup (Let's Encrypt)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
# Renew automatically: sudo systemctl enable certbot.timer
```

## Production Checklist

- [ ] Security groups properly configured
- [ ] Database passwords changed from defaults
- [ ] Environment variables set securely
- [ ] Nginx/reverse proxy configured
- [ ] SSL certificate installed
- [ ] Database backups automated
- [ ] CloudWatch monitoring enabled
- [ ] Application logs collected
- [ ] Load balancer configured (if multiple instances)
- [ ] Domain DNS configured
