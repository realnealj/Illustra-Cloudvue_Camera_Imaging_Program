import subprocess
import re

def get_interface_info():
    # Run the "ip addr" command
    result = subprocess.run(["ip", "addr"], capture_output=True, text=True)

    # Define the interface patterns to search for
    interface_patterns = [
        r"eth[0-9]:", r"eno[0-9]:", r"ens[0-9]:",
        r"enp[0-9]s[0-9]:", r"em[0-9]:"
    ]

    # Prepare regex patterns for matching interface and IP
    interface_regex = re.compile(r"(" + "|".join(interface_patterns) + r")")
    ip_regex = re.compile(r"inet (\d+\.\d+\.\d+\.\d+)")
    ip_mac_pairs = []  # Collect IP and MAC pairs for display
    ip_addresses = []  # Collect IP addresses for Chrome

    # Parse the command output
    lines = result.stdout.splitlines()
    current_interface = None

    for line in lines:
        interface_match = interface_regex.search(line)
        if interface_match:
            current_interface = interface_match.group(0).strip(":")

        # Check for IPv4 addresses in the interface section
        if current_interface:
            ip_match = ip_regex.search(line)
            if ip_match:
                ipv4_address = ip_match.group(1)
                subnet = ".".join(ipv4_address.split(".")[:3])

                # Run nmap command for subnet scanning
                nmap_command = f"nmap -sP {subnet}.0/24"
                nmap_result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

                # Use "ip neighbor" or "arp" to gather IP/MAC pairs
                neighbor_command = "ip neighbor show | grep -v 'FAILED' | grep -v 'INCOMPLETE' | sort -d"
                neighbor_result = subprocess.run(neighbor_command, shell=True, capture_output=True, text=True)

                if neighbor_result.returncode != 0 or not neighbor_result.stdout:
                    arp_command = "arp -n | grep -v '(incomplete)' | sort -d"
                    arp_result = subprocess.run(arp_command, shell=True, capture_output=True, text=True)
                    neighbor_output = arp_result.stdout
                else:
                    neighbor_output = neighbor_result.stdout

                # Extract IP and MAC from neighbor/arp output
                for line in neighbor_output.splitlines():
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    mac_match = re.search(r'([0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5})', line)
                    if ip_match and mac_match:
                        ip = ip_match.group(1)
                        mac = mac_match.group(1)
                        ip_mac_pairs.append((ip, mac))  # Add for display
                        ip_addresses.append(ip)  # Add for Chrome

                current_interface = None  # Reset for next interface

    unique_ip_mac_pairs = list(set(ip_mac_pairs))

    # Return IP and MAC pairs
    return unique_ip_mac_pairs

if __name__ == "__main__":
    # Display IP and MAC for debugging
    ip_mac_pairs = get_interface_info()
    print("\nDiscovered IP and MAC addresses:")
    for ip, mac in ip_mac_pairs:
        print(f"IP Address: {ip}, MAC Address: {mac}")
