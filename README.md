# QEMU VM Manager

A Python application to create and manage virtual machines using QEMU with a simple tkinter GUI.

![QEMU VM Manager Screenshot](screenshot.png)

## Features

- Create and manage virtual disks (qcow2, raw, vdi, vmdk formats)
- Create virtual machines with customizable CPU and memory settings
- OS installation via ISO images with detailed step-by-step guidance
- Easy VM management with a simple and intuitive GUI
- Troubleshooting tools to help diagnose and fix boot issues

## Prerequisites

- Python 3.6+
- QEMU installed and accessible in your system PATH
- Tkinter (usually comes with Python)

## Directory Structure

- `qemu_vm_manager/`: Main application package
  - `main.py`: Main application code
  - `qemu_utils.py`: Utilities for working with QEMU
  - `vdisks/`: Storage for virtual disk images
  - `isos/`: Storage for ISO images
  - `vms/`: VM configuration files
  - `logs/`: Application logs

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/qemu-vm-manager.git
   cd qemu-vm-manager
   ```

2. Make sure QEMU is installed on your system:
   - Windows: Download from [QEMU for Windows](https://qemu.weilnetz.de/)
   - Linux: `sudo apt install qemu-kvm qemu` (Ubuntu/Debian)
   - macOS: `brew install qemu` (using Homebrew)

3. Ensure QEMU is in your system PATH

## Usage

Run the application:

```
python qemu_vm_manager.py
```

### Creating a Virtual Machine

1. First, create a virtual disk in the "Create Disk" tab
2. Then create a VM in the "Create VM" tab, specifying:
   - VM name
   - CPU cores
   - Memory (MB)
   - Virtual disk (from those you've created)
   - Installation ISO (if this is a new VM)
3. Follow the installation guide that appears
4. After installation, manage your VM from the "Manage VMs" tab

## Troubleshooting

If your VM doesn't boot correctly:

1. Check the disk status using the "Check Disk Status" button
2. If needed, force boot with ISO using the "Force Boot with ISO" button
3. Check the logs in the `qemu_vm_manager/logs/` directory
4. Examine the generated batch file in the `qemu_vm_manager/vdisks/` directory

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- QEMU developers for the excellent virtualization software
- Python and Tkinter for making GUI development accessible 