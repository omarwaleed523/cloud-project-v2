import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import logging
from datetime import datetime
import qemu_utils

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"qemu_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class QemuVMManager:
    def __init__(self, root):
        self.root = root
        self.root.title("QEMU VM Manager")
        self.root.geometry("800x600")
        
        # Check if QEMU is available
        qemu_available, qemu_version = qemu_utils.check_qemu_available()
        if not qemu_available:
            messagebox.showerror("Error", f"QEMU is not available: {qemu_version}")
            logging.error(f"QEMU is not available: {qemu_version}")
            root.destroy()
            return
        
        logging.info(f"QEMU version: {qemu_version}")
        
        # Define paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.vdisks_dir = os.path.join(self.base_dir, "vdisks")
        self.isos_dir = os.path.join(self.base_dir, "isos")
        self.vms_dir = os.path.join(self.base_dir, "vms")
        
        # Ensure directories exist
        for directory in [self.vdisks_dir, self.isos_dir, self.vms_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Load existing VMs and disks
        self.vms = self.load_vms()
        self.vdisks = self.load_vdisks()
        
        # Create the notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_vm_tab()
        self.create_disk_tab()
        self.create_manage_tab()
        
    def load_vms(self):
        """Load existing VM configurations"""
        vms = {}
        vm_config_file = os.path.join(self.vms_dir, "vm_configs.json")
        if os.path.exists(vm_config_file):
            try:
                with open(vm_config_file, 'r') as f:
                    vms = json.load(f)
            except Exception as e:
                logging.error(f"Error loading VM configurations: {e}")
                messagebox.showerror("Error", f"Failed to load VM configurations: {e}")
        return vms
    
    def save_vms(self):
        """Save VM configurations to file"""
        vm_config_file = os.path.join(self.vms_dir, "vm_configs.json")
        try:
            with open(vm_config_file, 'w') as f:
                json.dump(self.vms, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving VM configurations: {e}")
            messagebox.showerror("Error", f"Failed to save VM configurations: {e}")
    
    def load_vdisks(self):
        """Load existing virtual disk information"""
        vdisks = {}
        vdisk_config_file = os.path.join(self.vdisks_dir, "vdisk_configs.json")
        if os.path.exists(vdisk_config_file):
            try:
                with open(vdisk_config_file, 'r') as f:
                    vdisks = json.load(f)
            except Exception as e:
                logging.error(f"Error loading virtual disk configurations: {e}")
                messagebox.showerror("Error", f"Failed to load virtual disk configurations: {e}")
        return vdisks
    
    def save_vdisks(self):
        """Save virtual disk configurations to file"""
        vdisk_config_file = os.path.join(self.vdisks_dir, "vdisk_configs.json")
        try:
            with open(vdisk_config_file, 'w') as f:
                json.dump(self.vdisks, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving virtual disk configurations: {e}")
            messagebox.showerror("Error", f"Failed to save virtual disk configurations: {e}")
    
    def create_vm_tab(self):
        """Create the tab for VM creation and management"""
        vm_tab = ttk.Frame(self.notebook)
        self.notebook.add(vm_tab, text="Create VM")
        
        # VM creation form
        ttk.Label(vm_tab, text="VM Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.vm_name = tk.StringVar()
        ttk.Entry(vm_tab, textvariable=self.vm_name).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(vm_tab, text="CPU Cores:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cpu_cores = tk.StringVar(value="1")
        ttk.Spinbox(vm_tab, from_=1, to=16, textvariable=self.cpu_cores).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(vm_tab, text="Memory (MB):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.memory = tk.StringVar(value="1024")
        ttk.Entry(vm_tab, textvariable=self.memory).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(vm_tab, text="Virtual Disk:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.selected_disk = tk.StringVar()
        self.disk_dropdown = ttk.Combobox(vm_tab, textvariable=self.selected_disk)
        self.disk_dropdown.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(vm_tab, text="ISO Image (for first boot):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.iso_path_var = tk.StringVar()
        ttk.Entry(vm_tab, textvariable=self.iso_path_var).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(vm_tab, text="Browse", command=self.browse_iso).grid(row=4, column=2, padx=5, pady=5)
        
        # Create VM button
        ttk.Button(vm_tab, text="Create VM", command=self.create_vm).grid(row=5, column=1, padx=5, pady=15)
        
        # Installation instructions
        install_frame = ttk.LabelFrame(vm_tab, text="OS Installation Guide")
        install_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        instructions = (
            "1. Create a virtual disk in the 'Create Disk' tab first.\n"
            "2. Select an OS installation ISO image above.\n"
            "3. After the VM is created, it will boot from the ISO.\n"
            "4. During OS installation, when asked where to install:\n"
            "   - Select the virtual disk (may appear as 'sda', 'vda', or similar)\n"
            "   - Create partitions and format as needed\n"
            "   - Complete the installation process fully\n"
            "5. After installation completes, shut down the VM.\n"
            "6. Then restart the VM from the 'Manage VMs' tab.\n"
        )
        
        ttk.Label(install_frame, text=instructions, justify="left").pack(padx=5, pady=5, fill="both")
        
        # Update disk dropdown
        self.update_disk_dropdown()
    
    def create_disk_tab(self):
        """Create the tab for virtual disk creation"""
        disk_tab = ttk.Frame(self.notebook)
        self.notebook.add(disk_tab, text="Create Disk")
        
        ttk.Label(disk_tab, text="Disk Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.disk_name = tk.StringVar()
        ttk.Entry(disk_tab, textvariable=self.disk_name).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(disk_tab, text="Disk Size (GB):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.disk_size = tk.StringVar(value="10")
        ttk.Entry(disk_tab, textvariable=self.disk_size).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(disk_tab, text="Disk Format:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.disk_format = tk.StringVar(value="qcow2")
        format_combo = ttk.Combobox(disk_tab, textvariable=self.disk_format)
        format_combo['values'] = ('qcow2', 'raw', 'vdi', 'vmdk')
        format_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Create disk button
        ttk.Button(disk_tab, text="Create Disk", command=self.create_disk).grid(row=3, column=1, padx=5, pady=15)
        
        # Existing disks list
        ttk.Label(disk_tab, text="Existing Disks:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.disk_listbox = tk.Listbox(disk_tab, width=50, height=10)
        self.disk_listbox.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Delete disk button
        ttk.Button(disk_tab, text="Delete Disk", command=self.delete_disk).grid(row=6, column=1, padx=5, pady=5)
        
        # Configure grid weights for resizing
        disk_tab.columnconfigure(1, weight=1)
        disk_tab.rowconfigure(5, weight=1)
        
        # Update disk list
        self.update_disk_list()
        
    def create_manage_tab(self):
        """Create the tab for VM management"""
        manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(manage_tab, text="Manage VMs")
        
        # VM listbox
        ttk.Label(manage_tab, text="Virtual Machines:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.vm_listbox = tk.Listbox(manage_tab, width=50, height=10)
        self.vm_listbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Boot options frame
        boot_frame = ttk.LabelFrame(manage_tab, text="Boot Options")
        boot_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Boot option radiobuttons
        self.boot_option = tk.StringVar(value="disk")
        ttk.Radiobutton(boot_frame, text="Boot from Virtual Disk", 
                        variable=self.boot_option, value="disk").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(boot_frame, text="Boot from ISO", 
                        variable=self.boot_option, value="iso").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        # ISO selection for boot
        ttk.Label(boot_frame, text="ISO Image:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.boot_iso_path = tk.StringVar()
        ttk.Entry(boot_frame, textvariable=self.boot_iso_path, width=30).grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(boot_frame, text="Browse", command=self.browse_boot_iso).grid(row=2, column=2, padx=5, pady=2)
        
        # Troubleshooting frame
        troubleshoot_frame = ttk.LabelFrame(manage_tab, text="Troubleshooting")
        troubleshoot_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(troubleshoot_frame, text="If VM doesn't boot correctly:").grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="w")
        ttk.Button(troubleshoot_frame, text="Check Disk Status", 
                   command=self.check_selected_disk_status).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(troubleshoot_frame, text="Force Boot with ISO", 
                   command=self.force_boot_with_iso).grid(row=1, column=1, padx=5, pady=2)
        
        # Buttons
        ttk.Button(manage_tab, text="Start VM", command=self.start_vm).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(manage_tab, text="Delete VM", command=self.delete_vm).grid(row=4, column=1, padx=5, pady=5)
        
        # Configure grid weights for resizing
        manage_tab.columnconfigure(0, weight=1)
        manage_tab.rowconfigure(1, weight=1)
        boot_frame.columnconfigure(1, weight=1)
        
        # Update VM list
        self.update_vm_list()
    
    def browse_iso(self):
        """Open file dialog to select ISO image"""
        iso_file = filedialog.askopenfilename(
            title="Select ISO Image",
            filetypes=[("ISO images", "*.iso"), ("All files", "*.*")]
        )
        if iso_file:
            # Store the selected ISO path
            self.iso_path_var.set(iso_file)
    
    def update_disk_dropdown(self):
        """Update the virtual disk dropdown with available disks"""
        disk_names = list(self.vdisks.keys())
        self.disk_dropdown['values'] = disk_names
        if disk_names:
            self.selected_disk.set(disk_names[0])
    
    def update_disk_list(self):
        """Update the list of existing virtual disks"""
        self.disk_listbox.delete(0, tk.END)
        for disk_name, disk_info in self.vdisks.items():
            self.disk_listbox.insert(tk.END, f"{disk_name} ({disk_info['size']}GB, {disk_info['format']})")
    
    def update_vm_list(self):
        """Update the list of existing VMs"""
        self.vm_listbox.delete(0, tk.END)
        for vm_name, vm_info in self.vms.items():
            self.vm_listbox.insert(tk.END, f"{vm_name} (CPU: {vm_info['cpu']}, RAM: {vm_info['memory']}MB)")
    
    def create_disk(self):
        """Create a new virtual disk"""
        disk_name = self.disk_name.get().strip()
        if not disk_name:
            messagebox.showerror("Error", "Disk name cannot be empty")
            return
        
        try:
            disk_size = int(self.disk_size.get())
            if disk_size <= 0:
                messagebox.showerror("Error", "Disk size must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Disk size must be a number")
            return
        
        disk_format = self.disk_format.get()
        if not disk_format:
            messagebox.showerror("Error", "Please select a disk format")
            return
        
        # Check if disk with same name already exists
        if disk_name in self.vdisks:
            messagebox.showerror("Error", f"A disk with name '{disk_name}' already exists")
            return
        
        disk_path = os.path.join(self.vdisks_dir, f"{disk_name}.{disk_format}")
        
        # Create the disk using qemu_utils
        success, message = qemu_utils.create_disk(disk_path, disk_format, disk_size)
        if not success:
            logging.error(f"Error creating disk: {message}")
            messagebox.showerror("Error", f"Failed to create disk: {message}")
            return
        
        # Save disk info
        self.vdisks[disk_name] = {
            "path": disk_path,
            "format": disk_format,
            "size": disk_size
        }
        self.save_vdisks()
        
        # Update UI
        self.update_disk_list()
        self.update_disk_dropdown()
        
        messagebox.showinfo("Success", f"Virtual disk '{disk_name}' created successfully")
    
    def delete_disk(self):
        """Delete selected virtual disk"""
        selection = self.disk_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a disk to delete")
            return
        
        disk_idx = selection[0]
        disk_entry = self.disk_listbox.get(disk_idx)
        disk_name = disk_entry.split(" ")[0]
        
        if disk_name not in self.vdisks:
            messagebox.showerror("Error", f"Disk '{disk_name}' not found")
            return
        
        # Check if disk is used by any VM
        for vm_name, vm_info in self.vms.items():
            if vm_info.get("disk") == disk_name:
                messagebox.showerror("Error", f"Cannot delete disk: It is used by VM '{vm_name}'")
                return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete disk '{disk_name}'?"):
            return
        
        disk_path = self.vdisks[disk_name]["path"]
        
        # Delete disk file using qemu_utils
        success, message = qemu_utils.delete_disk(disk_path)
        if not success:
            logging.error(f"Error deleting disk: {message}")
            messagebox.showerror("Error", f"Failed to delete disk: {message}")
            return
        
        # Remove from configuration
        del self.vdisks[disk_name]
        self.save_vdisks()
        
        # Update UI
        self.update_disk_list()
        self.update_disk_dropdown()
        
        messagebox.showinfo("Success", f"Virtual disk '{disk_name}' deleted successfully")
    
    def create_vm(self):
        """Create a new virtual machine"""
        vm_name = self.vm_name.get().strip()
        if not vm_name:
            messagebox.showerror("Error", "VM name cannot be empty")
            return
        
        try:
            cpu_cores = int(self.cpu_cores.get())
            if cpu_cores <= 0:
                messagebox.showerror("Error", "CPU cores must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "CPU cores must be a number")
            return
        
        try:
            memory = int(self.memory.get())
            if memory <= 0:
                messagebox.showerror("Error", "Memory must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Memory must be a number")
            return
        
        selected_disk = self.selected_disk.get()
        if not selected_disk:
            messagebox.showerror("Error", "Please select a virtual disk")
            return
        
        # Check if VM with same name already exists
        if vm_name in self.vms:
            messagebox.showerror("Error", f"A VM with name '{vm_name}' already exists")
            return
        
        # Check ISO path if provided
        iso_path = self.iso_path_var.get()
        if not iso_path:
            response = messagebox.askyesno("Warning", 
                "No ISO image selected. This VM will need to boot from an already prepared disk.\n\n"
                "If this is a new VM, you should select an OS installation ISO.\n\n"
                "Do you want to continue without an ISO?")
            if not response:
                return
        elif not os.path.exists(iso_path):
            messagebox.showerror("Error", f"ISO file does not exist: {iso_path}")
            return
        
        # Create VM configuration
        vm_config = {
            "name": vm_name,
            "cpu": cpu_cores,
            "memory": memory,
            "disk": selected_disk,
            "iso": iso_path,
            "first_boot": True if iso_path else False,  # Flag to indicate first boot only if ISO provided
            "os_installed": False  # Track if OS has been installed
        }
        
        # Save VM configuration
        self.vms[vm_name] = vm_config
        self.save_vms()
        
        # Update UI
        self.update_vm_list()
        
        # Show custom installation instructions dialog if ISO was provided
        if iso_path:
            self.show_installation_guide(vm_name)
            
            # Ask if user wants to start the VM now
            if messagebox.askyesno("Start VM", "Do you want to start the VM now to install the OS?"):
                self.start_vm_by_name(vm_name)
        else:
            messagebox.showinfo("Success", f"VM '{vm_name}' created successfully")
    
    def show_installation_guide(self, vm_name):
        """Display a graphical installation guide with screenshots"""
        if vm_name not in self.vms:
            return
        
        vm_info = self.vms[vm_name]
        disk_name = vm_info["disk"]
        
        # Create a custom dialog with installation steps
        install_guide = tk.Toplevel(self.root)
        install_guide.title(f"Installation Guide - {vm_name}")
        install_guide.geometry("650x550")
        install_guide.transient(self.root)
        install_guide.grab_set()  # Make it modal
        
        # Add a notebook for step-by-step instructions
        notebook = ttk.Notebook(install_guide)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Step 1: Overview
        step1 = ttk.Frame(notebook)
        notebook.add(step1, text="Overview")
        
        ttk.Label(step1, text="OS Installation Guide", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        overview_text = (
            f"VM Name: {vm_name}\n"
            f"Virtual Disk: {disk_name}\n\n"
            "This guide will help you install an operating system to your virtual disk.\n"
            "The process involves several important steps which must be completed correctly\n"
            "for your VM to boot properly after installation.\n\n"
            "Follow each tab from left to right for step-by-step instructions."
        )
        
        ttk.Label(step1, text=overview_text, justify="left").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Step 2: Boot from ISO
        step2 = ttk.Frame(notebook)
        notebook.add(step2, text="Boot from ISO")
        
        ttk.Label(step2, text="Step 1: Boot from Installation ISO", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        boot_text = (
            "• When the VM starts, it will boot from your installation ISO\n"
            "• You may need to press a key or select the CD/DVD option from the boot menu\n"
            "• The installer will load and guide you through the initial setup\n"
            "• Continue until you reach the disk selection/partitioning step"
        )
        
        ttk.Label(step2, text=boot_text, justify="left").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Step 3: Disk Selection
        step3 = ttk.Frame(notebook)
        notebook.add(step3, text="Disk Selection")
        
        ttk.Label(step3, text="Step 2: Select the Virtual Disk", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        disk_text = (
            "• When prompted to select where to install the OS, you'll see your virtual disk\n"
            "• It may appear as:\n"
            "   - IDE Disk 0, IDE0, or similar\n"
            "   - sda (for Linux installers)\n"
            "   - hda (for older Linux installers)\n"
            "   - Disk 0 (for Windows)\n\n"
            "• IMPORTANT: Select the entire disk and continue\n"
            "• If prompted, create a new partition table on the disk"
        )
        
        ttk.Label(step3, text=disk_text, justify="left").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Step 4: Partition and Format
        step4 = ttk.Frame(notebook)
        notebook.add(step4, text="Partitioning")
        
        ttk.Label(step4, text="Step 3: Partition and Format the Disk", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        partition_text = (
            "• Create the necessary partitions as required by your OS\n"
            "• For most operating systems, you'll need:\n"
            "   - A boot partition (sometimes marked as /boot)\n"
            "   - A system partition (C: drive or / for Linux)\n"
            "• Format the partitions with the appropriate file system\n"
            "• CRITICALLY IMPORTANT: Install the bootloader when prompted\n"
            "   - This is what allows the disk to boot on its own later\n"
            "   - For Windows, this is automatic\n"
            "   - For Linux, install GRUB to the MBR/first sector of the disk"
        )
        
        ttk.Label(step4, text=partition_text, justify="left").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Step 5: Complete Installation
        step5 = ttk.Frame(notebook)
        notebook.add(step5, text="Complete")
        
        ttk.Label(step5, text="Step 4: Complete Installation and First Boot", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        complete_text = (
            "• Complete the entire installation process\n"
            "• When prompted to restart, allow the system to reboot\n"
            "• IMPORTANT: After installation completes, the VM will shut down\n\n"
            "• To start your VM with the newly installed OS:\n"
            "   1. Go to the 'Manage VMs' tab\n"
            "   2. Select your VM from the list\n"
            "   3. Ensure 'Boot from Virtual Disk' is selected\n"
            "   4. Click 'Start VM'\n\n"
            "• If the VM doesn't boot, use the troubleshooting tools in the Manage VMs tab"
        )
        
        ttk.Label(step5, text=complete_text, justify="left").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Close button
        ttk.Button(install_guide, text="I Understand - Start Installation", 
                  command=install_guide.destroy).pack(pady=10)
        
        # Center the window
        install_guide.update_idletasks()
        width = install_guide.winfo_width()
        height = install_guide.winfo_height()
        x = (install_guide.winfo_screenwidth() // 2) - (width // 2)
        y = (install_guide.winfo_screenheight() // 2) - (height // 2)
        install_guide.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Wait for the dialog to be closed
        self.root.wait_window(install_guide)
    
    def start_vm_by_name(self, vm_name, boot_with_iso=False, iso_path=None):
        """Start a VM by its name"""
        if vm_name not in self.vms:
            messagebox.showerror("Error", f"VM '{vm_name}' not found")
            return
        
        vm_info = self.vms[vm_name]
        disk_name = vm_info["disk"]
        
        if disk_name not in self.vdisks:
            messagebox.showerror("Error", f"Virtual disk '{disk_name}' not found")
            return

        disk_path = self.vdisks[disk_name]["path"]
        
        # Check if disk has been modified (likely has OS installed)
        is_modified, details = qemu_utils.check_disk_status(disk_path)
        logging.info(f"Disk status for {disk_name}: {is_modified}, {details}")
        
        # Use provided ISO for boot if specified
        boot_iso = iso_path if boot_with_iso else None
        
        # Only use the VM's saved ISO if doing first boot and no override ISO provided
        first_boot = vm_info.get("first_boot", False)
        if first_boot and not boot_iso and vm_info.get("iso"):
            boot_iso = vm_info["iso"]
        
        # If disk is empty but trying to boot from disk, warn user
        if not is_modified and not boot_iso:
            response = messagebox.askyesno("Warning", 
                f"Virtual disk '{disk_name}' appears to be empty or unused.\n\n"
                "This disk likely doesn't have an operating system installed yet.\n\n"
                "Do you want to select an ISO to boot from instead?")
            if response:
                iso_file = filedialog.askopenfilename(
                    title="Select ISO Image for Boot",
                    filetypes=[("ISO images", "*.iso"), ("All files", "*.*")]
                )
                if iso_file and os.path.exists(iso_file):
                    boot_iso = iso_file
                else:
                    return
        
        # Start VM using qemu_utils
        success, result = qemu_utils.start_vm(
            vm_info, 
            self.vdisks[disk_name], 
            iso_path=boot_iso, 
            first_boot=first_boot or boot_with_iso  # Consider it a "first boot" if booting from ISO
        )
        
        if not success:
            logging.error(f"Error starting VM: {result}")
            messagebox.showerror("Error", f"Failed to start VM: {result}")
            return
        
        # Mark as not first boot for subsequent boots
        if first_boot:
            vm_info["first_boot"] = False
            self.save_vms()
        
        messagebox.showinfo("Success", f"VM '{vm_name}' started{' with ISO' if boot_iso else ''}")
    
    def start_vm(self):
        """Start the selected VM"""
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a VM to start")
            return
        
        vm_idx = selection[0]
        vm_entry = self.vm_listbox.get(vm_idx)
        vm_name = vm_entry.split(" ")[0]
        
        # Get boot option
        boot_with_iso = self.boot_option.get() == "iso"
        iso_path = self.boot_iso_path.get() if boot_with_iso else None
        
        if boot_with_iso and not iso_path:
            messagebox.showerror("Error", "Please select an ISO image for boot")
            return
        
        if boot_with_iso and not os.path.exists(iso_path):
            messagebox.showerror("Error", f"ISO file does not exist: {iso_path}")
            return
        
        self.start_vm_by_name(vm_name, boot_with_iso=boot_with_iso, iso_path=iso_path)
    
    def delete_vm(self):
        """Delete the selected VM"""
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a VM to delete")
            return
        
        vm_idx = selection[0]
        vm_entry = self.vm_listbox.get(vm_idx)
        vm_name = vm_entry.split(" ")[0]
        
        if vm_name not in self.vms:
            messagebox.showerror("Error", f"VM '{vm_name}' not found")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete VM '{vm_name}'?"):
            return
        
        # Remove VM configuration
        del self.vms[vm_name]
        self.save_vms()
        
        # Update UI
        self.update_vm_list()
        
        messagebox.showinfo("Success", f"VM '{vm_name}' deleted successfully")

    def browse_boot_iso(self):
        """Open file dialog to select ISO image for booting"""
        iso_file = filedialog.askopenfilename(
            title="Select ISO Image for Boot",
            filetypes=[("ISO images", "*.iso"), ("All files", "*.*")]
        )
        if iso_file:
            self.boot_iso_path.set(iso_file)
            # Automatically select ISO boot option when an ISO is chosen
            self.boot_option.set("iso")

    def check_selected_disk_status(self):
        """Check the status of the disk for the selected VM"""
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a VM first")
            return
        
        vm_idx = selection[0]
        vm_entry = self.vm_listbox.get(vm_idx)
        vm_name = vm_entry.split(" ")[0]
        
        if vm_name not in self.vms:
            messagebox.showerror("Error", f"VM '{vm_name}' not found")
            return
        
        vm_info = self.vms[vm_name]
        disk_name = vm_info["disk"]
        
        if disk_name not in self.vdisks:
            messagebox.showerror("Error", f"Virtual disk '{disk_name}' not found")
            return
        
        disk_path = self.vdisks[disk_name]["path"]
        
        # Check disk status
        is_modified, details = qemu_utils.check_disk_status(disk_path)
        
        if is_modified:
            messagebox.showinfo("Disk Status", 
                f"Disk '{disk_name}' appears to have been modified.\n\n"
                f"Details: {details}\n\n"
                "This disk likely has data or an operating system installed.")
        else:
            messagebox.showwarning("Disk Status", 
                f"Disk '{disk_name}' appears to be empty or unused.\n\n"
                f"Details: {details}\n\n"
                "You may need to install an operating system to this disk.")

    def force_boot_with_iso(self):
        """Force start a VM with an ISO, regardless of current settings"""
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a VM first")
            return
        
        vm_idx = selection[0]
        vm_entry = self.vm_listbox.get(vm_idx)
        vm_name = vm_entry.split(" ")[0]
        
        # Ask for ISO
        iso_file = filedialog.askopenfilename(
            title="Select ISO Image for Boot",
            filetypes=[("ISO images", "*.iso"), ("All files", "*.*")]
        )
        
        if not iso_file or not os.path.exists(iso_file):
            messagebox.showerror("Error", "Please select a valid ISO file")
            return
        
        # Start VM with forced ISO boot
        self.start_vm_by_name(vm_name, boot_with_iso=True, iso_path=iso_file)


if __name__ == "__main__":
    root = tk.Tk()
    app = QemuVMManager(root)
    root.mainloop() 