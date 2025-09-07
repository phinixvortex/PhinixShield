import time
import psutil
import requests
from scapy.all import sniff
from datetime import datetime
import subprocess
import threading
from rich.table import Table
from rich.console import Console

SERVER_URL = "http://127.0.0.1:5000/agent_data"
HOST_NAME = "Host1"
SEND_INTERVAL = 5
MAX_ATTEMPTS = 10

blocked_ips = {}  
ip_attempts = {}  

console = Console()

# ==========================
# Network Monitoring
# ==========================
def parse_packet(pkt):
    try:
        if pkt.haslayer("IP"):
            return {
                "time": datetime.now().strftime("%H:%M:%S"),
                "src": pkt["IP"].src,
                "dst": pkt["IP"].dst,
                "proto": str(pkt["IP"].proto),
                "status": "Suspicious" if pkt["IP"].ttl < 32 else "Allowed"
            }
    except Exception:
        pass
    return None

def start_network_monitor():
    results = []
    try:
        packets = sniff(count=5, timeout=1)
        for pkt in packets:
            parsed = parse_packet(pkt)
            if parsed:
                results.append(parsed)
    except Exception:
        pass
    return results

# ==========================
# Endpoint Monitoring
# ==========================
def start_endpoint_monitor():
    results = []
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    processes = len(psutil.pids())
    results.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "cpu": f"{cpu}%",
        "ram": f"{ram}%",
        "processes": str(processes),
        "status": "High Load" if cpu > 80 or ram > 80 else "Normal"
    })
    return results

# ==========================
# Auto-Response (IP Blocking)
# ==========================
def block_ip(ip):
    if ip not in blocked_ips:
        try:
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
            blocked_ips[ip] = datetime.now()
            console.print(f"❌ Blocked IP: {ip}", style="red")
        except Exception as e:
            console.print(f"⚠️ Failed to block IP {ip}: {e}", style="yellow")

def start_auto_response(network_data):
    for row in network_data:
        ip = row["src"]
        if row["status"] == "Suspicious":
            ip_attempts[ip] = ip_attempts.get(ip, 0) + 1
            if ip_attempts[ip] >= MAX_ATTEMPTS:
                block_ip(ip)

# ==========================
# Display Summary Table
# ==========================
def display_summary(network_data, endpoint_data):
    table = Table(title=f"[bold cyan]Agent Summary ({HOST_NAME})[/bold cyan]")

    # Network Table
    table.add_column("Time", style="yellow")
    table.add_column("Src IP", style="cyan")
    table.add_column("Dst IP", style="green")
    table.add_column("Proto", style="magenta")
    table.add_column("Status", style="red")

    if not network_data:
        table.add_row("-", "-", "-", "-", "-")
    else:
        for row in network_data:
            table.add_row(row["time"], row["src"], row["dst"], row["proto"], row["status"])

    # Endpoint info (CPU/RAM)
    if endpoint_data:
        ep = endpoint_data[-1]
        table.add_row(f"CPU: {ep['cpu']}", f"RAM: {ep['ram']}", f"Processes: {ep['processes']}", ep['status'], "-")

    # Blocked IPs
    if blocked_ips:
        table.add_row("Blocked IPs:", "-", "-", "-", ", ".join(blocked_ips.keys()))

    console.clear()
    console.print(table)

# ==========================
# Send Data to Server
# ==========================
def send_data_to_server():
    while True:
        network_data = start_network_monitor()
        endpoint_data = start_endpoint_monitor()
        start_auto_response(network_data)

        payload = {
            "host": HOST_NAME,
            "network_data": network_data,
            "endpoint_data": endpoint_data,
            "blocked_ips": [{"ip": k, "blocked_time": v.strftime("%H:%M:%S")} for k,v in blocked_ips.items()]
        }

        try:
            requests.post(SERVER_URL, json=payload, timeout=2)
        except Exception as e:
            console.print(f"[Agent] Failed to send data: {e}", style="yellow")

        display_summary(network_data, endpoint_data)
        time.sleep(SEND_INTERVAL)

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    threading.Thread(target=send_data_to_server, daemon=True).start()
    while True:
        time.sleep(1)
