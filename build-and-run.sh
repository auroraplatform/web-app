#!/bin/bash

# Build and run the web app Docker container
# This script builds the Docker image and runs the container

set -e

echo "🐳 Building Docker image for web app..."
docker build -t kocijancic/aurora:latest -t aurora:latest .

echo "🚀 Starting web app container..."

# Check if .env file exists
if [ -f .env ]; then
    echo "📁 Using existing .env file"
    docker run -d \
      --name aurora \
      -p 8000:8000 \
      --env-file .env \
      aurora:latest
else
    echo "⚠️  No .env file found, using default environment variables"
    echo "💡 You can create a .env file with your configuration if needed"
    echo "🔗 Using host.docker.internal to connect to ClickHouse on host machine"
    echo "🔐 Using ClickHouse credentials: username=dev, password=dev"
    docker run -d \
      --name aurora \
      -p 8000:8000 \
      -e CLICKHOUSE_HOST=host.docker.internal \
      -e CLICKHOUSE_PORT=8123 \
      -e CLICKHOUSE_USER=dev \
      -e CLICKHOUSE_PASSWORD=dev \
      -e CLICKHOUSE_DATABASE=default \
      aurora:latest
fi

echo "✅ Web app is starting up!"
echo "🌐 Access the app at: http://localhost:8000"
echo "📊 API docs at: http://localhost:8000/docs"
echo ""
echo "📋 Container logs:"
docker logs -f aurora
