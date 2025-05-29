"""
Cell War Driver GUI Launcher for Windows

This script provides a graphical user interface for launching the Cell War Driver program on Windows.
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_available_ports():
    """Get available COM ports."""
    return [port.device for port in serial.tools.list_ports.comports()]


def run_command():
    """Run the Cell War Driver with the selected options."""
    # Build command arguments
    args = []
    
    # Port settings
    if port_var.get() != "Auto-detect":
        args.extend(["--port", port_var.get()])
    
    # Baudrate
    args.extend(["--baudrate", baudrate_var.get()])
    
    # Timeout
    args.extend(["--timeout", timeout_var.get()])
    
    # Command delay
    args.extend(["--command-delay", delay_var.get()])
    
    # Retry count
    args.extend(["--retry-count", retry_var.get()])
    
    # Log directory
    if log_dir_var.get():
        args.extend(["--log-dir", log_dir_var.get()])
    
    # Log level
    args.extend(["--log-level", log_level_var.get()])
    
    # CSV directory
    if csv_dir_var.get():
        args.extend(["--csv-dir", csv_dir_var.get()])
    
    # CSV filename
    if csv_filename_var.get():
        args.extend(["--csv-filename", csv_filename_var.get()])
    
    # Build the command string for display
    cmd_str = "python main.py " + " ".join(args)
    command_display.delete(1.0, tk.END)
    command_display.insert(tk.END, cmd_str)
    
    try:
        # Run the command
        python_path = os.path.join(SCRIPT_DIR, "venv", "Scripts", "python.exe")
        if not os.path.exists(python_path):
            python_path = "python"  # Fall back to system Python
        
        # Prepare for the subprocess
        main_script = os.path.join(SCRIPT_DIR, "main.py")
        cmd = [python_path, main_script] + args
        
        # Set status
        status_label.config(text="Status: Running...")
        root.update()
        
        # Run the command
        process = subprocess.Popen(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   cwd=SCRIPT_DIR)
        
        # Display output in real-time
        output_display.delete(1.0, tk.END)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_display.insert(tk.END, output)
                output_display.see(tk.END)
                root.update()
        
        # Get any remaining output and errors
        stdout, stderr = process.communicate()
        output_display.insert(tk.END, stdout)
        
        if stderr:
            output_display.insert(tk.END, "\nERRORS:\n" + stderr)
        
        # Set status
        if process.returncode == 0:
            status_label.config(text="Status: Completed successfully")
        else:
            status_label.config(text=f"Status: Failed (return code {process.returncode})")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Cell War Driver: {str(e)}")
        status_label.config(text="Status: Error")


def refresh_ports():
    """Refresh the list of available ports."""
    ports = get_available_ports()
    port_dropdown['values'] = ["Auto-detect"] + ports
    if not ports:
        status_label.config(text="Status: No COM ports detected")
    else:
        status_label.config(text=f"Status: Found {len(ports)} COM ports")


def browse_dir(var):
    """Browse for a directory."""
    directory = filedialog.askdirectory(initialdir=SCRIPT_DIR)
    if directory:
        var.set(directory)


def check_env():
    """Check and set up the Python environment."""
    venv_dir = os.path.join(SCRIPT_DIR, "venv")
    
    if not os.path.exists(venv_dir):
        result = messagebox.askyesno(
            "Virtual Environment",
            "Python virtual environment not found. Create it now?\n\n"
            "This will set up a dedicated environment for Cell War Driver."
        )
        
        if result:
            status_label.config(text="Status: Setting up environment...")
            root.update()
            
            try:
                # Create virtual environment
                subprocess.run([sys.executable, "-m", "venv", venv_dir], 
                               check=True, cwd=SCRIPT_DIR)
                
                # Install requirements
                pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
                req_file = os.path.join(SCRIPT_DIR, "requirements.txt")
                subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                               check=True, cwd=SCRIPT_DIR)
                subprocess.run([pip_path, "install", "-r", req_file], 
                               check=True, cwd=SCRIPT_DIR)
                
                status_label.config(text="Status: Environment set up successfully")
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    "Setup Error",
                    f"Failed to set up environment: {str(e)}"
                )
                status_label.config(text="Status: Environment setup failed")
        else:
            status_label.config(text="Status: Using system Python")
    else:
        status_label.config(text="Status: Ready (virtual environment found)")


# Create the main window
root = tk.Tk()
root.title("Cell War Driver GUI Launcher")
root.geometry("800x700")
root.minsize(700, 600)

# Variables
port_var = tk.StringVar(value="Auto-detect")
baudrate_var = tk.StringVar(value="115200")
timeout_var = tk.StringVar(value="1.0")
delay_var = tk.StringVar(value="0.5")
retry_var = tk.StringVar(value="3")
log_dir_var = tk.StringVar(value=os.path.join(SCRIPT_DIR, "output"))
log_level_var = tk.StringVar(value="INFO")
csv_dir_var = tk.StringVar(value=os.path.join(SCRIPT_DIR, "output"))
csv_filename_var = tk.StringVar(value="cell_data.csv")

# Main frame
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Connection settings frame
conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding=10)
conn_frame.pack(fill=tk.X, padx=5, pady=5)

# Port selection with refresh button
port_frame = ttk.Frame(conn_frame)
port_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(port_frame, text="COM Port:").pack(side=tk.LEFT)
port_dropdown = ttk.Combobox(port_frame, textvariable=port_var, width=15)
port_dropdown.pack(side=tk.LEFT, padx=5)
refresh_btn = ttk.Button(port_frame, text="Refresh", command=refresh_ports)
refresh_btn.pack(side=tk.LEFT, padx=5)

# Baudrate
baud_frame = ttk.Frame(conn_frame)
baud_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(baud_frame, text="Baud Rate:").pack(side=tk.LEFT)
baudrate_combo = ttk.Combobox(baud_frame, textvariable=baudrate_var, width=15)
baudrate_combo['values'] = ("9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600")
baudrate_combo.pack(side=tk.LEFT, padx=5)

# Timeout
timeout_frame = ttk.Frame(conn_frame)
timeout_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(timeout_frame, text="Timeout (s):").pack(side=tk.LEFT)
timeout_entry = ttk.Entry(timeout_frame, textvariable=timeout_var, width=10)
timeout_entry.pack(side=tk.LEFT, padx=5)

# Command settings frame
cmd_frame = ttk.LabelFrame(main_frame, text="Command Settings", padding=10)
cmd_frame.pack(fill=tk.X, padx=5, pady=5)

# Command delay
delay_frame = ttk.Frame(cmd_frame)
delay_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(delay_frame, text="Command Delay (s):").pack(side=tk.LEFT)
delay_entry = ttk.Entry(delay_frame, textvariable=delay_var, width=10)
delay_entry.pack(side=tk.LEFT, padx=5)

# Retry count
retry_frame = ttk.Frame(cmd_frame)
retry_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(retry_frame, text="Retry Count:").pack(side=tk.LEFT)
retry_entry = ttk.Entry(retry_frame, textvariable=retry_var, width=10)
retry_entry.pack(side=tk.LEFT, padx=5)

# Output settings frame
output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding=10)
output_frame.pack(fill=tk.X, padx=5, pady=5)

# Log directory
log_dir_frame = ttk.Frame(output_frame)
log_dir_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(log_dir_frame, text="Log Directory:").pack(side=tk.LEFT)
log_dir_entry = ttk.Entry(log_dir_frame, textvariable=log_dir_var, width=40)
log_dir_entry.pack(side=tk.LEFT, padx=5)
log_dir_btn = ttk.Button(log_dir_frame, text="Browse", 
                          command=lambda: browse_dir(log_dir_var))
log_dir_btn.pack(side=tk.LEFT, padx=5)

# Log level
log_level_frame = ttk.Frame(output_frame)
log_level_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(log_level_frame, text="Log Level:").pack(side=tk.LEFT)
log_level_combo = ttk.Combobox(log_level_frame, textvariable=log_level_var, width=15)
log_level_combo['values'] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
log_level_combo.pack(side=tk.LEFT, padx=5)

# CSV directory
csv_dir_frame = ttk.Frame(output_frame)
csv_dir_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(csv_dir_frame, text="CSV Directory:").pack(side=tk.LEFT)
csv_dir_entry = ttk.Entry(csv_dir_frame, textvariable=csv_dir_var, width=40)
csv_dir_entry.pack(side=tk.LEFT, padx=5)
csv_dir_btn = ttk.Button(csv_dir_frame, text="Browse", 
                           command=lambda: browse_dir(csv_dir_var))
csv_dir_btn.pack(side=tk.LEFT, padx=5)

# CSV filename
csv_filename_frame = ttk.Frame(output_frame)
csv_filename_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(csv_filename_frame, text="CSV Filename:").pack(side=tk.LEFT)
csv_filename_entry = ttk.Entry(csv_filename_frame, textvariable=csv_filename_var, width=40)
csv_filename_entry.pack(side=tk.LEFT, padx=5)

# Command display
cmd_display_frame = ttk.LabelFrame(main_frame, text="Command to Run", padding=10)
cmd_display_frame.pack(fill=tk.X, padx=5, pady=5)
command_display = tk.Text(cmd_display_frame, height=3, wrap=tk.WORD)
command_display.pack(fill=tk.X, padx=5, pady=5)

# Run button
run_btn = ttk.Button(main_frame, text="Run Cell War Driver", command=run_command)
run_btn.pack(padx=5, pady=5)

# Status label
status_label = ttk.Label(main_frame, text="Status: Starting up...")
status_label.pack(padx=5, pady=5)

# Output display
output_frame = ttk.LabelFrame(main_frame, text="Output", padding=10)
output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
output_display = tk.Text(output_frame, wrap=tk.WORD)
output_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Add scrollbar to output display
output_scrollbar = ttk.Scrollbar(output_display, orient=tk.VERTICAL, command=output_display.yview)
output_display.configure(yscrollcommand=output_scrollbar.set)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Initialize
refresh_ports()
check_env()

# Start the GUI
if __name__ == "__main__":
    root.mainloop()
