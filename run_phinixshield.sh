#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start server in a new terminal
gnome-terminal -- bash -c "echo 'Starting PhinixShield Server...'; python3 server/phinixshield_server.py; exec bash"

# Wait a few seconds before starting agent
sleep 5

# Start agent in a new terminal
gnome-terminal -- bash -c "echo 'Starting PhinixShield Agent...'; sudo python3 agents/phinixshield_agent.py; exec bash"
