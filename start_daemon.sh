#!/bin/bash
# Start the Voxink Dictation Daemon in the background
# This preserves the user's audio environment variables with sudo -E

cd "$(dirname "$0")"

# Kill any existing instance
sudo /usr/bin/pkill -f "python src/main.py" || true

echo "Starting Voxink in the background..."
nohup sudo -E /home/jab/projects/new/glaido-clone/.venv/bin/python /home/jab/projects/new/glaido-clone/src/main.py > /tmp/voxink.log 2>&1 &

echo "Dictation daemon is now running! (Logs: /tmp/voxink.log)"
echo "Press your configured hotkey to start speaking."
