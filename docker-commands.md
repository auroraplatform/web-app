# Docker Commands for Web App

This document contains the commands to build and run the web app using Docker.

## Quick Start

### Option 1: Use the build script
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

### Option 2: Manual Docker commands

#### Build the image
```bash
docker build -t web-app:latest .
```

#### Run the container
```bash
docker run -d \
  --name web-app \
  -p 8000:8000 \
  --env-file .env \
  web-app:latest
```

#### Using docker-compose
```bash
docker-compose -f docker-compose.app.yml up -d
```

## Environment Configuration

### Option 1: Use .env file (recommended)
1. Copy the template: `cp env.template .env`
2. Edit `.env` with your configuration values
3. Run the container with `--env-file .env`

### Option 2: Use default values
The container will run with default ClickHouse settings (localhost:8123) if no `.env` file is provided.

### Option 3: Pass environment variables directly
```bash
docker run -d \
  --name web-app \
  -p 8000:8000 \
  -e CLICKHOUSE_HOST=your-host \
  -e CLICKHOUSE_PORT=8123 \
  -e OPENAI_API_KEY=your-key \
  web-app:latest
```

## Container Management

### View logs
```bash
docker logs -f web-app
```

### Stop the container
```bash
docker stop web-app
```

### Remove the container
```bash
docker rm web-app
```

### Restart the container
```bash
docker restart web-app
```

## Access the Application

- **Web App**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Environment Variables

The container uses the following environment variables:

- `CLICKHOUSE_HOST`: ClickHouse server host (default: localhost)
- `CLICKHOUSE_PORT`: ClickHouse server port (default: 8123)
- `CLICKHOUSE_USER`: ClickHouse username (default: empty)
- `CLICKHOUSE_PASSWORD`: ClickHouse password (default: empty)
- `CLICKHOUSE_DATABASE`: ClickHouse database name (default: default)
- `OPENAI_API_KEY`: OpenAI API key for LLM functionality (default: empty)

## Notes

- The container runs on port 8000
- The frontend is served from the built Next.js output in `frontend/out/`
- The backend FastAPI app handles both API requests and serves the frontend
- Health checks are performed every 30 seconds
- The container runs as a non-root user for security
- If no `.env` file exists, the container will use default values
- The `env.template` file provides a starting point for configuration
