#!/bin/bash

# AI Notebook System - Setup Script
# This script sets up the complete development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if required ports are available
check_ports() {
    local ports=("3000" "8000" "5432" "6379" "9000" "9001" "8888")
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use"
        else
            print_success "Port $port is available"
        fi
    done
}

# Check if Ollama is running locally
check_ollama() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Local Ollama is running and accessible"
        
        # Check available models
        local models=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "")
        if [ -n "$models" ]; then
            print_status "Available Ollama models:"
            echo "$models" | while read -r model; do
                echo "  - $model"
            done
        else
            print_warning "No models found in local Ollama"
        fi
    else
        print_error "Local Ollama is not running on port 11434"
        print_status "Please start Ollama locally: ollama serve"
        exit 1
    fi
}

# Create environment file
create_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_success ".env file created"
    else
        print_warning ".env file already exists"
    fi
}

# Start Docker services
start_services() {
    print_status "Starting Docker services..."
    
    # Start core services first
    docker-compose up -d postgres redis minio
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Start remaining services
    docker-compose up -d jupyter-kernel backend frontend
    
    # Wait for all services
    print_status "Waiting for all services to be ready..."
    sleep 20
    
    print_success "All services started successfully"
}

# Show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis: localhost:6379"
    echo "  Jupyter Kernel: http://localhost:8888"
    echo "  Ollama API: http://localhost:11434 (Local)"
    
    echo ""
    print_status "AI Providers Status:"
    echo "  Default Provider: Ollama (Local)"
    echo "  Ollama Models: Check with 'curl http://localhost:11434/api/tags'"
    echo "  OpenAI: Configure OPENAI_API_KEY in .env"
    echo "  Gemini: Configure GEMINI_API_KEY in .env"
}

# Main setup function
main() {
    echo "🚀 Setting up AI Notebook System..."
    
    # Check prerequisites
    check_docker
    check_ports
    check_ollama
    
    # Create environment file
    create_env
    
    # Start services
    start_services
    
    # Show status
    show_status
    
    echo ""
    print_success "🎉 AI Notebook System setup completed successfully!"
    echo ""
    print_status "AI Provider Configuration:"
    echo "  ✅ Ollama (Local) - Ready to use with local models"
    echo "  🔧 OpenAI - Add OPENAI_API_KEY to .env to enable"
    echo "  🔧 Gemini - Add GEMINI_API_KEY to .env to enable"
    echo ""
    print_status "Next steps:"
    echo "1. Update .env file with your API keys (optional)"
    echo "2. Access the application at http://localhost:3000"
    echo "3. Create your first project and start building!"
    echo "4. Use AI chat to generate code and workflows"
    echo ""
    print_status "To manage Ollama models:"
    echo "  - List models: curl http://localhost:11434/api/tags"
    echo "  - Download model: ollama pull <model_name>"
    echo "  - Start Ollama: ollama serve"
    echo ""
    print_status "To stop services: docker-compose down"
    print_status "To view logs: docker-compose logs -f"
    print_status "To restart: docker-compose restart"
}

# Run setup
main "$@" 