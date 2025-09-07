🚀 PhinixShield

PhinixShield is a terminal-based SOC (Security Operations Center) tool with a central server and agent system.  
It allows live network monitoring, endpoint monitoring (CPU/RAM/Processes), and auto-blocking suspicious IPs.

---

🔹 Features

- Live network monitoring per agent  
- Live CPU/RAM and process monitoring  
- Auto-block IPs after 10 suspicious attempts  
- View last 10 suspicious IPs per agent  
- View blocked IPs table in the dashboard  
- Local agent summary in the agent terminal  
- One-command launcher script (`run_phinixshield.sh`)  

---

🗂️ Folder Structure

PhinixShield/

│

├─ server/

│   └─ phinixshield_server.py   # Server dashboard + API

├─ agents/

│   └─ phinixshield_agent.py    # Agent sending network & endpoint data

├─ run_phinixshield.sh          # One-command launcher for server + agent

├─ requirements.txt             # Python dependencies

├─ README.md

└─ .gitignore

---

⚡ Installation

1. Clone the repository:

git clone git@github.com:phinixvortex/PhinixShield.git

cd PhinixShield

2. Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

3. Install required Python packages:

pip install -r requirements.txt


---

▶️ Running PhinixShield

Run the one-command launcher:

bash
./run_phinixshield.sh


What happens:

1. The server dashboard opens in a new terminal.  
2. The agent opens in a separate terminal and starts sending data.  
3. The dashboard updates live with:

- Network packets  
- CPU/RAM usage  
- Blocked IPs  
- Last 10 suspicious IPs  

---

🖥️ Server Commands

While the server terminal is active, you can type:

u <host> <ip>   -> Unblock an IP manually
g               -> Toggle CPU/RAM display
b               -> Toggle blocked IPs table
q               -> Quit the dashboard


---

🔹 Notes

- The agent requires sudo to block IPs via iptables.  
- Tested on Kali Linux / Ubuntu GNOME (for gnome-terminal). Adjust terminal commands if using XFCE or other environments.  
- Default max suspicious attempts is 10 before auto-blocking an IP.  
- Data is sent every 5 seconds from the agent to the server.  

---

📄 License

MIT License

Copyright (c) 2025 mohd Atif

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

👥 Contribution

Contributions are welcome! Open an issue or submit a pull request.  

---

⚙️ Future Improvements

- Auto-detect multiple agents on a LAN  
- Customizable alerts for CPU/RAM thresholds  
- Export logs to CSV or JSON  
- Web-based dashboard version
