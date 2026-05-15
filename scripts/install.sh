#!/bin/bash
# FRIDAY Linux/macOS installer

set -e

echo "🛠️  FRIDAY Installer"
echo "===================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check minimum version
required="3.11"
if [ "$(printf '%s\n' "$required" "$python_version" | sort -V | head -n1)" != "$required" ]; then
    echo "❌ Python 3.11+ required. Please upgrade."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install FRIDAY
echo "Installing FRIDAY..."
pip install -e ".[dev]"

# Create default config
echo "Creating default config..."
cat > friday.yaml << 'EOF'
agent:
  model: gpt-4
  temperature: 0.7
gateway:
  channels:
    - telegram
memory:
  db_path: friday_memory.db
EOF

echo ""
echo "✅ FRIDAY installed successfully!"
echo ""
echo "Next steps:"
echo "  1. Edit friday.yaml with your API keys"
echo "  2. Run: friday --setup"
echo "  3. Run: friday --chat"
echo ""
