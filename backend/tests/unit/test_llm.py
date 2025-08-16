import pytest
from unittest.mock import Mock, patch, MagicMock
from app.llm import LLMClient

class TestLLMClient:
    """Test cases for LLMClient class"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        with patch('app.llm.settings') as mock_settings:
            mock_settings.openai_api_key = "test-api-key"
            self.llm_client = LLMClient()
    
    def test_init(self):
        """Test LLMClient initialization"""
        assert self.llm_client.model == "gpt-3.5-turbo"
        assert self.llm_client.client is not None
    
    @patch('app.llm.OpenAI')
    def test_init_with_api_key(self, mock_openai):
        """Test LLMClient initialization with API key"""
        mock_openai.return_value = Mock()
        client = LLMClient()
        mock_openai.assert_called_once_with(api_key="test-api-key")
    
    def test_generate_sql_success(self, sample_schema):
        """Test successful SQL generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response):
            result = self.llm_client.generate_sql("show all users", str(sample_schema))
        
        assert result["success"] is True
        assert "SELECT * FROM users" in result["sql"]
        assert result["model_used"] == "gpt-3.5-turbo"
    
    def test_generate_sql_api_error(self, sample_schema):
        """Test SQL generation with API error"""
        with patch.object(self.llm_client.client.chat.completions, 'create', side_effect=Exception("API Error")):
            result = self.llm_client.generate_sql("show all users", str(sample_schema))
        
        assert result["success"] is False
        assert "API Error" in result["error"]
    
    def test_generate_sql_prompt_formatting(self, sample_schema):
        """Test that prompts are properly formatted"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            self.llm_client.generate_sql("show all users", str(sample_schema))
            
            # Verify the create method was called with correct parameters
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            
            # Check system prompt
            system_message = call_args[1]['messages'][0]
            assert system_message['role'] == 'system'
            assert "ClickHouse" in system_message['content']
            assert "SQL expert" in system_message['content']
            
            # Check user prompt
            user_message = call_args[1]['messages'][1]
            assert user_message['role'] == 'user'
            assert "show all users" in user_message['content']
            assert str(sample_schema) in user_message['content']
    
    def test_generate_sql_temperature_and_tokens(self, sample_schema):
        """Test that temperature and max_tokens are set correctly"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            self.llm_client.generate_sql("show all users", str(sample_schema))
            
            call_args = mock_create.call_args
            assert call_args[1]['temperature'] == 0.1
            assert call_args[1]['max_tokens'] == 200
    
    def test_generate_sql_sql_sanitization(self, sample_schema):
        """Test that SQL is properly sanitized (whitespace normalized)"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT    *    FROM    users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response):
            result = self.llm_client.generate_sql("show all users", str(sample_schema))
        
        assert result["sql"] == "SELECT * FROM users"
    
    def test_explain_query_success(self):
        """Test successful query explanation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This query selects all users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response):
            explanation = self.llm_client.explain_query("SELECT * FROM users")
        
        assert "selects all users" in explanation
    
    def test_explain_query_api_error(self):
        """Test query explanation with API error"""
        with patch.object(self.llm_client.client.chat.completions, 'create', side_effect=Exception("API Error")):
            explanation = self.llm_client.explain_query("SELECT * FROM users")
        
        assert "Error generating explanation" in explanation
        assert "API Error" in explanation
    
    def test_explain_query_prompt_formatting(self):
        """Test that explanation prompts are properly formatted"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This query selects all users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            self.llm_client.explain_query("SELECT * FROM users")
            
            call_args = mock_create.call_args
            user_message = call_args[1]['messages'][0]
            assert user_message['role'] == 'user'
            assert "SELECT * FROM users" in user_message['content']
            assert "Explain this ClickHouse SQL query" in user_message['content']
    
    def test_explain_query_temperature(self):
        """Test that explanation uses correct temperature"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This query selects all users"))]
        
        with patch.object(self.llm_client.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            self.llm_client.explain_query("SELECT * FROM users")
            
            call_args = mock_create.call_args
            assert call_args[1]['temperature'] == 0.3
            assert call_args[1]['max_tokens'] == 150
