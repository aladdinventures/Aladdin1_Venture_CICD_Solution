#!/bin/bash
# Copyright (c) 2025 Saeed Alaediny
# MAMOS Agent Installation Script

set -e

echo "🤖 MAMOS Agent Installation Script"
echo "===================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Navigate to agent directory
AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../apps/agent/mamos" && pwd)"
cd "$AGENT_DIR"

echo "📂 Agent directory: $AGENT_DIR"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create config if not exists
if [ ! -f "$AGENT_DIR/agent.yaml" ]; then
    echo "📝 Creating agent.yaml..."
    cp agent.yaml.example agent.yaml
    echo "⚠️  Please edit agent.yaml with your server URL and registration token"
fi

# Test agent
echo ""
echo "🧪 Testing agent connection..."
python3 mamos_agent.py test --config agent.yaml || true

echo ""
echo "✅ Agent installation complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit agent.yaml with your configuration:"
echo "     nano $AGENT_DIR/agent.yaml"
echo ""
echo "  2. Get a registration token from the dashboard"
echo ""
echo "  3. Run the agent:"
echo "     python3 $AGENT_DIR/mamos_agent.py run --config $AGENT_DIR/agent.yaml"
echo ""
echo "  4. (Optional) Set up as systemd service:"
echo "     sudo cp $AGENT_DIR/mamos-agent.service /etc/systemd/system/"
echo "     sudo systemctl enable mamos-agent"
echo "     sudo systemctl start mamos-agent"
echo ""

