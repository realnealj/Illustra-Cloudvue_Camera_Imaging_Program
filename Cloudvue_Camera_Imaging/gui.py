import tkinter as tk
import threading
import queue
import Network_Scanner
import chrome_opener
import partner_code

# ============================================================
# THREAD-SAFE LOGGING + STATUS QUEUE
# ============================================================
log_queue = queue.Queue()
status_queue = queue.Queue()

def log_message(msg):
    log_queue.put(msg)

def update_camera_status(ip, color):
    # color: "gray", "yellow", "green", "red"
    status_queue.put((ip, color))


# ============================================================
# PROCESS LOG + STATUS QUEUE EVERY 100ms
# ============================================================
def process_queues():
    # Handle log messages
    while True:
        try:
            msg = log_queue.get_nowait()
        except queue.Empty:
            break

        log_text.config(state="normal")
        log_text.insert("end", msg + "\n")
        log_text.see("end")
        log_text.config(state="disabled")

    # Handle status indicator changes
    while True:
        try:
            ip, color = status_queue.get_nowait()
        except queue.Empty:
            break

        if ip in ip_status_indicators:
            canvas, circle = ip_status_indicators[ip]
            canvas.itemconfig(circle, fill=color)

    window.after(100, process_queues)


# ============================================================
# WRAPPER TO CALL YOUR partner_code FUNCTION IN THREADS
# ============================================================
def threaded_partner_process(selected_ips, partner_code_value):
    threads = []

    for ip in selected_ips:
        update_camera_status(ip, "yellow")
        log_message(f"[{ip}] Starting processing...")

        t = threading.Thread(
            target=single_camera_partner_action,
            args=(ip, partner_code_value),
            daemon=True
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    log_message("All cameras finished processing.")


def single_camera_partner_action(ip, partner_code_value):
    try:
        partner_code.ping_and_reopen([ip], partner_code_value)

        update_camera_status(ip, "green")
        log_message(f"[{ip}] Completed successfully.")
    except Exception as e:
        update_camera_status(ip, "red")
        log_message(f"[{ip}] ERROR: {e}")


# ============================================================
# GUI FUNCTIONS (your existing ones, enhanced)
# ============================================================
def run_partner_code():
    selected_indices = ip_listbox.curselection()
    if not selected_indices:
        status_label.config(text="No cameras selected.", fg="red")
        return

    selected_ips = [ip_listbox.get(i).split()[1] for i in selected_indices]
    partner_code_value = partner_code_entry.get().strip()

    if not partner_code_value:
        status_label.config(text="Partner code cannot be empty.", fg="red")
        return

    status_label.config(text="Processing partner code…", fg="white")
    log_message("\n=== Starting Partner Join Process ===")

    threading.Thread(
        target=threaded_partner_process,
        args=(selected_ips, partner_code_value),
        daemon=True
    ).start()


def start_process():
    status_label.config(text="Scanning network for devices...")
    window.update_idletasks()

    global ip_mac_pairs
    ip_mac_pairs = Network_Scanner.get_interface_info()

    update_listbox(ip_mac_pairs)
    status_label.config(text="Scan complete.")
    begin_button.config(state=tk.NORMAL)


def update_listbox(pairs):
    ip_listbox.delete(0, tk.END)

    # Reset status indicators
    ip_status_indicators.clear()

    for ip, mac in pairs:
        display_text = f"IP: {ip:<15}    MAC: {mac:<20}"
        ip_listbox.insert(tk.END, display_text)

        # Create a status indicator for each IP
        canvas = tk.Canvas(ip_listbox, width=15, height=15, bg="#333333", highlightthickness=0)
        circle = canvas.create_oval(2, 2, 13, 13, fill="gray")
        ip_status_indicators[ip] = (canvas, circle)


def run_open_in_chrome():
    selected_indices = ip_listbox.curselection()
    selected_ips = [ip_listbox.get(i).split()[1] for i in selected_indices]
    chrome_opener.open_in_chrome(selected_ips)


def join_to_cloudvue_partner():
    run_partner_code()


def filter_listbox(event=None):
    search_text = search_entry.get().strip().lower()
    if not search_text:
        update_listbox(ip_mac_pairs)
        return

    filtered = [(ip, mac) for ip, mac in ip_mac_pairs if search_text in mac.lower()]
    update_listbox(filtered)


# ============================================================
# BUILD GUI
# ============================================================
window = tk.Tk()
window.title("Cloudvue Camera Imaging Program")
window.geometry("700x700")
window.configure(bg="#222222")

frame = tk.Frame(window, padx=20, pady=20, bg="#333333", relief="groove", bd=2)
frame.pack(expand=True, fill="both", padx=20, pady=20)

welcome_message = (
    "Welcome to Cloudvue Camera Imaging Program.\n\n"
    "Ensure your cameras are connected to the same network as your computer.\n"
    "Click Start to discover connected devices."
)
welcome_label = tk.Label(
    frame, text=welcome_message, wraplength=500, justify="center",
    font=("Arial", 10), bg="#333333", fg="#DDDDDD"
)
welcome_label.pack(pady=20)

start_button = tk.Button(
    frame, text="Scan", font=("Arial", 12, "bold"), command=start_process,
    bg="#4B4A9C", fg="white", width=10,
)
start_button.pack(pady=10)

status_label = tk.Label(frame, text="", font=("Arial", 8), bg="#333333", fg="#AAAAAA")
status_label.pack(pady=(5, 0))

output_frame = tk.Frame(frame, bg="#333333")
output_frame.pack(fill="both", pady=(10, 6))

button_frame = tk.Frame(output_frame, bg="#333333")
button_frame.pack(side="right", anchor="n", padx=10)

begin_button = tk.Button(
    button_frame, text="1. Setup Camera/Upgrade Firmware",
    font=("Arial", 8, "bold"), command=run_open_in_chrome,
    bg="#4B4A9C", fg="white", width=28, state=tk.DISABLED
)
begin_button.pack(pady=(0, 5))

ip_listbox = tk.Listbox(
    output_frame, selectmode=tk.MULTIPLE, bg="#333333", fg="#DDDDDD",
    font=("Arial", 10), height=10
)
ip_listbox.pack(side="left", fill="both", expand=True)

# Track IP status lights
ip_status_indicators = {}

search_frame = tk.Frame(frame, bg="#333333")
search_frame.pack(fill="x", pady=(6, 6))

search_label = tk.Label(
    search_frame, text="Search MAC:", font=("Arial", 10),
    bg="#333333", fg="#DDDDDD"
)
search_label.pack(side="left", padx=(10, 5))

search_entry = tk.Entry(
    search_frame, font=("Arial", 10),
    bg="#222222", fg="#DDDDDD", width=30,
    insertbackground="#DDDDDD"
)
search_entry.pack(side="left", padx=5)
search_entry.bind("<KeyRelease>", filter_listbox)

partner_frame = tk.Frame(frame, bg="#333333")
partner_frame.pack(fill="x", pady=(10, 6))

partner_code_label = tk.Label(
    partner_frame, text="Enter Partner Code:",
    font=("Arial", 10), bg="#333333", fg="#DDDDDD"
)
partner_code_label.pack(side="left", padx=(10, 5))

partner_code_entry = tk.Entry(
    partner_frame, font=("Arial", 10),
    bg="#222222", fg="#DDDDDD", width=30,
    insertbackground="#DDDDDD"
)
partner_code_entry.pack(side="left", padx=5)

submit_button = tk.Button(
    partner_frame, text="2. Submit Partner Code and Join to Cloudvue",
    font=("Arial", 8), command=join_to_cloudvue_partner,
    bg="#4B4A9C", fg="white"
)
submit_button.pack(side="left", padx=(5, 10))

# ============================================================
# PROGRESS LOG WINDOW
# ============================================================
log_text = tk.Text(
    frame, height=10, width=80, bg="#111111",
    fg="#00FF00", font=("Courier", 9), state="disabled"
)
log_text.pack(fill="both", expand=False, pady=(15, 5))


# ============================================================
# START QUEUE PROCESSING LOOP
# ============================================================
window.after(100, process_queues)

# ============================================================
# MAINLOOP
# ============================================================
window.mainloop()
