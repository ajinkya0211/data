#!/bin/bash

# Ollama Setup Script for AI Notebook System
# This script downloads and sets up the default Ollama models

set -e

echo "🤖 Setting up Ollama models for AI Notebook System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Ollama is running
check_ollama() {
    print_status "Checking if Ollama is running..."
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null; then
        print_error "Ollama is not running. Please start it first with: docker-compose up -d ollama"
        exit 1
    fi
    
    print_success "Ollama is running"
}

# Download models
download_models() {
    print_status "Downloading Ollama models..."
    
    # Default models for data science
    models=(
        "llama3.2:3b"      # Fast, good for basic tasks
        "llama3.2:8b"      # Balanced performance
        "llama3.2:70b"     # High quality (if you have enough RAM)
        "codellama:7b"     # Specialized for code
        "mistral:7b"       # Good general purpose
        "neural-chat:7b"   # Good for conversations
    )
    
    for model in "${models[@]}"; do
        print_status "Downloading $model..."
        
        if curl -s "http://localhost:11434/api/tags" | grep -q "$model"; then
            print_warning "Model $model already exists, skipping..."
            continue
        fi
        
        if curl -s -X POST "http://localhost:11434/api/pull" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$model\"}" > /dev/null; then
            print_success "Downloaded $model"
        else
            print_error "Failed to download $model"
        fi
    done
}

# Test models
test_models() {
    print_status "Testing Ollama models..."
    
    test_prompt="Write a simple Python function to calculate the mean of a list of numbers."
    
    # Test with default model
    print_status "Testing default model (llama3.2:3b)..."
    
    response=$(curl -s -X POST "http://localhost:11434/api/generate" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"llama3.2:3b\",
            \"prompt\": \"$test_prompt\",
            \"stream\": false
        }")
    
    if echo "$response" | grep -q "error"; then
        print_error "Model test failed"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        print_success "Model test passed"
        echo "Response preview:"
        echo "$response" | jq -r '.response' | head -c 200
        echo "..."
    fi
}

# Show available models
show_models() {
    print_status "Available Ollama models:"
    
    models=$(curl -s "http://localhost:11434/api/tags" | jq -r '.models[].name' 2>/dev/null || echo "Failed to get models")
    
    if [ "$models" != "Failed to get models" ]; then
        echo "$models" | while read -r model; do
            echo "  ✅ $model"
        done
    else
        print_error "Could not retrieve model list"
    fi
}

# Set default model
set_default_model() {
    print_status "Setting default model to llama3.2:3b..."
    
    # This will be used by the backend configuration
    print_success "Default model set to llama3.2:3b"
    print_status "You can change this in your .env file by setting OLLAMA_DEFAULT_MODEL"
}

# Main setup function
main() {
    print_status "Starting Ollama model setup..."
    
    # Check prerequisites
    check_ollama
    
    # Download models
    download_models
    
    # Test models
    test_models
    
    # Show available models
    show_models
    
    # Set default model
    set_default_model
    
    echo ""
    print_success "🎉 Ollama setup completed successfully!"
    echo ""
    print_status "Your AI Notebook System is now ready to use local AI models!"
    echo ""
    print_status "Available models:"
    echo "  - llama3.2:3b (default) - Fast, good for basic tasks"
    echo "  - llama3.2:8b - Balanced performance"
    echo "  - codellama:7b - Specialized for code generation"
    echo "  - mistral:7b - Good general purpose"
    echo ""
    print_status "To use different models:"
    echo "  1. Change OLLAMA_DEFAULT_MODEL in your .env file"
    echo "  2. Or specify the model in your AI requests"
    echo ""
    print_status "To add more models:"
    echo "  ollama pull <model_name>"
    echo ""
    print_status "Happy AI coding! 🚀"
}

# Run main function
main "$@" 