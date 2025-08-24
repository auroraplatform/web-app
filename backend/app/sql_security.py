import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SQLValidationResult:
    is_safe: bool
    error_message: Optional[str] = None
    allowed_operations: List[str] = None

class SQLSecurityValidator:
    def __init__(self):
        self.allowed_operations = {
            'SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN'
        }
        
        self.forbidden_patterns = [
            r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE)\b',
            r'\b(UNION|EXEC|EXECUTE|xp_|sp_)\b',
            r'--.*$',  # SQL comments
            r'/\*.*?\*/',  # Multi-line comments
            r';\s*$',  # Multiple statements
            r'`.*`',  # Backticks (potential code injection)
            r'<script',  # XSS attempts
        ]
        
        self.allowed_table_patterns = [
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',
            r'^system\.(columns|tables|databases)$',
        ]
    
    def validate_sql(self, sql: str, user_context: Dict = None) -> SQLValidationResult:
        """Validate SQL query for security"""
        if not sql or not sql.strip():
            return SQLValidationResult(False, "Empty SQL query")
        
        sql = sql.strip().upper()
        
        # Check for forbidden operations
        for pattern in self.forbidden_patterns:
            if re.search(pattern, sql, re.IGNORECASE | re.MULTILINE):
                return SQLValidationResult(
                    False, 
                    f"Forbidden operation or pattern detected: {pattern}"
                )

        # Check if operation is allowed
        operation = self._extract_operation(sql)
        if operation not in self.allowed_operations:
            return SQLValidationResult(
                False,
                f"Operation '{operation}' is not allowed. Allowed: {', '.join(self.allowed_operations)}"
            )

        # Check if tautology pattern is present
        if not self._check_for_tautologies(sql):
            return SQLValidationResult(
                False,
                "Potential tautology-based SQL injection detected"
            )
        
        # Extract and validate table names
        table_names = self._extract_table_names(sql)
        if not self._validate_table_names(table_names):
            return SQLValidationResult(
                False,
                f"Invalid table names detected: {table_names}"
            )
        
        # Additional query security checks
        if not self._check_query_complexity(sql):
            return SQLValidationResult(
                False,
                "Query too complex or potentially dangerous"
            )
        
        return SQLValidationResult(True)
    
    def _extract_operation(self, sql: str) -> str:
        """Extract the main SQL operation"""
        words = sql.split()
        return words[0] if words else ""
    
    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        table_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
        matches = re.findall(table_pattern, sql, re.IGNORECASE)
        return [match.strip() for match in matches]
    
    def _validate_table_names(self, table_names: List[str]) -> bool:
        """Validate that table names are safe"""
        for table_name in table_names:
            if not any(re.match(pattern, table_name, re.IGNORECASE) for pattern in self.allowed_table_patterns):
                return False
        return True
    
    def _check_query_complexity(self, sql: str) -> bool:
        """Check if query is too complex"""
        # Limit query length
        if len(sql) > 10000:
            return False
        
        # Limit number of JOINs
        if sql.count('JOIN') > 5:
            return False
        
        # Limit number of subqueries
        if sql.count('(') > 20:
            return False
        
        return True
    
    def _check_for_tautologies(self, sql: str) -> bool:
        """Check for potential tautology-based SQL injection"""
        tautology_patterns = [
            r'\b\d+\s*=\s*\d+\b', # 1=1, 2=2, etc.
            r'\bTRUE\s*=\s*TRUE\b',
            r'\bFALSE\s*=\s*FALSE\b',
            r'\b[a-zA-Z_]\w*\s*=\s*[a-zA-Z_]\w*\b', # variable=variable
        ]

        for pattern in tautology_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return False

        return True

sql_validator = SQLSecurityValidator()
