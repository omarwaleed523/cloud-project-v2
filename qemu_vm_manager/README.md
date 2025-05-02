# QEMU VM Manager

A simple Python application to create and manage virtual machines using QEMU.

## Features

- Create virtual disks with different formats (qcow2, raw, vdi, vmdk)
- Create virtual machines with customizable CPU and memory settings
- Automatically boot new VMs from ISO images for OS installation
- Manage existing VMs and disks
- Simple and intuitive GUI interface

## Prerequisites

- Python 3.6+
- QEMU installed and available in your system PATH
- Tkinter (usually comes with Python)

## Directory Structure

The application organizes files in the following directories:

- `/vdisks` - Storage for virtual disk images
- `/isos` - Storage for ISO images
- `/vms` - VM configuration files
- `/logs` - Application logs

## Usage

1. **Create a Virtual Disk**:
   - Go to the "Create Disk" tab
   - Specify disk name, size, and format
   - Click "Create Disk"

2. **Create a Virtual Machine**:
   - Go to the "Create VM" tab
   - Specify VM name, CPU cores, and memory
   - Select a previously created virtual disk
   - Optionally, select an ISO image for first boot
   - Click "Create VM"

3. **Start a Virtual Machine**:
   - Go to the "Manage VMs" tab
   - Select a VM from the list
   - Click "Start VM"

4. **Delete a Virtual Machine or Disk**:
   - Select the VM or disk you want to delete
   - Click "Delete VM" or "Delete Disk"

## Running the Application

```
python main.py
```

## Notes

- The first time a VM boots, it will try to boot from the ISO image to allow OS installation
- Subsequent boots will use the virtual disk directly
- Virtual disk deletion is prevented if the disk is in use by a VM 