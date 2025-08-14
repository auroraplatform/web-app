"""Sample database schemas for testing purposes"""

# Simple user table schema
SIMPLE_USER_SCHEMA = {
    "name": "users",
    "columns": [
        {"name": "id", "type": "UInt32"},
        {"name": "name", "type": "String"},
        {"name": "email", "type": "String"},
        {"name": "created_at", "type": "DateTime"}
    ]
}

# Complex e-commerce schema
ECOMMERCE_SCHEMA = {
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "username", "type": "String"},
                {"name": "email", "type": "String"},
                {"name": "first_name", "type": "String"},
                {"name": "last_name", "type": "String"},
                {"name": "created_at", "type": "DateTime"},
                {"name": "updated_at", "type": "DateTime"},
                {"name": "is_active", "type": "UInt8"}
            ]
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "user_id", "type": "UInt32"},
                {"name": "order_number", "type": "String"},
                {"name": "total_amount", "type": "Float64"},
                {"name": "status", "type": "String"},
                {"name": "created_at", "type": "DateTime"},
                {"name": "updated_at", "type": "DateTime"}
            ]
        },
        {
            "name": "order_items",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "order_id", "type": "UInt32"},
                {"name": "product_id", "type": "UInt32"},
                {"name": "quantity", "type": "UInt32"},
                {"name": "unit_price", "type": "Float64"},
                {"name": "total_price", "type": "Float64"}
            ]
        },
        {
            "name": "products",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "name", "type": "String"},
                {"name": "description", "type": "String"},
                {"name": "price", "type": "Float64"},
                {"name": "category_id", "type": "UInt32"},
                {"name": "stock_quantity", "type": "UInt32"},
                {"name": "created_at", "type": "DateTime"},
                {"name": "updated_at", "type": "DateTime"}
            ]
        },
        {
            "name": "categories",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "name", "type": "String"},
                {"name": "description", "type": "String"},
                {"name": "parent_id", "type": "Nullable(UInt32)"},
                {"name": "created_at", "type": "DateTime"}
            ]
        }
    ]
}

# Analytics schema with time-series data
ANALYTICS_SCHEMA = {
    "tables": [
        {
            "name": "page_views",
            "columns": [
                {"name": "id", "type": "UInt64"},
                {"name": "user_id", "type": "Nullable(UInt32)"},
                {"name": "page_url", "type": "String"},
                {"name": "referrer", "type": "Nullable(String)"},
                {"name": "user_agent", "type": "String"},
                {"name": "ip_address", "type": "String"},
                {"name": "timestamp", "type": "DateTime64(3)"},
                {"name": "session_id", "type": "String"}
            ]
        },
        {
            "name": "user_sessions",
            "columns": [
                {"name": "session_id", "type": "String"},
                {"name": "user_id", "type": "Nullable(UInt32)"},
                {"name": "start_time", "type": "DateTime64(3)"},
                {"name": "end_time", "type": "Nullable(DateTime64(3))"},
                {"name": "duration_seconds", "type": "Nullable(UInt32)"},
                {"name": "page_count", "type": "UInt32"},
                {"name": "device_type", "type": "String"},
                {"name": "country", "type": "String"}
            ]
        },
        {
            "name": "conversion_events",
            "columns": [
                {"name": "id", "type": "UInt64"},
                {"name": "user_id", "type": "Nullable(UInt32)"},
                {"name": "event_type", "type": "String"},
                {"name": "event_value", "type": "Nullable(Float64)"},
                {"name": "timestamp", "type": "DateTime64(3)"},
                {"name": "session_id", "type": "String"},
                {"name": "properties", "type": "String"}
            ]
        }
    ]
}

# Financial transactions schema
FINANCIAL_SCHEMA = {
    "tables": [
        {
            "name": "transactions",
            "columns": [
                {"name": "transaction_id", "type": "String"},
                {"name": "account_id", "type": "UInt32"},
                {"name": "transaction_type", "type": "String"},
                {"name": "amount", "type": "Decimal(18,2)"},
                {"name": "currency", "type": "String"},
                {"name": "description", "type": "String"},
                {"name": "transaction_date", "type": "Date"},
                {"name": "created_at", "type": "DateTime"},
                {"name": "status", "type": "String"}
            ]
        },
        {
            "name": "accounts",
            "columns": [
                {"name": "account_id", "type": "UInt32"},
                {"name": "customer_id", "type": "UInt32"},
                {"name": "account_type", "type": "String"},
                {"name": "balance", "type": "Decimal(18,2)"},
                {"name": "currency", "type": "String"},
                {"name": "opened_date", "type": "Date"},
                {"name": "status", "type": "String"}
            ]
        },
        {
            "name": "customers",
            "columns": [
                {"name": "customer_id", "type": "UInt32"},
                {"name": "first_name", "type": "String"},
                {"name": "last_name", "type": "String"},
                {"name": "email", "type": "String"},
                {"name": "phone", "type": "String"},
                {"name": "date_of_birth", "type": "Date"},
                {"name": "registration_date", "type": "Date"},
                {"name": "status", "type": "String"}
            ]
        }
    ]
}
