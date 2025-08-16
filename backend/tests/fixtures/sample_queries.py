"""Sample natural language queries for testing purposes"""

# Basic SELECT queries
BASIC_QUERIES = [
    "show all users",
    "display all records from users table",
    "get everything from users",
    "select all users",
    "list all users",
    "fetch all user data",
    "retrieve all users",
    "show me all users"
]

# COUNT queries
COUNT_QUERIES = [
    "how many users do we have",
    "count all users",
    "total number of users",
    "user count",
    "how many users are there",
    "total users",
    "count of users",
    "number of users"
]

# Filtered queries
FILTERED_QUERIES = [
    "show users created in the last 30 days",
    "find users who signed up this month",
    "get active users",
    "show users with email ending in @gmail.com",
    "find users created between 2023 and 2024",
    "show users with status active",
    "get users older than 18",
    "find users in California"
]

# JOIN queries
JOIN_QUERIES = [
    "show users and their orders",
    "find users who made purchases",
    "get user details with order information",
    "show users with their order counts",
    "find users who haven't ordered anything",
    "get users and their total spending",
    "show users with their latest order",
    "find users with orders over $100"
]

# Aggregation queries
AGGREGATION_QUERIES = [
    "total revenue by month",
    "average order value by user",
    "count of orders by status",
    "sum of amounts by category",
    "maximum order value",
    "minimum order value",
    "average user age",
    "total users by country"
]

# Time-based queries
TIME_BASED_QUERIES = [
    "users created this week",
    "orders from yesterday",
    "revenue last month",
    "page views today",
    "transactions this quarter",
    "sessions in the last hour",
    "conversions this year",
    "activity in the last 24 hours"
]

# Complex analytical queries
COMPLEX_QUERIES = [
    "find users who made more than 5 orders in the last 6 months",
    "show top 10 customers by total spending",
    "calculate conversion rate by page for the last 30 days",
    "find products with declining sales trend",
    "show user retention rate by month",
    "calculate average session duration by device type",
    "find customers who haven't made a purchase in 90 days",
    "show revenue growth rate by quarter"
]

# Error-prone queries (for testing edge cases)
ERROR_PRONE_QUERIES = [
    "",  # Empty query
    "   ",  # Whitespace only
    "gibberish query with no meaning",
    "show users from nonexistent_table",
    "select * from users where invalid_column = 5",
    "count users group by invalid_field",
    "show users order by nonexistent_column",
    "find users where age > 'invalid_string'"
]

# Business intelligence queries
BI_QUERIES = [
    "what is our customer acquisition cost",
    "show customer lifetime value by segment",
    "calculate churn rate by month",
    "find our most profitable customer segments",
    "show sales performance by region",
    "calculate average order frequency",
    "find products with highest margin",
    "show customer satisfaction trends"
]

# Data quality queries
DATA_QUALITY_QUERIES = [
    "find users with missing email addresses",
    "show duplicate user records",
    "find orders with invalid amounts",
    "show products with missing descriptions",
    "find users with invalid phone numbers",
    "show transactions with future dates",
    "find orders without user_id",
    "show users with invalid age values"
]

# Performance testing queries
PERFORMANCE_QUERIES = [
    "select * from page_views where timestamp > '2024-01-01'",  # Large date range
    "count all records from transactions table",  # Full table scan
    "show all user sessions with detailed page view data",  # Complex join
    "find users with orders in all categories",  # Complex subquery
    "calculate running total for all transactions",  # Window function
    "show all products with full category hierarchy",  # Recursive query
    "find users who visited every page",  # Complex aggregation
    "show complete user journey timeline"  # Multiple joins and aggregations
]
