import unittest
import os
import tempfile
import shutil
import json
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import QemuVMManager

class TestMain(unittest.TestCase):
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
        
        # Sample VM config data
        self.sample_vms = {
            "test_vm": {
                "name": "test_vm",
                "cpu": 1,
                "memory": 1024,
                "disk": "test_disk",
                "first_boot": False
            }
        }
        
        # Sample disk config data
        self.sample_vdisks = {
            "test_disk": {
                "path": os.path.join(self.vdisks_dir, "test_disk.qcow2"),
                "format": "qcow2",
                "size": 10
            }
        }
        
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_base_dir)
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_init_qemu_not_available(self, mock_tk, mock_check_qemu):
        """Test initialization when QEMU is not available"""
        mock_check_qemu.return_value = (False, "QEMU not found")
        
        # Mock root and messagebox
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        with patch('tkinter.messagebox.showerror') as mock_error:
            QemuVMManager(mock_root)
            
            # Verify error was shown
            mock_error.assert_called_once()
            mock_root.destroy.assert_called_once()
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    @patch('os.makedirs')
    def test_init_creates_directories(self, mock_makedirs, mock_tk, mock_check_qemu):
        """Test that directories are created during initialization"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Mock methods that would be called during initialization
        with patch.object(QemuVMManager, 'load_vms', return_value={}):
            with patch.object(QemuVMManager, 'load_vdisks', return_value={}):
                with patch.object(QemuVMManager, 'create_vm_tab'):
                    with patch.object(QemuVMManager, 'create_disk_tab'):
                        with patch.object(QemuVMManager, 'create_manage_tab'):
                            app = QemuVMManager(mock_root)
                            
                            # Check that makedirs was called for each directory
                            self.assertEqual(mock_makedirs.call_count, 3)
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_load_vms_success(self, mock_tk, mock_check_qemu):
        """Test loading VM configurations"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Create a VM config file
        vm_config_file = os.path.join(self.vms_dir, "vm_configs.json")
        with open(vm_config_file, 'w') as f:
            json.dump(self.sample_vms, f)
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method to only test load_vms
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties manually
            app.root = mock_root
            app.vms_dir = self.vms_dir
            
            # Call method and check result
            vms = app.load_vms()
            self.assertEqual(vms, self.sample_vms)
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_load_vms_file_not_exists(self, mock_tk, mock_check_qemu):
        """Test loading VM configurations when file doesn't exist"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties manually
            app.root = mock_root
            app.vms_dir = self.vms_dir
            
            # Call method and check result
            vms = app.load_vms()
            self.assertEqual(vms, {})
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_save_vms(self, mock_tk, mock_check_qemu):
        """Test saving VM configurations"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties manually
            app.root = mock_root
            app.vms_dir = self.vms_dir
            app.vms = self.sample_vms
            
            # Call method to save VMs
            app.save_vms()
            
            # Check that file was created with correct content
            vm_config_file = os.path.join(self.vms_dir, "vm_configs.json")
            with open(vm_config_file, 'r') as f:
                saved_vms = json.load(f)
                self.assertEqual(saved_vms, self.sample_vms)
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_iso(self, mock_filedialog, mock_tk, mock_check_qemu):
        """Test browse ISO functionality"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        mock_filedialog.return_value = "/path/to/test.iso"
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties
            app.root = mock_root
            app.iso_path_var = MagicMock()
            
            # Call method
            app.browse_iso()
            
            # Check that dialog was shown and path was set
            mock_filedialog.assert_called_once()
            app.iso_path_var.set.assert_called_once_with("/path/to/test.iso")
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_update_disk_dropdown(self, mock_tk, mock_check_qemu):
        """Test update disk dropdown functionality"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties
            app.root = mock_root
            app.vdisks = self.sample_vdisks
            app.disk_dropdown = MagicMock()
            app.selected_disk = MagicMock()
            
            # Call method
            app.update_disk_dropdown()
            
            # Check that dropdown values were updated
            app.disk_dropdown.__setitem__.assert_called_once_with('values', ['test_disk'])
            app.selected_disk.set.assert_called_once_with('test_disk')
    
    @patch('qemu_utils.check_qemu_available')
    @patch('tkinter.Tk')
    def test_update_disk_list(self, mock_tk, mock_check_qemu):
        """Test update disk list functionality"""
        mock_check_qemu.return_value = (True, "QEMU version 5.0.0")
        
        # Mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Override initialization method
        with patch.object(QemuVMManager, '__init__', lambda self, root: None):
            app = QemuVMManager(mock_root)
            
            # Set required properties
            app.root = mock_root
            app.vdisks = self.sample_vdisks
            app.disk_listbox = MagicMock()
            
            # Call method
            app.update_disk_list()
            
            # Check that listbox was updated
            app.disk_listbox.delete.assert_called_once_with(0, "end")
            app.disk_listbox.insert.assert_called_once()

if __name__ == '__main__':
    unittest.main() 