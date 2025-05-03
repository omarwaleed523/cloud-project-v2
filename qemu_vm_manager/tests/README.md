# QEMU VM Manager Tests

This directory contains unit tests and integration tests for the QEMU VM Manager application.

## Test Structure

- `test_qemu_utils.py` - Unit tests for the qemu_utils module
- `test_integration.py` - Integration tests for the interaction between modules
- `run_tests.py` - Script to run all tests with unittest
- `requirements-test.txt` - Dependencies required for testing

## Running Tests

### Method 1: Using unittest

To run tests using the Python unittest framework:

```bash
# From the main project directory
python qemu_vm_manager/tests/run_tests.py
```

### Method 2: Using pytest (recommended)

For more advanced test execution, you can use pytest:

1. Install test dependencies:
```bash
pip install -r qemu_vm_manager/tests/requirements-test.txt
```

2. Run tests with coverage reports:
```bash
# From the main project directory
pytest qemu_vm_manager/tests/ -v
```

## Coverage Report

The pytest configuration includes code coverage reporting. After running tests with pytest, you can view:

- Terminal coverage summary
- HTML coverage report in the `htmlcov/` directory (open `htmlcov/index.html` in a browser)

## Writing New Tests

### Unit Tests

Unit tests should test individual functions in isolation, using mocks for dependencies.

Example:
```python
@patch('subprocess.run')
def test_create_disk(self, mock_run):
    # Mock a successful disk creation
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "Formatted successfully"
    mock_run.return_value = mock_process
    
    success, message = qemu_utils.create_disk(
        self.test_disk_path, "qcow2", 10
    )
    
    self.assertTrue(success)
    self.assertEqual(message, "Formatted successfully")
```

### Integration Tests

Integration tests should test the interaction between different modules:

Example:
```python
@patch('qemu_utils.create_disk')
def test_create_disk_integration(self, mock_create_disk):
    mock_create_disk.return_value = (True, "Disk created successfully")
    
    # Test the flow from UI to utils and back
    app.create_disk()
    mock_create_disk.assert_called_once()
    # Check other assertions...
```

## Notes for Testing the GUI

The Tkinter GUI is challenging to test automatically. We use the following approaches:

1. Mock all Tkinter components using `unittest.mock`
2. Focus on testing the logic flow through the components
3. Verify that the correct functions are called with the right parameters 