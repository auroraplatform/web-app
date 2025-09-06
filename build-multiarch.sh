#!/bin/bash

# Aurora Multi-Architecture Docker Build Script
# This script builds and pushes Aurora Docker images for both AMD64 and ARM64 architectures
# Also includes local testing capabilities

set -e

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

# Configuration
IMAGE_NAME="miyasatoka/aurora-web-app"
TAG="latest"
PLATFORMS="linux/amd64,linux/arm64"
LOCAL_IMAGE_NAME="aurora:latest"
LOCAL_CONTAINER_NAME="aurora-web-app"
LOCAL_PORT="8000"

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if buildx is available
    if ! docker buildx version >/dev/null 2>&1; then
        print_error "Docker buildx is not available. Please update Docker to a recent version."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup buildx builder
setup_buildx() {
    print_status "Setting up Docker buildx builder..."
    
    # Check if multiarch builder exists
    if docker buildx ls | grep -q "multiarch"; then
        print_status "Multiarch builder already exists, using it..."
        docker buildx use multiarch
    else
        print_status "Creating new multiarch builder..."
        docker buildx create --name multiarch --use
    fi
    
    # Bootstrap the builder
    print_status "Bootstrapping builder (this may take a moment)..."
    docker buildx inspect --bootstrap
    
    print_success "Buildx setup complete"
}

# Function to build and push multi-architecture image
build_and_push() {
    print_status "Building and pushing multi-architecture Docker image..."
    print_status "Image: ${IMAGE_NAME}:${TAG}"
    print_status "Platforms: ${PLATFORMS}"
    
    # Build and push
    docker buildx build \
        --platform ${PLATFORMS} \
        -t ${IMAGE_NAME}:${TAG} \
        --push .
    
    # Create local tag for testing (don't push this)
    print_status "Creating local tag for testing..."
    docker tag ${IMAGE_NAME}:${TAG} ${LOCAL_IMAGE_NAME}
    
    print_success "Multi-architecture build and push completed!"
}

# Function to verify the image
verify_image() {
    print_status "Verifying multi-architecture image..."
    
    # Wait a moment for DockerHub to process
    sleep 5
    
    # Check available architectures
    print_status "Available architectures for ${IMAGE_NAME}:${TAG}:"
    docker buildx imagetools inspect ${IMAGE_NAME}:${TAG} | grep -A 10 "Manifests:"
    
    print_success "Image verification complete"
}

# Function to check .env file and provide guidance
check_env_file() {
    print_status "Checking for .env file..."
    
    if [ -f ".env" ]; then
        print_success "Found .env file, will use it for local testing"
        ENV_FILE_FLAG="--env-file .env"
    else
        print_warning "No .env file found"
        print_status "Creating default .env file for local testing..."
        
        cat > .env << 'ENVFILE'
# Environment Configuration for Aurora
# Copy this file to .env and modify the values as needed

# ClickHouse Configuration
CLICKHOUSE_HOST=host.docker.internal
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=dev
CLICKHOUSE_PASSWORD=dev
CLICKHOUSE_DATABASE=default

# OpenAI API Key (required for LLM functionality)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Frontend Configuration
FRONTEND_OUT_DIR=/app/frontend/out
ENVFILE
        
        print_success "Default .env file created"
        print_warning "⚠️  Please edit .env file with your actual configuration before testing"
        ENV_FILE_FLAG="--env-file .env"
    fi
}

# Function to test locally
test_locally() {
    print_status "Testing Aurora container locally..."
    
    # Stop and remove existing container if it exists
    if docker ps -a --filter name=${LOCAL_CONTAINER_NAME} | grep -q ${LOCAL_CONTAINER_NAME}; then
        print_status "Stopping existing container..."
        docker stop ${LOCAL_CONTAINER_NAME} 2>/dev/null || true
        docker rm ${LOCAL_CONTAINER_NAME} 2>/dev/null || true
    fi
    
    # Run the container
    print_status "Starting Aurora container locally..."
    docker run -d \
        --name ${LOCAL_CONTAINER_NAME} \
        -p ${LOCAL_PORT}:8000 \
        ${ENV_FILE_FLAG} \
        ${LOCAL_IMAGE_NAME}
    
    # Wait for container to be ready
    print_status "Waiting for container to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:${LOCAL_PORT}/api/health >/dev/null 2>&1; then
            print_success "Container is ready!"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
    
    print_success "🎉 Aurora is running locally!"
    echo
    print_status "🌐 Access the app at: http://localhost:${LOCAL_PORT}"
    print_status "📊 API docs at: http://localhost:${LOCAL_PORT}/docs"
    print_status "🏥 Health check at: http://localhost:${LOCAL_PORT}/api/health"
    echo
    print_status "📋 Container logs (press Ctrl+C to stop following):"
    docker logs -f ${LOCAL_CONTAINER_NAME}
}

# Function to show usage
show_usage() {
    echo "Aurora Multi-Architecture Docker Build Script"
    echo
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo
    echo "Options:"
    echo "  -t, --tag TAG        Docker image tag (default: latest)"
    echo "  -p, --platforms PLATFORMS  Comma-separated list of platforms (default: linux/amd64,linux/arm64)"
    echo "  -h, --help           Show this help message"
    echo
    echo "Commands:"
    echo "  build                 Build and push multi-architecture image (default)"
    echo "  test                  Build and test locally (includes build)"
    echo "  local                 Test existing local image (no build)"
    echo
    echo "Examples:"
    echo "  $0                    # Build with default settings"
    echo "  $0 -t v1.0.0         # Build with specific tag"
    echo "  $0 -p linux/amd64    # Build only for AMD64"
    echo "  $0 test              # Build and test locally"
    echo "  $0 local             # Test existing local image"
    echo
    echo "Default platforms: linux/amd64,linux/arm64"
}

# Function to parse command line arguments
parse_arguments() {
    COMMAND="build"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--tag)
                TAG="$2"
                shift 2
                ;;
            -p|--platforms)
                PLATFORMS="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            build|test|local)
                COMMAND="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to check if we're in the right directory
check_directory() {
    print_status "Checking if we're in the Aurora project directory..."
    
    if [[ ! -f "Dockerfile" ]]; then
        print_error "Dockerfile not found. Please run this script from the Aurora project root directory."
        exit 1
    fi
    
    if [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
        print_error "Backend or frontend directory not found. Please run this script from the Aurora project root directory."
        exit 1
    fi
    
    print_success "Directory check passed"
}

# Main function
main() {
    echo "🐳 Aurora Multi-Architecture Docker Build Script"
    echo "================================================"
    echo
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Show configuration
    print_status "Configuration:"
    echo "  Image: ${IMAGE_NAME}:${TAG}"
    echo "  Local Image: ${LOCAL_IMAGE_NAME}"
    echo "  Platforms: ${PLATFORMS}"
    echo "  Command: ${COMMAND}"
    echo "  Directory: $(pwd)"
    echo
    
    # Run based on command
    case $COMMAND in
        build)
            check_directory
            check_prerequisites
            setup_buildx
            build_and_push
            verify_image
            
            echo
            print_success "🎉 Multi-architecture build completed successfully!"
            print_status "Your Aurora image is now available on DockerHub for both AMD64 and ARM64 platforms."
            print_status "EC2 instances will automatically pull the AMD64 version."
            print_status "ARM64 devices (like your Mac) will automatically pull the ARM64 version."
            ;;
        test)
            check_directory
            check_prerequisites
            setup_buildx
            build_and_push
            verify_image
            check_env_file
            test_locally
            ;;
        local)
            check_env_file
            test_locally
            ;;
    esac
}

# Run main function with all arguments
main "$@"
