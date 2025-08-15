# app/llm.py
from openai import OpenAI
from typing import Dict
import json
from app.config import settings

class LLMClient:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_sql(self, natural_query: str, schema_context: str) -> Dict:
        """Generate SQL from natural language query"""
        
        system_prompt = """You are a SQL expert specializing in ClickHouse queries.
Given a natural language question and database schema, generate a valid ClickHouse SQL query.

CRITICAL RULES:
1. ALWAYS use parameterized queries with {param_name:Type} syntax
2. NEVER include user input directly in the SQL string
3. Use parameters for ALL user-provided values (names, dates, numbers, etc.)
4. Only use tables and columns that exist in the provided schema
5. Use proper ClickHouse syntax with type annotations
6. Extract parameter values from the natural language query
7. Return response as JSON with 'sql' and 'parameters' fields
8. When you're including a value to the sql statement, always add LIKE %<value>%

Parameter format: {param_name:Type}
- String values: {name:String}
- Numbers: {count:UInt32}, {amount:Float64}
- Dates: {start_date:Date}, {timestamp:DateTime}

Response format:
{
  "sql": "SELECT * FROM events WHERE user_name = {user_name:String}",
  "parameters": {
    "user_name": "%John%"
  }
}

Examples:
- "Show events for user John" → 
  {
    "sql": "SELECT * FROM events WHERE user_name LIKE {user_name:String}",
    "parameters": {"user_name": "%John%"}
  }
- "Count orders with amount greater than 100" →
  {
    "sql": "SELECT COUNT(*) FROM orders WHERE amount > {min_amount:Float64}",
    "parameters": {"min_amount": 100.0}
  }

Schema context will be provided below."""

        user_prompt = f"""
Schema:
{schema_context}

Natural language query: {natural_query}

Generate the ClickHouse SQL query:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300 # prevent truncated response
            )
            
            response_content = self.sanitize_sql(response.choices[0].message.content.strip())

            try:
                parsed_response = json.loads(response_content)
                sql_query = self.sanitize_sql(parsed_response.get("sql", ""))
                parameters = parsed_response.get("parameters", {})

                return {
                    "success": True,
                    "sql": sql_query,
                    "parameters": parameters,
                    "model_used": self.model
                }
            
            except json.JSONDecodeError as e:
                # Fallback: try to extract SQL if JSON parsing fails
                print(f"JSON parsing failed: {e}")
                sql_query = self.sanitize_sql(response_content)
                return {
                    "success": True,
                    "sql": sql_query,
                    "parameters": {},
                    "model_used": self.model,
                    "warning": "Could not parse parameters from response"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sanitize_sql(self, sql: str) -> str:
        sanitized_query = ' '.join(sql.split())
        sanitized_query = sanitized_query.replace(";", "")
        return sanitized_query

    def explain_query(self, sql_query: str) -> str:
        """Generate natural language explanation of SQL query"""
        prompt = f"""Explain this ClickHouse SQL query in simple terms:

{sql_query}

Explanation:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

llm_client = LLMClient()
