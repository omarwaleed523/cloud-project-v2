import subprocess
import os
import logging
import shutil
import platform
import time
import hashlib

def check_qemu_available():
    """Check if QEMU is available in the system PATH"""
    try:
        result = subprocess.run(["qemu-img", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "QEMU is installed but qemu-img command failed"
    except FileNotFoundError:
        return False, "QEMU is not installed or not in the system PATH"

def get_disk_info(disk_path):
    """Get information about a virtual disk using qemu-img info"""
    if not os.path.exists(disk_path):
        return None, f"Disk file not found: {disk_path}"
    
    try:
        result = subprocess.run(["qemu-img", "info", disk_path],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            return parse_disk_info(result.stdout), None
        return None, result.stderr
    except Exception as e:
        return None, str(e)

def parse_disk_info(info_text):
    """Parse the output of qemu-img info command"""
    info = {}
    lines = info_text.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
    
    return info

def create_disk(disk_path, disk_format, disk_size_gb):
    """Create a new virtual disk"""
    try:
        cmd = ["qemu-img", "create", "-f", disk_format, disk_path, f"{disk_size_gb}G"]
        result = subprocess.run(cmd, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except Exception as e:
        return False, str(e)

def delete_disk(disk_path):
    """Delete a virtual disk file"""
    if not os.path.exists(disk_path):
        return False, f"Disk file not found: {disk_path}"
    
    try:
        os.remove(disk_path)
        return True, f"Disk deleted successfully: {disk_path}"
    except Exception as e:
        return False, str(e)

def start_vm(vm_config, disk_config, iso_path=None, first_boot=False):
    """Start a VM with the given configuration"""
    disk_path = disk_config["path"]
    disk_format = disk_config["format"]
    
    # Verify disk exists
    if not os.path.exists(disk_path):
        return False, f"Virtual disk file not found: {disk_path}"
    
    # Get disk info and log it
    disk_info_success, disk_info_result = get_disk_info(disk_path)
    if disk_info_success:
        logging.info(f"Using disk: {disk_path}")
        logging.info(f"Disk info: {disk_info_result}")
    else:
        logging.warning(f"Could not get disk info: {disk_info_result}")
    
    # Basic QEMU command
    cmd = [
        "qemu-system-x86_64",
        "-name", vm_config["name"],
        "-m", str(vm_config["memory"]),
        "-smp", str(vm_config["cpu"]),
    ]
    
    # Add primary hard disk - clearly labeled for OS installation
    disk_option = f"file={disk_path},format={disk_format},index=0,media=disk,if=ide"
    cmd.extend([
        "-drive", disk_option,
    ])
    logging.info(f"PRIMARY DISK: {disk_option}")
    
    # Add ISO boot if provided
    if iso_path and os.path.exists(iso_path):
        # Add ISO as a separate drive with IDE interface
        iso_option = f"file={iso_path},index=1,media=cdrom,if=ide"
        cmd.extend([
            "-drive", iso_option,
            "-boot", "order=dc,menu=on"  # Boot from CD first, then disk, with boot menu
        ])
        logging.info(f"ISO BOOT: {iso_option}")
        logging.info("Boot order: CD-ROM first, then Hard Disk")
    else:
        # No ISO, boot from hard disk only
        cmd.extend(["-boot", "order=c,menu=on"])  # Boot specifically from hard drive with boot menu
        logging.info("Boot order: Hard Disk only")
    
    # Add VGA for better graphics
    cmd.extend([
        "-vga", "std",
    ])
    
    # Use appropriate audio settings based on the platform
    system = platform.system().lower()
    if system == "windows":
        # Use a more basic audio configuration for Windows
        cmd.extend([
            "-device", "ich9-intel-hda",
        ])
    elif system == "linux":
        # Use PulseAudio on Linux
        cmd.extend([
            "-audiodev", "id=pa,driver=pa",
            "-device", "ich9-intel-hda",
            "-device", "hda-output,audiodev=pa",
        ])
    elif system == "darwin":
        # Use CoreAudio on macOS
        cmd.extend([
            "-audiodev", "id=coreaudio,driver=coreaudio",
            "-device", "ich9-intel-hda",
            "-device", "hda-output,audiodev=coreaudio",
        ])
    
    # Add RTC, USB keyboard and mouse, and network
    cmd.extend([
        "-rtc", "base=localtime,clock=host",
        "-usb",
        "-device", "usb-tablet",
        "-device", "usb-kbd",
        "-nic", "user,model=e1000"  # Use e1000 for better compatibility
    ])
    
    # Build the command string for display purposes
    cmd_str = " ".join(cmd)
    
    # Save the command to a batch file for debugging/manual running
    batch_file = os.path.join(os.path.dirname(disk_path), f"{vm_config['name']}_run.bat")
    try:
        with open(batch_file, 'w') as f:
            f.write(cmd_str)
        logging.info(f"Saved startup command to: {batch_file}")
    except Exception as e:
        logging.warning(f"Could not save batch file: {e}")
    
    try:
        # Log the full command
        logging.info("=========================================")
        logging.info("STARTING VM WITH COMMAND:")
        logging.info(cmd_str)
        logging.info("=========================================")
        
        # Create a popup with disk info to confirm configuration
        disk_info_message = (
            f"VM: {vm_config['name']}\n"
            f"PRIMARY DISK: {os.path.basename(disk_path)}\n"
            f"- Path: {disk_path}\n"
            f"- Format: {disk_format}\n"
        )
        
        if iso_path and os.path.exists(iso_path):
            disk_info_message += f"ISO: {os.path.basename(iso_path)}\n"
            disk_info_message += "BOOT ORDER: ISO first, then Hard Disk\n\n"
        else:
            disk_info_message += "BOOT ORDER: Hard Disk only\n\n"
            
        disk_info_message += (
            "INSTALLATION NOTES:\n"
            "- During OS installation, select the primary disk\n"
            "- The disk may appear as IDE0, sda, hda, or similar\n"
            "- Be sure to create partitions and format the disk\n"
            "- Complete the installation fully before rebooting"
        )
        
        # Display the VM and disk information
        import tkinter as tk
        from tkinter import messagebox
        
        # Show the confirmation without waiting for OK
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        info_window = tk.Toplevel(root)
        info_window.title(f"VM Boot Info: {vm_config['name']}")
        info_window.geometry("600x400")
        
        # Add the info text
        text = tk.Text(info_window, wrap=tk.WORD)
        text.insert(tk.END, disk_info_message)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a dismiss button
        btn = tk.Button(info_window, text="Proceed with VM Start", command=info_window.destroy)
        btn.pack(pady=10)
        
        # Start VM in a separate thread so dialog can show
        import threading
        
        def start_vm_process():
            # Wait a moment for the info window to display
            time.sleep(1.5)
            
            # We use Popen so the UI doesn't freeze while the VM is running
            process = subprocess.Popen(cmd)
            
            # Keep a reference to the process in case we need it later
            return process
        
        # Start the VM in a separate thread
        thread = threading.Thread(target=start_vm_process)
        thread.daemon = True
        thread.start()
        
        # Wait for user to dismiss the dialog
        root.wait_window(info_window)
        root.destroy()
        
        return True, "VM started successfully with explicit disk configuration"
    except Exception as e:
        logging.error(f"Error starting VM: {e}")
        return False, str(e)

def check_and_copy_iso(source_path, dest_dir):
    """Check if the ISO exists and copy it to the destination directory if needed"""
    if not os.path.exists(source_path):
        return False, f"ISO file not found: {source_path}"
    
    # Make sure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    basename = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, basename)
    
    # If the ISO is already in the destination, no need to copy
    if os.path.normpath(source_path) == os.path.normpath(dest_path):
        return True, dest_path
    
    # Copy the ISO file
    try:
        shutil.copy2(source_path, dest_path)
        return True, dest_path
    except Exception as e:
        return False, str(e)

def check_disk_status(disk_path):
    """
    Check if a disk has been modified/written to by comparing file size and hash
    Returns a tuple (is_modified, details)
    """
    if not os.path.exists(disk_path):
        return False, f"Disk file not found: {disk_path}"
    
    # Get current size
    current_size = os.path.getsize(disk_path)
    
    # Get basic file info
    try:
        result = subprocess.run(["qemu-img", "info", disk_path],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode != 0:
            return False, f"Error getting disk info: {result.stderr}"
        
        # If disk is larger than 1MB, it's likely been modified
        if current_size > 1024 * 1024:
            return True, f"Disk size is {current_size/1024/1024:.2f} MB, likely modified"
        
        # If not, check if file has non-zero data
        with open(disk_path, 'rb') as f:
            # Read first 1MB to check if it contains data
            data = f.read(1024 * 1024)
            if any(byte != 0 for byte in data):
                return True, "Disk contains non-zero data"
        
        return False, "Disk appears to be empty or unmodified"
    except Exception as e:
        return False, f"Error checking disk status: {e}"

def convert_disk_format(disk_path, target_format):
    """
    Convert disk to a different format
    Returns a tuple (success, message)
    """
    if not os.path.exists(disk_path):
        return False, f"Disk file not found: {disk_path}"
    
    # Get current format and path info
    dir_path, filename = os.path.split(disk_path)
    name, ext = os.path.splitext(filename)
    target_path = os.path.join(dir_path, f"{name}.{target_format}")
    
    # Check if target file already exists
    if os.path.exists(target_path):
        return False, f"Target file already exists: {target_path}"
    
    try:
        cmd = ["qemu-img", "convert", "-f", ext.replace(".", ""), "-O", target_format, disk_path, target_path]
        result = subprocess.run(cmd, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode == 0:
            return True, target_path
        return False, result.stderr
    except Exception as e:
        return False, str(e) 