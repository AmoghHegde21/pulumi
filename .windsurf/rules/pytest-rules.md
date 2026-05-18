---
trigger: manual
---

## Python Version
- Use Python 3.13 syntax and features.
- Ensure compatibility with Python 3.13 only unless otherwise specified.

## Testing Framework
- Use pytest for all unit and integration tests.
- Do NOT use unittest unless explicitly requested.
- Prefer pytest fixtures over setup/teardown methods.
- Use parametrized tests where appropriate.

## Test Directory Structure

- Mirror the source code directory structure inside the `tests/` folder.
- Create corresponding subfolders under `tests/` that match the application structure.
- Generate test files alongside the mirrored structure.

Example source structure:

app/
├── services/
│   └── auth_service.py
├── utils/
│   └── validators.py
└── api/
    └── users.py

Generated test structure:

tests/
├── services/
│   └── test_auth_service.py
├── utils/
│   └── test_validators.py
└── api/
    └── test_users.py

## File Naming Rules

- Prefix all test files with `test_`.
- Keep one primary test file per source module.

Examples:
- auth_service.py → test_auth_service.py
- validators.py → test_validators.py

## Test Organization

- Group tests by feature/module.
- Keep related fixtures near their corresponding test modules.
- Use `conftest.py` for shared fixtures when appropriate.

## Test Naming Conventions
- Test function names must clearly describe behavior.

Examples:
def test_user_login_success():
def test_invalid_email_raises_error():

## Assertions
- Use plain pytest assertions only.

Preferred:
assert result == expected

Avoid:
self.assertEqual(...)

## Mocking
- Use pytest-mock or unittest.mock for mocking.
- Mock external APIs, databases, filesystem operations, and network calls.

## Coverage Expectations
- Generate happy path, edge case, and failure case tests.
- Aim for high coverage on business logic.
- Include exception testing using:
pytest.raises(...)

## Async Code
- Use pytest-asyncio for async tests.
- Mark async tests with:
@pytest.mark.asyncio

## Code Quality
- Keep tests isolated and deterministic.
- Avoid flaky tests.
- Do not add unnecessary sleeps or timing dependencies.

## Output Expectations
When generating tests:
1. Create complete runnable pytest test files.
2. Include required imports.
3. Add fixtures if useful.
4. Avoid placeholder comments.
5. Prefer readable and maintainable tests.

## Example Style

```python
import pytest
from app.calculator import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
    ],
)
def test_add_multiple_cases(a, b, expected):
    assert add(a, b) == expected