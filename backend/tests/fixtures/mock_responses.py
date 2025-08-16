"""Mock API responses for testing purposes"""

# Successful SQL generation responses
SUCCESSFUL_SQL_RESPONSES = {
    "basic_select": {
        "success": True,
        "sql": "SELECT * FROM users",
        "model_used": "gpt-3.5-turbo"
    },
    "count_query": {
        "success": True,
        "sql": "SELECT COUNT(*) FROM users",
        "model_used": "gpt-3.5-turbo"
    },
    "filtered_query": {
        "success": True,
        "sql": "SELECT * FROM users WHERE created_at >= NOW() - INTERVAL 30 DAY",
        "model_used": "gpt-3.5-turbo"
    },
    "join_query": {
        "success": True,
        "sql": "SELECT u.*, o.order_id, o.amount FROM users u LEFT JOIN orders o ON u.id = o.user_id",
        "model_used": "gpt-3.5-turbo"
    },
    "aggregation_query": {
        "success": True,
        "sql": "SELECT DATE_TRUNC('month', created_at) as month, SUM(amount) as total_revenue FROM orders GROUP BY month ORDER BY month",
        "model_used": "gpt-3.5-turbo"
    }
}

# Failed SQL generation responses
FAILED_SQL_RESPONSES = {
    "api_error": {
        "success": False,
        "error": "OpenAI API rate limit exceeded. Please try again later."
    },
    "invalid_schema": {
        "success": False,
        "error": "Invalid database schema provided. Cannot generate SQL."
    },
    "unclear_query": {
        "success": False,
        "error": "Query is unclear. Please provide more specific information."
    },
    "unsupported_operation": {
        "success": False,
        "error": "This type of query is not supported by the current system."
    },
    "timeout_error": {
        "success": False,
        "error": "Request timed out. Please try again with a simpler query."
    }
}

# Query explanation responses
QUERY_EXPLANATIONS = {
    "basic_select": "This query retrieves all records from the users table, showing every user in the database.",
    "count_query": "This query counts the total number of users in the database, returning a single number.",
    "filtered_query": "This query finds users who were created in the last 30 days, filtering by creation date.",
    "join_query": "This query combines user information with their order details using a LEFT JOIN to show all users and their orders if they have any.",
    "aggregation_query": "This query calculates monthly revenue by grouping orders by month and summing the amounts, ordered chronologically."
}

# Database query execution responses
DATABASE_RESPONSES = {
    "successful_query": {
        "success": True,
        "data": [
            ["1", "John Doe", "john@example.com", "2024-01-15 10:30:00"],
            ["2", "Jane Smith", "jane@example.com", "2024-01-16 14:20:00"],
            ["3", "Bob Johnson", "bob@example.com", "2024-01-17 09:15:00"]
        ],
        "columns": ["id", "name", "email", "created_at"]
    },
    "empty_result": {
        "success": True,
        "data": [],
        "columns": ["id", "name", "email", "created_at"]
    },
    "large_result": {
        "success": True,
        "data": [["user" + str(i)] for i in range(1000)],
        "columns": ["id"]
    },
    "query_error": {
        "success": False,
        "error": "Syntax error in SQL query: Invalid column name 'nonexistent_column'"
    },
    "connection_error": {
        "success": False,
        "error": "Connection to ClickHouse database failed: Connection refused"
    }
}

# Schema inspection responses
SCHEMA_RESPONSES = {
    "all_tables": {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "name", "type": "String"},
                    {"name": "email", "type": "String"},
                    {"name": "created_at", "type": "DateTime"}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "user_id", "type": "UInt32"},
                    {"name": "amount", "type": "Float64"},
                    {"name": "order_date", "type": "DateTime"}
                ]
            }
        ]
    },
    "single_table": {
        "name": "users",
        "columns": [
            {"name": "id", "type": "UInt32"},
            {"name": "name", "type": "String"},
            {"name": "email", "type": "String"},
            {"name": "created_at", "type": "DateTime"}
        ]
    },
    "table_not_found": {
        "error": "Table 'nonexistent_table' not found in database"
    }
}

# Health check responses
HEALTH_RESPONSES = {
    "healthy": {
        "status": "healthy",
        "clickhouse_connected": True,
        "timestamp": "2024-01-17T10:30:00Z"
    },
    "unhealthy": {
        "status": "unhealthy",
        "clickhouse_connected": False,
        "error": "Database connection failed",
        "timestamp": "2024-01-17T10:30:00Z"
    }
}

# Error responses for different HTTP status codes
HTTP_ERROR_RESPONSES = {
    "400_bad_request": {
        "detail": "Bad Request",
        "status_code": 400
    },
    "401_unauthorized": {
        "detail": "Not authenticated",
        "status_code": 401
    },
    "403_forbidden": {
        "detail": "Not enough permissions",
        "status_code": 403
    },
    "404_not_found": {
        "detail": "Not Found",
        "status_code": 404
    },
    "422_validation_error": {
        "detail": [
            {
                "loc": ["body", "query"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ],
        "status_code": 422
    },
    "500_internal_error": {
        "detail": "Internal server error",
        "status_code": 500
    }
}

# Performance test responses
PERFORMANCE_RESPONSES = {
    "fast_response": {
        "success": True,
        "sql": "SELECT * FROM users LIMIT 10",
        "model_used": "gpt-3.5-turbo",
        "response_time_ms": 150
    },
    "slow_response": {
        "success": True,
        "sql": "SELECT * FROM users JOIN orders ON users.id = orders.user_id JOIN products ON orders.product_id = products.id",
        "model_used": "gpt-3.5-turbo",
        "response_time_ms": 2500
    },
    "timeout_response": {
        "success": False,
        "error": "Request timed out after 30 seconds",
        "response_time_ms": 30000
    }
}

# Smart query processing responses
SMART_QUERY_RESPONSES = {
    "successful_processing": {
        "success": True,
        "sql": "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL 30 DAY",
        "context_used": "users table with creation date information",
        "confidence": 0.95,
        "execution": {
            "success": True,
            "data": [["150"]],
            "columns": ["count"]
        },
        "explanation": "This query counts users created in the last 30 days"
    },
    "low_confidence": {
        "success": True,
        "sql": "SELECT * FROM users WHERE name LIKE '%user%'",
        "context_used": "users table with name field",
        "confidence": 0.65,
        "warning": "Low confidence in query interpretation. Please verify the results.",
        "execution": {
            "success": True,
            "data": [["1", "testuser", "test@example.com"]],
            "columns": ["id", "name", "email"]
        }
    }
}
