import tkinter as tk
import Network_Scanner
import chrome_opener
import partner_code


def start_process():
    # Display "scanning" message
    status_label.config(text="Scanning network for devices...", font=("Arial", 8))
    window.update_idletasks()  # Update the GUI immediately to show the status message

    # Run the network scan and display IP/MAC addresses
    ip_mac_pairs = Network_Scanner.get_interface_info()
    ip_listbox.delete(0, tk.END)  # Clear previous output

    # Display IP addresses in the Listbox
    for ip, mac in ip_mac_pairs:
        ip_listbox.insert(tk.END, f"IP: {ip:<15}    MAC: {mac:<20}")

    # Update status to finished
    status_label.config(text="Scan complete.")
    begin_button.config(state=tk.NORMAL)  # Enable the Begin Process button



def run_open_in_chrome():
    # Retrieve selected IP addresses from Listbox
    selected_indices = ip_listbox.curselection()
    selected_ips = [ip_listbox.get(i).split()[1] for i in selected_indices]  # Extract only IPs

    # Pass the selected IPs to chrome_opener
    chrome_opener.open_in_chrome(selected_ips)


def join_to_cloudvue_partner():
    selected_indices = ip_listbox.curselection()
    selected_ips = [ip_listbox.get(i).split()[1] for i in selected_indices]  # Extract only IPs

    # Get the partner code from the entry box
    partner_code_value = partner_code_entry.get().strip()
    if not partner_code_value:
        status_label.config(text="Partner code cannot be empty.", fg="red")
        return

        # Pass the selected IPs and partner code to partner_code.py
    status_label.config(text="Joining to Cloudvue Partner...", font=("Arial", 8))
    window.update_idletasks()  # Update GUI immediately to show the status message

    partner_code.ping_and_reopen(selected_ips, partner_code_value)
    status_label.config(text="Join process complete.", font=("Arial", 8))

# Create the main application window
window = tk.Tk()
window.title("Cloudvue Camera Imaging Program")
window.geometry("700x500")
window.configure(bg="#222222")  # Dark background for night mode

# Create a frame for better alignment and aesthetics with dark mode styling
frame = tk.Frame(window, padx=20, pady=20, bg="#333333", relief="groove", bd=2)
frame.pack(expand=True, fill="both", padx=20, pady=20)

# Add the welcome message
welcome_message = (
    "Welcome to Cloudvue Camera Imaging Program.\n\n"
    "Ensure your cameras are connected to the same network as your computer.\n"
    "Click Start to discover connected devices."
)
welcome_label = tk.Label(
    frame,
    text=welcome_message,
    wraplength=500,
    justify="center",
    font=("Arial", 10),
    bg="#333333",
    fg="#DDDDDD",
)
welcome_label.pack(pady=20)

# Add the Start button
start_button = tk.Button(
    frame,
    text="Scan",
    font=("Arial", 12, "bold"),
    command=start_process,
    bg="#4B4A9C",
    fg="white",
    width=10,
)
start_button.pack(pady=10)

# Status label for scanning message
status_label = tk.Label(frame, text="", font=("Arial", 8), bg="#333333", fg="#AAAAAA")
status_label.pack(pady=(5, 0))

# Frame for the Begin Process button, Join Partner button, and Listbox for IP/MAC addresses
output_frame = tk.Frame(frame, bg="#333333")
output_frame.pack(fill="x", pady=(10, 6))

# Create a separate frame for buttons on the right side
button_frame = tk.Frame(output_frame, bg="#333333")
button_frame.pack(side="right", anchor="n", padx=10)

# Place the Begin Process button at the top of the button_frame
begin_button = tk.Button(
    button_frame,
    text="1. Setup Camera/Upgrade Firmware",
    font=("Arial", 8, "bold"),
    command=run_open_in_chrome,
    bg="#4B4A9C",
    fg="white",
    width=28,
    state=tk.DISABLED,
)
begin_button.pack(pady=(0, 5))  # Add spacing between buttons


# Listbox for displaying IP/MAC addresses with multiple selection enabled
ip_listbox = tk.Listbox(
    output_frame,
    selectmode=tk.MULTIPLE,
    bg="#333333",
    fg="#DDDDDD",
    font=("Arial", 10),
    height=10,
)
ip_listbox.pack(fill="both", expand=True)

# Frame for partner code input and submission
partner_frame = tk.Frame(frame, bg="#333333")
partner_frame.pack(fill="x", pady=(10, 6))

partner_code_label = tk.Label(
    partner_frame, text="Enter Partner Code:", font=("Arial", 10), bg="#333333", fg="#DDDDDD"
)
partner_code_label.pack(side="left", padx=(10, 5))

partner_code_entry = tk.Entry(
    partner_frame,
    font=("Arial", 10),
    bg="#222222",
    fg="#DDDDDD",
    width=30,
    insertbackground="#DDDDDD",  # Cursor color
)
partner_code_entry.pack(side="left", padx=5)

submit_button = tk.Button(
    partner_frame,
    text="2. Submit Partner Code and Join to Cloudvue",
    font=("Arial", 8),
    command=join_to_cloudvue_partner,
    bg="#4B4A9C",
    fg="white",
)
submit_button.pack(side="left", padx=(5, 10))

# Run the application
window.mainloop()
