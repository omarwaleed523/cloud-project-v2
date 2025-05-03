import unittest
import os
import tempfile
import shutil
import json
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import qemu_utils
from main import QemuVMManager

class TestQemuVMManagerIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as our test environment
        self.test_base_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        self.vdisks_dir = os.path.join(self.test_base_dir, "vdisks")
        self.isos_dir = os.path.join(self.test_base_dir, "isos")
        self.vms_dir = os.path.join(self.test_base_dir, "vms")
        self.logs_dir = os.path.join(self.test_base_dir, "logs")
        
        os.makedirs(self.vdisks_dir)
        os.makedirs(self.isos_dir)
        os.makedirs(self.vms_dir)
        os.makedirs(self.logs_dir)
        
        # Test data
        self.test_disk_name = "test_disk"
        self.test_disk_path = os.path.join(self.vdisks_dir, f"{self.test_disk_name}.qcow2")
        self.test_disk_format = "qcow2"
        self.test_disk_size = 10
        
        self.test_vm_name = "test_vm"
        self.test_vm_cpu = 1
        self.test_vm_memory = 1024
        
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_base_dir)
    
    @patch('tkinter.Tk')
    @patch('qemu_utils.check_qemu_available')
    def test_init(self, mock_check_qemu, mock_tk):
        # Mock QEMU availability check
        mock_check_qemu.return_value = (True, "QEMU emulator version 5.0.0")
        
        # Mock tk Root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override paths for testing
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            # Create app without normal initialization
            app = QemuVMManager(mock_root)
            
            # Set properties manually
            app.root = mock_root
            app.base_dir = self.test_base_dir
            app.vdisks_dir = self.vdisks_dir
            app.isos_dir = self.isos_dir
            app.vms_dir = self.vms_dir
            
            # Initialize empty data
            app.vms = {}
            app.vdisks = {}
    
    @patch('tkinter.Tk')
    @patch('qemu_utils.check_qemu_available')
    @patch('qemu_utils.create_disk')
    def test_create_disk_integration(self, mock_create_disk, mock_check_qemu, mock_tk):
        # Mock the dependencies
        mock_check_qemu.return_value = (True, "QEMU emulator version 5.0.0")
        mock_create_disk.return_value = (True, "Disk created successfully")
        
        # Mock tk root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Create app with mocked initialization
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties manually
            app.root = mock_root
            app.base_dir = self.test_base_dir
            app.vdisks_dir = self.vdisks_dir
            app.isos_dir = self.isos_dir
            app.vms_dir = self.vms_dir
            app.vms = {}
            app.vdisks = {}
            
            # Mock UI elements
            app.disk_name = MagicMock(get=lambda: self.test_disk_name)
            app.disk_size = MagicMock(get=lambda: str(self.test_disk_size))
            app.disk_format = MagicMock(get=lambda: self.test_disk_format)
            app.disk_listbox = MagicMock()
            app.update_disk_list = MagicMock()
            app.update_disk_dropdown = MagicMock()
            app.save_vdisks = MagicMock()
            
            # Call create disk with mocked messagebox
            with patch('tkinter.messagebox.showerror') as mock_error:
                with patch('tkinter.messagebox.showinfo') as mock_info:
                    app.create_disk()
                    
                    # Verify that create_disk was called with correct parameters
                    expected_path = os.path.join(self.vdisks_dir, f"{self.test_disk_name}.{self.test_disk_format}")
                    mock_create_disk.assert_called_once_with(
                        expected_path, 
                        self.test_disk_format, 
                        self.test_disk_size
                    )
                    
                    # Verify the app functions were called
                    app.update_disk_list.assert_called_once()
                    app.update_disk_dropdown.assert_called_once()
                    app.save_vdisks.assert_called_once()
                    
                    # Check that disk was added to vdisks dict
                    self.assertIn(self.test_disk_name, app.vdisks)
                    self.assertEqual(app.vdisks[self.test_disk_name]["path"], expected_path)
                    self.assertEqual(app.vdisks[self.test_disk_name]["format"], self.test_disk_format)
                    self.assertEqual(app.vdisks[self.test_disk_name]["size"], self.test_disk_size)
    
    @patch('tkinter.Tk')
    @patch('qemu_utils.check_qemu_available')
    @patch('qemu_utils.start_vm')
    def test_start_vm_integration(self, mock_start_vm, mock_check_qemu, mock_tk):
        # Mock the dependencies
        mock_check_qemu.return_value = (True, "QEMU emulator version 5.0.0")
        mock_start_vm.return_value = (True, "VM started successfully")
        
        # Mock tk Root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Create app with mocked initialization
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties manually
            app.root = mock_root
            app.base_dir = self.test_base_dir
            app.vdisks_dir = self.vdisks_dir
            app.isos_dir = self.isos_dir
            app.vms_dir = self.vms_dir
            
            # Create test disk and VM data
            app.vdisks = {
                self.test_disk_name: {
                    "path": self.test_disk_path,
                    "format": self.test_disk_format,
                    "size": self.test_disk_size
                }
            }
            
            app.vms = {
                self.test_vm_name: {
                    "name": self.test_vm_name,
                    "cpu": self.test_vm_cpu,
                    "memory": self.test_vm_memory,
                    "disk": self.test_disk_name,
                    "first_boot": False
                }
            }
            
            # Mock check_disk_status function
            with patch('qemu_utils.check_disk_status') as mock_check_disk:
                mock_check_disk.return_value = (True, "Disk is modified")
                
                # Mock messagebox
                with patch('tkinter.messagebox.showinfo') as mock_info:
                    app.start_vm_by_name(self.test_vm_name)
                    
                    # Verify start_vm was called with correct parameters
                    mock_start_vm.assert_called_once()
                    
                    # Get the actual args passed to start_vm
                    args, kwargs = mock_start_vm.call_args
                    
                    # Check the VM config passed
                    vm_config = args[0]
                    self.assertEqual(vm_config["name"], self.test_vm_name)
                    self.assertEqual(vm_config["cpu"], self.test_vm_cpu)
                    self.assertEqual(vm_config["memory"], self.test_vm_memory)
                    
                    # Check the disk config passed
                    disk_config = args[1]
                    self.assertEqual(disk_config["path"], self.test_disk_path)
                    self.assertEqual(disk_config["format"], self.test_disk_format)
                    self.assertEqual(disk_config["size"], self.test_disk_size)
                    
                    # Verify iso_path is None for normal boot
                    self.assertFalse(kwargs.get("first_boot", False))
                    self.assertIsNone(kwargs.get("iso_path"))

if __name__ == '__main__':
    unittest.main() 