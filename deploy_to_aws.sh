#!/bin/bash

###############################################################################
# AWS EC2 Deployment Script for E-Commerce Application
# Usage: bash deploy_to_aws.sh
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== E-Commerce AWS EC2 Deployment Script ===${NC}"

# ==============================================================================
# CONFIGURATION
# ==============================================================================

AWS_REGION="${AWS_REGION:-ap-south-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.large}"
KEY_NAME="${KEY_NAME:-ecom-key}"
SECURITY_GROUP_NAME="ecom-sg"
SECURITY_GROUP_DESC="E-commerce app security group"
REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/ecom.git}"
REPO_BRANCH="main"

echo -e "${YELLOW}Configuration:${NC}"
echo "AWS Region: $AWS_REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Key Pair: $KEY_NAME"
echo "Repository: $REPO_URL"

# ==============================================================================
# STEP 1: Create Security Group
# ==============================================================================

echo -e "\n${YELLOW}[1/5] Creating Security Group...${NC}"

# Check if security group exists
SG_EXISTS=$(aws ec2 describe-security-groups \
  --region $AWS_REGION \
  --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
  --query 'SecurityGroups[0].GroupId' \
  --output text 2>/dev/null || echo "None")

if [ "$SG_EXISTS" != "None" ] && [ "$SG_EXISTS" != "" ]; then
  SG_ID=$SG_EXISTS
  echo "Security group already exists: $SG_ID"
else
  SG_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "$SECURITY_GROUP_DESC" \
    --region $AWS_REGION \
    --query 'GroupId' \
    --output text)
  echo -e "${GREEN}✓ Created security group: $SG_ID${NC}"
fi

# Add inbound rules
PORTS=(22 8000 8081 5432 8082 80 443)
for PORT in "${PORTS[@]}"; do
  aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port $PORT \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || echo "Port $PORT already authorized"
done

echo -e "${GREEN}✓ Security group rules configured${NC}"

# ==============================================================================
# STEP 2: Create Key Pair
# ==============================================================================

echo -e "\n${YELLOW}[2/5] Setting up Key Pair...${NC}"

if [ ! -f "${KEY_NAME}.pem" ]; then
  aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --region $AWS_REGION \
    --query 'KeyMaterial' \
    --output text > ${KEY_NAME}.pem
  chmod 400 ${KEY_NAME}.pem
  echo -e "${GREEN}✓ Created key pair: ${KEY_NAME}.pem${NC}"
else
  echo "Key pair already exists: ${KEY_NAME}.pem"
fi

# ==============================================================================
# STEP 3: Launch EC2 Instance
# ==============================================================================

echo -e "\n${YELLOW}[3/5] Launching EC2 Instance...${NC}"

# Get latest Ubuntu 22.04 AMI
AMI_ID=$(aws ec2 describe-images \
  --region $AWS_REGION \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].[ImageId]' \
  --output text)

INSTANCE_ID=$(aws ec2 run-instances \
  --image-ids $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --region $AWS_REGION \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=50,VolumeType=gp3}' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ecom-app}]" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo -e "${GREEN}✓ Launched instance: $INSTANCE_ID${NC}"
echo "Waiting for instance to start..."

# Wait for instance to have public IP
sleep 10
EC2_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region $AWS_REGION \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

while [ "$EC2_IP" = "None" ] || [ -z "$EC2_IP" ]; do
  sleep 5
  EC2_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $AWS_REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)
done

echo -e "${GREEN}✓ Instance public IP: $EC2_IP${NC}"

# ==============================================================================
# STEP 4: Wait for SSH and Install Dependencies
# ==============================================================================

echo -e "\n${YELLOW}[4/5] Waiting for instance to be ready...${NC}"

# Wait for SSH to be available
for i in {1..60}; do
  if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i ${KEY_NAME}.pem ubuntu@$EC2_IP "echo 'SSH ready'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH connection ready${NC}"
    break
  fi
  echo "Waiting for SSH... ($i/60)"
  sleep 5
done

# Create initialization script
cat > init_instance.sh << 'INITEOF'
#!/bin/bash
set -e

echo "=== Updating system packages ==="
sudo apt-get update && sudo apt-get upgrade -y

echo "=== Installing Docker and Docker Compose ==="
sudo apt-get install -y docker.io docker-compose git curl

echo "=== Adding user to docker group ==="
sudo usermod -aG docker ubuntu
newgrp docker << 'GRPEOF'

echo "=== Cloning repository ==="
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/ecom.git
cd ecom/Team-Aryavarse

echo "=== Creating environment files ==="
if [ ! -f backend/.env ]; then
  cat > backend/.env << 'ENVEOF'
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
ENVEOF
fi

echo "=== Building and starting containers ==="
docker-compose -f docker-compose.prod.yml up -d

echo "=== Waiting for services to start ==="
sleep 10

echo "=== Container status ==="
docker-compose ps

echo "=== Setup complete ==="
GRPEOF
INITEOF

# Transfer and execute initialization script
scp -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem init_instance.sh ubuntu@$EC2_IP:/tmp/
ssh -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem ubuntu@$EC2_IP "bash /tmp/init_instance.sh"

echo -e "${GREEN}✓ Instance initialized${NC}"

# ==============================================================================
# STEP 5: Configure Nginx Reverse Proxy
# ==============================================================================

echo -e "\n${YELLOW}[5/5] Configuring Nginx Reverse Proxy...${NC}"

cat > nginx_config.sh << 'NGINXEOF'
#!/bin/bash

echo "=== Installing Nginx ==="
sudo apt-get install -y nginx

echo "=== Creating Nginx configuration ==="
sudo tee /etc/nginx/sites-available/ecom > /dev/null <<'CONFEOF'
upstream backend {
    server localhost:8000;
}

upstream adminpanel {
    server localhost:8081;
}

server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 50M;

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Admin panel
    location / {
        proxy_pass http://adminpanel/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
CONFEOF

echo "=== Enabling Nginx configuration ==="
sudo ln -sf /etc/nginx/sites-available/ecom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "✓ Nginx configured and running"
NGINXEOF

scp -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem nginx_config.sh ubuntu@$EC2_IP:/tmp/
ssh -o StrictHostKeyChecking=no -i ${KEY_NAME}.pem ubuntu@$EC2_IP "bash /tmp/nginx_config.sh"

echo -e "${GREEN}✓ Nginx configured${NC}"

# ==============================================================================
# DEPLOYMENT COMPLETE
# ==============================================================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🎉 Deployment Complete! 🎉                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}Access Information:${NC}"
echo "SSH Command: ssh -i ${KEY_NAME}.pem ubuntu@$EC2_IP"
echo "Frontend:    http://$EC2_IP:8081 (or http://$EC2_IP via Nginx)"
echo "Backend:     http://$EC2_IP:8000/docs"
echo "Keycloak:    http://$EC2_IP:8082"
echo "Database:    $EC2_IP:5432"

echo -e "\n${YELLOW}Instance Details:${NC}"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP:   $EC2_IP"
echo "Region:      $AWS_REGION"
echo "Key Pair:    ${KEY_NAME}.pem"

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo "# View logs"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$EC2_IP 'docker-compose -f Team-Aryavarse/docker-compose.prod.yml logs -f'"

echo -e "\n# Backup database"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$EC2_IP 'docker exec team_db pg_dump -U postgres ecom8 > backup.sql'"

echo -e "\n# Stop containers"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$EC2_IP 'docker-compose -f Team-Aryavarse/docker-compose.prod.yml down'"

echo -e "\n# Restart containers"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$EC2_IP 'docker-compose -f Team-Aryavarse/docker-compose.prod.yml up -d'"

# Save configuration for future reference
cat > deployment_info.txt << INFOEOF
===== Deployment Information =====
Instance ID: $INSTANCE_ID
Public IP: $EC2_IP
Region: $AWS_REGION
Key Pair: ${KEY_NAME}.pem
Security Group: $SG_ID
Instance Type: $INSTANCE_TYPE
Created: $(date)
INFOEOF

echo -e "\n${GREEN}✓ Deployment info saved to: deployment_info.txt${NC}"
