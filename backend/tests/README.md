# Backend Testing Infrastructure

This directory contains the comprehensive testing suite for the backend application, following industry best practices and providing extensive coverage of all components.

## 🏗️ Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests (70% of test suite)
│   ├── test_llm.py           # LLM client tests
│   ├── test_database.py      # Database client tests
│   ├── test_schema.py        # Schema inspector tests
│   ├── test_embeddings.py    # Embeddings manager tests
│   └── test_query_processor.py # Query processor tests
├── integration/                # Integration tests (25% of test suite)
│   └── test_api_endpoints.py # API endpoint tests
├── e2e/                       # End-to-end tests (5% of test suite)
│   └── test_full_workflow.py # Complete workflow tests
└── fixtures/                   # Test data and mock responses
    ├── sample_schemas.py      # Database schema fixtures
    ├── sample_queries.py      # Natural language query fixtures
    └── mock_responses.py      # Mock API response fixtures
```

## 🚀 Getting Started

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# Tests with specific markers
pytest -m unit
pytest -m integration
pytest -m e2e
```

### 4. Run Tests in Parallel

```bash
# Run tests in parallel (faster execution)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## 📊 Test Coverage

The testing suite aims for:
- **Overall Coverage**: 90%+
- **Critical Paths**: 95%+
- **Error Handling**: 100%

### Coverage Reports

After running tests, coverage reports are generated in:
- **Terminal**: `--cov-report=term-missing`
- **HTML**: `--cov-report=html` (generates `htmlcov/` directory)
- **XML**: `--cov-report=xml` (for CI/CD integration)

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation with mocked dependencies:

- **LLM Client**: SQL generation, prompt formatting, error handling
- **Database Client**: Query execution, connection handling, result formatting
- **Schema Inspector**: Schema parsing, validation, metadata extraction
- **Embeddings Manager**: Vector operations, similarity search, cache management
- **Query Processor**: Natural language processing, context retrieval, SQL generation

### Integration Tests (`tests/integration/`)

Test component interactions and API endpoints:

- **API Endpoints**: All FastAPI endpoints, request/response validation
- **Database Integration**: Real database interactions, schema operations
- **LLM Integration**: OpenAI API interactions, end-to-end SQL generation

### End-to-End Tests (`tests/e2e/`)

Test complete user workflows and system behavior:

- **Natural Language → SQL → Execution**: Complete query processing pipeline
- **Schema Embedding → Context Retrieval**: Full context building workflow
- **Error Handling**: System-wide error scenarios and recovery
- **Performance**: Load testing and response time validation

## 🔧 Test Configuration

### pytest.ini

Configuration file with:
- Test discovery patterns
- Coverage settings
- Custom markers
- Warning filters

### conftest.py

Shared fixtures and configuration:
- Mock objects for external dependencies
- Sample data fixtures
- Test client setup
- Async test configuration

## 📝 Writing Tests

### Test Naming Convention

```python
def test_function_name_scenario():
    """Test description"""
    # Test implementation
```

### Test Class Structure

```python
class TestComponentName:
    """Test cases for ComponentName class"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        # Setup code
    
    def test_specific_functionality(self):
        """Test specific functionality"""
        # Test implementation
```

### Using Fixtures

```python
def test_with_fixtures(mock_clickhouse, sample_schema):
    """Test using shared fixtures"""
    # Test implementation using fixtures
```

### Mocking External Dependencies

```python
@patch('app.module.external_service')
def test_with_mocked_service(mock_service):
    """Test with mocked external service"""
    mock_service.return_value = "mocked_response"
    # Test implementation
```

## 🎯 Test Data Management

### Fixtures (`tests/fixtures/`)

- **Sample Schemas**: Various database schema configurations
- **Sample Queries**: Natural language queries for testing
- **Mock Responses**: Expected API responses and error scenarios

### Test Data Factories

Use factory-boy for complex object creation:

```python
from factory import Factory, Faker

class UserFactory(Factory):
    class Meta:
        model = dict
    
    name = Faker('name')
    email = Faker('email')
    created_at = Faker('date_time')
```

## 🚦 CI/CD Integration

### GitHub Actions

The testing suite is designed to integrate with CI/CD pipelines:

```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-test.txt
      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Coverage Thresholds

- **Minimum Coverage**: 80% (configurable in pytest.ini)
- **Coverage Reports**: HTML, XML, and terminal output
- **Coverage Failures**: Tests will fail if coverage drops below threshold

## 🔍 Debugging Tests

### Running Single Tests

```bash
# Run specific test file
pytest tests/unit/test_llm.py

# Run specific test method
pytest tests/unit/test_llm.py::TestLLMClient::test_generate_sql_success

# Run tests matching pattern
pytest -k "test_generate_sql"
```

### Verbose Output

```bash
# Show test details
pytest -v

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

### Debugging with pdb

```python
import pdb; pdb.set_trace()  # Add breakpoint in test
```

## 📈 Performance Testing

### Response Time Benchmarks

- **Unit Tests**: < 30 seconds total execution
- **API Endpoints**: < 100ms response time
- **SQL Generation**: < 2 seconds for complex queries

### Load Testing

```python
def test_performance_under_load():
    """Test performance under load"""
    responses = []
    for i in range(100):
        response = client.post("/generate-sql", json={"query": f"query {i}"})
        responses.append(response)
    
    # Verify all responses within acceptable time
    for response in responses:
        assert response.status_code == 200
```

## 🧹 Test Maintenance

### Regular Tasks

- **Monthly**: Review test coverage and add missing scenarios
- **Quarterly**: Update test data and mock responses
- **Bi-annually**: Performance benchmarking and optimization
- **Annually**: Testing strategy review and tool updates

### Adding New Tests

1. **Unit Tests**: Add to appropriate module in `tests/unit/`
2. **Integration Tests**: Add to `tests/integration/` or create new file
3. **E2E Tests**: Add to `tests/e2e/` for complete workflow testing
4. **Fixtures**: Add new test data to `tests/fixtures/`

### Test Documentation

- **Docstrings**: Clear description of what each test validates
- **Comments**: Explain complex test logic and assertions
- **README**: Keep this file updated with new testing patterns

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes the backend directory
2. **Mock Issues**: Check that mocks are properly configured in conftest.py
3. **Coverage Issues**: Verify that all code paths are being tested
4. **Performance Issues**: Use pytest-profiling for performance analysis

### Getting Help

- Check test output for detailed error messages
- Review fixture configurations in conftest.py
- Ensure all dependencies are installed from requirements-test.txt
- Check pytest.ini configuration for custom settings

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Coverage Plugin](https://pytest-cov.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
