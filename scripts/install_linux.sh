#!/bin/bash
# Copyright (c) 2025 Saeed Alaediny
# MAMOS Linux Installation Script

set -e

echo "🚀 MAMOS Installation Script"
echo "=============================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please do not run as root"
   exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Check for Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "📦 Docker Compose not found, using docker-compose plugin"
fi

# Navigate to MAMOS directory
MAMOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$MAMOS_DIR"

echo "📂 MAMOS directory: $MAMOS_DIR"

# Create .env file if not exists
if [ ! -f "$MAMOS_DIR/infra/docker/mamos/.env" ]; then
    echo "📝 Creating .env file..."
    cat > "$MAMOS_DIR/infra/docker/mamos/.env" <<EOF
NODE_ENV=production
PORT=4000
DATABASE_URL=file:./prod.db
JWT_SECRET=$(openssl rand -hex 32)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
EOF
    echo "✅ .env file created"
fi

# Start services
echo "🐳 Starting MAMOS services..."
cd "$MAMOS_DIR/infra/docker/mamos"
docker compose -f docker-compose.dev.yml up -d

echo ""
echo "✅ MAMOS installation complete!"
echo ""
echo "📊 Access the services:"
echo "  - Dashboard: http://localhost:3000"
echo "  - Orchestrator API: http://localhost:4000"
echo "  - Grafana: http://localhost:3001 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "📝 Default credentials:"
echo "  - Dashboard: admin@example.com / admin123"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker compose -f $MAMOS_DIR/infra/docker/mamos/docker-compose.dev.yml logs -f"
echo "  - Stop services: docker compose -f $MAMOS_DIR/infra/docker/mamos/docker-compose.dev.yml down"
echo "  - Restart services: docker compose -f $MAMOS_DIR/infra/docker/mamos/docker-compose.dev.yml restart"
echo ""

