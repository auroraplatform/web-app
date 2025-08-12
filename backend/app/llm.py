# app/llm.py
from openai import OpenAI
from typing import List, Dict
from app.config import settings

class LLMClient:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_sql(self, natural_query: str, schema_context: str) -> Dict:
        """Generate SQL from natural language query"""
        
        system_prompt = """You are a SQL expert specializing in ClickHouse queries.
Given a natural language question and database schema, generate a valid ClickHouse SQL query.

Rules:
1. Only use tables and columns that exist in the provided schema
2. Use proper ClickHouse syntax
3. Include appropriate WHERE clauses for date/time filters
4. Use proper aggregation functions when needed
5. Respond with only the SQL query, no explanations

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
                max_tokens=200
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "sql": sql_query,
                "model_used": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
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