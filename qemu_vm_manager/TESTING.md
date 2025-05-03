# Testing Guide for QEMU VM Manager

This document provides a comprehensive guide for testing the QEMU VM Manager application, including unit tests, integration tests, and test coverage.

## Test Structure

The testing framework is organized as follows:

```
qemu_vm_manager/
├── tests/
│   ├── __init__.py           # Package initialization
│   ├── test_qemu_utils.py    # Unit tests for qemu_utils.py
│   ├── test_main.py          # Unit tests for main.py
│   ├── test_integration.py   # Integration tests
│   ├── run_tests.py          # Script to run all tests
│   ├── requirements-test.txt # Test dependencies
│   ├── README.md             # Testing documentation
│   └── ci_workflow.yml       # CI workflow configuration
├── pytest.ini                # pytest configuration
└── requirements.txt          # Project dependencies (includes test deps)
```

## Setting Up the Test Environment

1. Install the required dependencies:

```bash
pip install -r qemu_vm_manager/requirements.txt
```

2. Make sure QEMU is installed and available in your system PATH.

## Running Tests

### Method 1: Using unittest

```bash
# From the project root directory
python qemu_vm_manager/tests/run_tests.py
```

### Method 2: Using pytest (recommended)

```bash
# From the project root directory
pytest qemu_vm_manager/tests/
```

For more verbose output:

```bash
pytest qemu_vm_manager/tests/ -v
```

## Running Specific Test Categories

### Run only unit tests for qemu_utils.py:

```bash
pytest qemu_vm_manager/tests/test_qemu_utils.py
```

### Run only unit tests for main.py:

```bash
pytest qemu_vm_manager/tests/test_main.py
```

### Run only integration tests:

```bash
pytest qemu_vm_manager/tests/test_integration.py
```

## Running Tests with Coverage

To generate a coverage report:

```bash
pytest --cov=qemu_vm_manager qemu_vm_manager/tests/
```

To generate a detailed HTML coverage report:

```bash
pytest --cov=qemu_vm_manager --cov-report=html qemu_vm_manager/tests/
```

Then open `htmlcov/index.html` in your web browser to view the detailed coverage report.

## Test Design Principles

### Unit Tests

- Test individual functions and methods in isolation
- Mock external dependencies like subprocess calls, file operations, and UI components
- Focus on covering all code paths and edge cases
- Each test should be independent and not rely on the state from other tests

### Integration Tests

- Test the interaction between different modules
- Verify that data flows correctly between components
- Mock external dependencies (like QEMU) but test real interactions between your modules
- Focus on complete workflows from the user's perspective

## Maintaining Tests

As you modify the application, be sure to:

1. Update existing tests to reflect changes in functionality
2. Add new tests for any new features or components
3. Run the full test suite before committing changes
4. Monitor test coverage to ensure it remains high

## CI/CD Integration

The `ci_workflow.yml` file provides a GitHub Actions workflow configuration that:

1. Runs tests on multiple operating systems (Windows, Ubuntu)
2. Tests with multiple Python versions (3.9, 3.10, 3.11)
3. Generates and uploads coverage reports
4. Separates unit tests from integration tests

To use this in a GitHub repository:

1. Create a `.github/workflows` directory at the root of your repository
2. Copy the `ci_workflow.yml` file to this directory
3. Push to GitHub to trigger the workflow

## Troubleshooting

### Common Test Failures

1. **Missing QEMU**: Tests may fail if QEMU is not installed or not in the system PATH. Ensure QEMU is properly installed.
2. **Tkinter issues**: Tkinter-related tests may fail in headless environments. These are mocked in the test suite but may require additional configuration in certain CI environments.
3. **File permissions**: Tests that create and delete files may fail due to permission issues. Ensure the tests are running with appropriate permissions.

### Debugging Tests

To debug tests, you can use the `-xvs` flags with pytest:

```bash
pytest qemu_vm_manager/tests/test_qemu_utils.py -xvs
```

This will:
- `-x`: Stop after the first failure
- `-v`: Provide verbose output
- `-s`: Show print statements (don't capture stdout)

## Writing New Tests

When adding new features to the application, consider the following for writing tests:

### For new functions in qemu_utils.py:

1. Add unit tests in `test_qemu_utils.py`
2. Mock all external dependencies
3. Test success and failure paths

### For new UI elements or features in main.py:

1. Add unit tests in `test_main.py`
2. Mock Tkinter components
3. Test the business logic behind the UI

### For new workflows that span multiple components:

1. Add integration tests in `test_integration.py`
2. Focus on the interactions between components 