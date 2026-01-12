# Unit Tests for File Storage Service

## Overview

This directory contains comprehensive unit tests for the File Storage Service backend. The tests cover critical functionality including:

- **Password Utilities** (`test_password_utils.py`)
  - Password hashing and verification (bcrypt)
  - Password strength validation
  - JWT token creation and validation
  - Token expiration handling

- **Repository Layer** (`test_repositories.py`)
  - UserRepository CRUD operations
  - FileRepository CRUD operations
  - Pagination and filtering
  - Soft deletion

- **Authentication Service** (`test_auth_service.py`)
  - User registration flow
  - Login authentication
  - Email validation
  - Password strength requirements
  - JWT token generation
  - User status checking

## Prerequisites

Before running tests, ensure you have:

1. **PostgreSQL test database** set up:
   ```bash
   # Create test database
   createdb file_storage_test
   ```

2. **Python dependencies** installed:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment variables** configured in `.env`:
   ```bash
   DATABASE_URL=postgresql+psycopg2://postgres:123@localhost:5432/file_storage
   SECRET_KEY=your-secret-key-change-in-production-12345
   ```

## Running Tests

### Run All Unit Tests

```bash
cd backend
pytest tests/unit/ -v
```

### Run Specific Test File

```bash
# Test password utilities
pytest tests/unit/test_password_utils.py -v

# Test repositories
pytest tests/unit/test_repositories.py -v

# Test authentication service
pytest tests/unit/test_auth_service.py -v
```

### Run Specific Test Class

```bash
# Test only PasswordUtils
pytest tests/unit/test_password_utils.py::TestPasswordUtils -v

# Test only UserRepository
pytest tests/unit/test_repositories.py::TestUserRepository -v
```

### Run Specific Test Method

```bash
pytest tests/unit/test_password_utils.py::TestPasswordUtils::test_hash_password_creates_valid_hash -v
```

### Run with Coverage Report

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Tests in Parallel (faster)

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest tests/unit/ -n 4 -v
```

## Test Output Examples

### Successful Test Run

```
================================ test session starts =================================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.0.0
rootdir: /backend
collected 45 items

tests/unit/test_password_utils.py ..................            [ 40%]
tests/unit/test_repositories.py ....................            [ 84%]
tests/unit/test_auth_service.py .......                         [100%]

================================= 45 passed in 3.21s ==================================
```

### Failed Test Example

```
_________________________________ FAILURES _________________________________
_______ TestPasswordUtils.test_hash_password_creates_valid_hash ________

    def test_hash_password_creates_valid_hash(self):
        password = "TestPassword123!"
        hashed = PasswordUtils.hash_password(password)
>       assert hashed.startswith("$2b$")
E       AssertionError: assert False

_________________________________ short test summary info __________________________________
FAILED tests/unit/test_password_utils.py::TestPasswordUtils::test_hash_password_creates_valid_hash
```

## Test Structure

Each test file follows this structure:

```python
class TestClassName:
    """Test suite for ClassName"""
    
    def test_method_name_scenario(self, fixtures):
        """Test that method does X when Y happens"""
        # Arrange
        setup_data = create_test_data()
        
        # Act
        result = method_under_test(setup_data)
        
        # Assert
        assert result == expected_value
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `db` - Database session (function-scoped, rolled back after each test)
- `client` - FastAPI test client
- `test_user` - Pre-created test user
- `user_token` - Authentication token for test user

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Descriptive Names**: Use clear test method names like `test_login_with_invalid_password`
3. **One Assertion per Test**: Preferably test one behavior per test method
4. **Use Fixtures**: Reuse setup code via pytest fixtures
5. **Clean Database**: Tests use transactions that are rolled back automatically

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=app
```

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed
```

**Solution**: Ensure PostgreSQL is running and test database exists:
```bash
sudo service postgresql start
creatdb file_storage_test
```

### Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Run tests from the `backend` directory:
```bash
cd backend
pytest tests/unit/
```

### Test Database Already Exists

```
psycopg2.errors.DuplicateDatabase: database "file_storage_test" already exists
```

**Solution**: This is normal - tests will use the existing database.

## Contributing

When adding new functionality:

1. Write tests FIRST (Test-Driven Development)
2. Ensure all existing tests pass
3. Add tests for edge cases and error handling
4. Aim for >80% code coverage
5. Run tests before committing:
   ```bash
   pytest tests/unit/ -v
   ```

## Test Coverage Goals

- **Utilities**: 100% coverage (critical security functions)
- **Repositories**: >90% coverage (data access layer)
- **Services**: >85% coverage (business logic)
- **Overall**: >80% coverage

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Testing FastAPI Applications](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
