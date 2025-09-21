#!/bin/bash

# PR Review Agent Installation Script
# This script sets up the PR Review Agent with all dependencies

set -e

echo "🤖 PR Review Agent Installation Script"
echo "======================================"

# Check if Python 3.8+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            echo "✅ Python $PYTHON_VERSION found"
        else
            echo "❌ Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        echo "❌ Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3 found"
    else
        echo "❌ pip3 not found. Please install pip"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo "📦 Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y git curl build-essential
        elif command -v yum &> /dev/null; then
            sudo yum install -y git curl gcc gcc-c++ make
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y git curl gcc gcc-c++ make
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install git curl
        else
            echo "⚠️  Homebrew not found. Please install git and curl manually"
        fi
    fi
}

# Create virtual environment
create_venv() {
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created"
}

# Install Python dependencies
install_deps() {
    echo "📚 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Create configuration file
create_config() {
    echo "⚙️  Creating configuration file..."
    
    if [ ! -f "config.yml" ]; then
        cat > config.yml << EOF
server: github
repo: "owner/repository"
pr_id: 1

github:
  token: "your_github_token_here"

gitlab:
  url: "https://gitlab.com"
  token: "your_gitlab_token_here"

bitbucket:
  username: "your_username"
  password: "your_password"
EOF
        echo "✅ Configuration file created (config.yml)"
        echo "⚠️  Please update config.yml with your API keys"
    else
        echo "✅ Configuration file already exists"
    fi
}

# Create environment file
create_env() {
    echo "🔐 Creating environment file..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# AI Integration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# Git Platform Tokens
GITHUB_TOKEN=your_github_token_here
GITLAB_TOKEN=your_gitlab_token_here
BITBUCKET_USERNAME=your_username
BITBUCKET_PASSWORD=your_password

# Optional: Alternative AI Provider
ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
        echo "✅ Environment file created (.env)"
        echo "⚠️  Please update .env with your API keys"
    else
        echo "✅ Environment file already exists"
    fi
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    python -m pytest tests/ -v --tb=short
    echo "✅ Tests completed"
}

# Create logs directory
create_logs_dir() {
    echo "📁 Creating logs directory..."
    mkdir -p logs
    echo "✅ Logs directory created"
}

# Main installation function
main() {
    echo "Starting installation..."
    echo ""
    
    check_python
    check_pip
    install_system_deps
    create_venv
    install_deps
    create_config
    create_env
    create_logs_dir
    run_tests
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update config.yml with your API keys"
    echo "2. Update .env with your environment variables"
    echo "3. Activate the virtual environment: source venv/bin/activate"
    echo "4. Run the agent: python main.py --help"
    echo "5. Start the web dashboard: python demo/web_demo.py"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"
