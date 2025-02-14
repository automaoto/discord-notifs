from maoto_agent import *
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .secrets_status
load_dotenv('.secrets_status')
SERVER_WEBHOOK_URL = os.getenv("SERVER_WEBHOOK_URL")  # Discord Webhook URL
STATUS_FILE = "server-status/latest_status.txt"  # File to track last status

def read_last_status():
    """Read the last known status from the status file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()
    return None  # Return None if the file doesn't exist

def write_last_status(status):
    """Write the current status to the status file."""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        f.write(status)

def send_discord_notification(is_up):
    """Send a notification to Discord when the server status changes."""
    status_message = "🟢 **Server is UP**" if is_up else "🔴 **Server is DOWN**"
    payload = {
        "content": status_message,
        "username": "MAOTO Status",
    }
    response = requests.post(SERVER_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"Notification sent: {status_message}")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

def check_server_status():
    """Check the server status and send a notification if it changes."""
    try:
        # Initialize the agent
        agent = Maoto(connection_mode='no_nat')
        is_server_up = agent.check_status()  # True if server is UP, False otherwise

        # Read the last status from the state file
        last_status = read_last_status()
        current_status = "UP" if is_server_up else "DOWN"

        # Notify only if the status has changed
        if current_status != last_status:
            send_discord_notification(is_server_up)
            write_last_status(current_status)
        else:
            print(f"No status change. Server is still {current_status}.")
    except Exception as e:
        print(f"Error checking server status: {e}")
        # If there's an error, assume server is down and update status if needed
        if read_last_status() != "DOWN":
            send_discord_notification(False)
            write_last_status("DOWN")

if __name__ == "__main__":
    check_server_status()
