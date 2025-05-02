#!/usr/bin/env python3
"""
QEMU VM Manager Launcher

This script launches the QEMU VM Manager application.
"""

import os
import sys
import subprocess

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Launch the application
if __name__ == "__main__":
    try:
        from qemu_vm_manager.main import QemuVMManager
        import tkinter as tk
        
        root = tk.Tk()
        app = QemuVMManager(root)
        root.mainloop()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you're running this script from the correct directory.")
    except Exception as e:
        print(f"Error launching application: {e}") 