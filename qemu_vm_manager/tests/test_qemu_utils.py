import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys
import json

# Add parent directory to path so we can import qemu_utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import qemu_utils

class TestQemuUtils(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_disk_path = os.path.join(self.test_dir, "test_disk.qcow2")
        
        # Sample test data
        self.test_vm_config = {
            "name": "test_vm",
            "cpu": 1,
            "memory": 1024
        }
        
        self.test_disk_config = {
            "path": self.test_disk_path,
            "format": "qcow2",
            "size": 10
        }
        
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_dir)

    @patch('subprocess.run')
    def test_check_qemu_available_success(self, mock_run):
        # Mock a successful subprocess run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "QEMU emulator version 5.0.0"
        mock_run.return_value = mock_process
        
        available, message = qemu_utils.check_qemu_available()
        
        self.assertTrue(available)
        self.assertEqual(message, "QEMU emulator version 5.0.0")
        mock_run.assert_called_once_with(
            ["qemu-img", "--version"], 
            stdout=-1, 
            stderr=-1, 
            text=True
        )
    
    @patch('subprocess.run')
    def test_check_qemu_available_failure(self, mock_run):
        # Mock a failed subprocess run (non-zero return code)
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Command failed"
        mock_run.return_value = mock_process
        
        available, message = qemu_utils.check_qemu_available()
        
        self.assertFalse(available)
        self.assertEqual(message, "QEMU is installed but qemu-img command failed")
    
    @patch('subprocess.run')
    def test_check_qemu_not_found(self, mock_run):
        # Mock a FileNotFoundError
        mock_run.side_effect = FileNotFoundError("No such file or directory")
        
        available, message = qemu_utils.check_qemu_available()
        
        self.assertFalse(available)
        self.assertEqual(message, "QEMU is not installed or not in the system PATH")
    
    def test_parse_disk_info(self):
        sample_output = """image: test_disk.qcow2
file format: qcow2
virtual size: 10G (10737418240 bytes)
disk size: 196K
cluster_size: 65536
Format specific information:
    compat: 1.1
    lazy refcounts: false
    refcount bits: 16
    corrupt: false"""
        
        result = qemu_utils.parse_disk_info(sample_output)
        
        self.assertEqual(result["image"], "test_disk.qcow2")
        self.assertEqual(result["file format"], "qcow2")
        self.assertEqual(result["virtual size"], "10G (10737418240 bytes)")
        self.assertEqual(result["disk size"], "196K")
    
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
        mock_run.assert_called_once_with(
            ["qemu-img", "create", "-f", "qcow2", self.test_disk_path, "10G"],
            stdout=-1,
            stderr=-1,
            text=True
        )
    
    @patch('os.path.exists')
    @patch('os.remove')
    def test_delete_disk_success(self, mock_remove, mock_exists):
        # Mock that file exists and is removed successfully
        mock_exists.return_value = True
        
        success, message = qemu_utils.delete_disk(self.test_disk_path)
        
        self.assertTrue(success)
        self.assertEqual(message, f"Disk deleted successfully: {self.test_disk_path}")
        mock_remove.assert_called_once_with(self.test_disk_path)
    
    @patch('os.path.exists')
    def test_delete_disk_not_found(self, mock_exists):
        # Mock that file doesn't exist
        mock_exists.return_value = False
        
        success, message = qemu_utils.delete_disk(self.test_disk_path)
        
        self.assertFalse(success)
        self.assertEqual(message, f"Disk file not found: {self.test_disk_path}")
    
    @patch('qemu_utils.get_disk_info')
    @patch('os.path.exists')
    @patch('subprocess.Popen')
    @patch('tkinter.Tk')
    @patch('tkinter.Toplevel')
    def test_start_vm(self, mock_toplevel, mock_tk, mock_popen, mock_exists, mock_get_disk_info):
        # Mock dependencies
        mock_exists.return_value = True
        mock_get_disk_info.return_value = (True, {"disk": "info"})
        
        # Mock the Tk UI elements
        mock_root = MagicMock()
        mock_info_window = MagicMock()
        mock_tk.return_value = mock_root
        mock_toplevel.return_value = mock_info_window
        
        success, message = qemu_utils.start_vm(
            self.test_vm_config,
            self.test_disk_config
        )
        
        # Due to the complexity of testing the tkinter UI and threading,
        # we'll just verify that the function returned successfully
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main() 