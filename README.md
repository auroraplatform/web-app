# Aurora Web App

A natural language query interface that enables users to query Kafka data streams stored in ClickHouse databases using intelligent schema understanding and SQL generation capabilities.

## Overview

Aurora enables users to query ClickHouse databases using natural language. It combines Large Language Models (LLMs) with semantic search to understand database schemas and generate accurate SQL queries from user questions.

## Features

- **Natural Language Querying**: Convert natural language questions into SQL queries
- **Kafka Connection**: Connect to Kafka data streams and query stored data
- **Intelligent Schema Understanding**: Uses embeddings to understand database structure and relationships
- **Smart Context Retrieval**: Automatically identifies relevant tables and columns for queries
- **SQL Security Validation**: Built-in protection against malicious SQL injection
- **Real-time Query Execution**: Direct integration with ClickHouse for immediate results
- **Modern Web Interface**: Clean, responsive UI built with Next.js
- **API Documentation**: Interactive API docs with FastAPI

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query` | POST | Execute SQL query |
| `/api/generate-sql` | POST | Generate SQL from natural language |
| `/api/smart-query` | POST | Process natural language with smart context |
| `/api/schema` | GET | Get complete database schema |
| `/api/schema/{table}` | GET | Get specific table schema |
| `/api/tables` | GET | List all tables |
| `/api/health` | GET | Health check |

## Usage Examples

### Natural Language Query

```bash
curl -X POST "http://localhost:8000/api/smart-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the top 10 customers by revenue"}'
```

### Direct SQL Execution

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM customers LIMIT 10"}'
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CLICKHOUSE_HOST` | ClickHouse server host | `localhost` |
| `CLICKHOUSE_PORT` | ClickHouse server port | `8123` |
| `CLICKHOUSE_USER` | ClickHouse username | `default` |
| `CLICKHOUSE_PASSWORD` | ClickHouse password | (empty) |
| `CLICKHOUSE_DATABASE` | ClickHouse database | `default` |
| `OPENAI_API_KEY` | OpenAI API key | (required) |

## Security

- **SQL Injection Protection**: Validates and sanitizes all SQL queries
- **Input Validation**: Pydantic models for request validation
- **CORS Configuration**: Controlled cross-origin access
- **Error Handling**: Structured error responses without sensitive data exposure
