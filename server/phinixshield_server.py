import threading
import time
from datetime import datetime
from collections import deque
from flask import Flask, request, jsonify
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
import sys
import select

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)

# ============================================================
# GLOBAL DATA
# ============================================================
agents_data = {}         # Data from agents
SHOW_BLOCKED_IPS = True
SHOW_CPU_RAM = True
cpu_history = {}         
ram_history = {}         

# ============================================================
# DASHBOARD TABLES
# ============================================================
def build_network_table(agent_name, data):
    table = Table(title=f"🌐 Network Monitor ({agent_name})")
    table.add_column("Time", style="yellow")
    table.add_column("Source IP", style="cyan")
    table.add_column("Destination IP", style="green")
    table.add_column("Protocol", style="magenta")
    table.add_column("Status", style="red")
    if not data:
        table.add_row("-", "-", "-", "-", "-")
    else:
        for row in data:
            table.add_row(row["time"], row["src"], row["dst"], row["proto"], row["status"])
    return table

def build_endpoint_table(agent_name, data):
    table = Table(title=f"🖥️ Endpoint Monitor ({agent_name})")
    table.add_column("Time", style="yellow")
    table.add_column("CPU", style="cyan")
    table.add_column("RAM", style="green")
    table.add_column("Processes", style="magenta")
    table.add_column("Status", style="red")
    if not data:
        table.add_row("-", "-", "-", "-", "-")
    else:
        for row in data:
            table.add_row(row["time"], row["cpu"], row["ram"], row["processes"], row["status"])
    return table

def build_blocked_ips_table(agent_name, data):
    table = Table(title=f"⛔ Blocked IPs ({agent_name})")
    table.add_column("IP", style="red")
    table.add_column("Blocked Time", style="yellow")
    if not data:
        table.add_row("-", "-")
    else:
        for row in data:
            table.add_row(row["ip"], row["blocked_time"])
    return table

def build_suspicious_ips_table(agent_name, network_data):
    table = Table(title=f"⚠️ Last 10 Suspicious IPs ({agent_name})")
    table.add_column("Time", style="yellow")
    table.add_column("Source IP", style="cyan")
    table.add_column("Destination IP", style="green")
    table.add_column("Protocol", style="magenta")
    table.add_column("Status", style="red")

    if not network_data:
        table.add_row("-", "-", "-", "-", "-")
    else:
        suspicious = [pkt for pkt in network_data if pkt["status"] == "Suspicious"][-10:]
        if not suspicious:
            table.add_row("-", "-", "-", "-", "-")
        else:
            for row in suspicious:
                table.add_row(row["time"], row["src"], row["dst"], row["proto"], row["status"])
    return table

# ============================================================
# CPU/RAM Text Display
# ============================================================
def update_history(host, cpu, ram):
    if host not in cpu_history:
        cpu_history[host] = deque(maxlen=60)
        ram_history[host] = deque(maxlen=60)
    cpu_history[host].append(cpu)
    ram_history[host].append(ram)

def build_cpu_ram_panel(host):
    if host not in cpu_history or not cpu_history[host]:
        return Panel("No data yet", title=f"📊 CPU/RAM ({host})")
    cpu = list(cpu_history[host])[-1]
    ram = list(ram_history[host])[-1]
    return Panel(f"CPU: {cpu}%\nRAM: {ram}%", title=f"📊 CPU/RAM ({host})")

# ============================================================
# DASHBOARD LAYOUT
# ============================================================
def make_layout():
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    return layout

def start_dashboard():
    layout = make_layout()
    layout["header"].update("🚀 PhinixShield Central Dashboard")
    layout["footer"].update("Press Ctrl+C to exit")
    print("Server started!")
    with Live(layout, refresh_per_second=1, screen=True):
        while True:
            for agent, data in agents_data.items():
                network_data = data.get("network_data", [])
                endpoint_data = data.get("endpoint_data", [])

                layout["main"].update(build_network_table(agent, network_data))
                layout["main"].update(build_endpoint_table(agent, endpoint_data))
                if SHOW_BLOCKED_IPS:
                    layout["main"].update(build_blocked_ips_table(agent, data.get("blocked_ips", [])))

                # CPU/RAM
                if SHOW_CPU_RAM and endpoint_data:
                    cpu = float(endpoint_data[-1]["cpu"].replace("%",""))
                    ram = float(endpoint_data[-1]["ram"].replace("%",""))
                    update_history(agent, cpu, ram)
                    layout["main"].update(build_cpu_ram_panel(agent))

                # Suspicious IPs
                layout["main"].update(build_suspicious_ips_table(agent, network_data))

            time.sleep(1)

# ============================================================
# FLASK ENDPOINT
# ============================================================
@app.route("/agent_data", methods=["POST"])
def receive_agent_data():
    try:
        data = request.json
        agents_data[data.get("host")] = data
        print(f"[Server] Received data from host: {data.get('host')}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[Server] Error receiving data: {e}")
        return jsonify({"status": "error", "error": str(e)}), 400

# ============================================================
# INTERACTIVE COMMANDS
# ============================================================
def interactive_commands():
    global SHOW_BLOCKED_IPS, SHOW_CPU_RAM
    print("\n🔹 Commands:\n  u <host> <ip>   -> Unblock IP\n  g -> Toggle CPU/RAM display\n  b -> Toggle blocked IPs\n  q -> Quit\n")
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 1)
        if ready:
            cmd = sys.stdin.readline().strip()
            if cmd.startswith("u "):
                try:
                    _, host, ip = cmd.split()
                    host_data = agents_data.get(host)
                    if host_data and "blocked_ips" in host_data:
                        host_data["blocked_ips"] = [b for b in host_data["blocked_ips"] if b["ip"] != ip]
                        print(f"✅ Manually unblocked {ip} for {host}")
                    else:
                        print(f"⚠️ Host or IP not found")
                except Exception as e:
                    print(f"⚠️ Error: {e}")
            elif cmd == "g":
                SHOW_CPU_RAM = not SHOW_CPU_RAM
                print(f"📊 CPU/RAM display: {SHOW_CPU_RAM}")
            elif cmd == "b":
                SHOW_BLOCKED_IPS = not SHOW_BLOCKED_IPS
                print(f"⛔ Blocked IPs table display: {SHOW_BLOCKED_IPS}")
            elif cmd == "q":
                print("Exiting dashboard...")
                sys.exit(0)
            else:
                print("⚠️ Unknown command")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    threading.Thread(target=interactive_commands, daemon=True).start()
    threading.Thread(target=start_dashboard, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
