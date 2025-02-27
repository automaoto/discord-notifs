import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .secrets_status
load_dotenv('.secrets_status')
SERVER_WEBHOOK_URL = os.getenv("SERVER_WEBHOOK_URL")
STATUS_FILE = "server_status/latest_status.txt"  # JSON file to track last statuses

def read_last_status():
    """Read the last known statuses from the status file."""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading status file: {e}")
    return {}

def write_last_status(status_dict):
    """Write the current statuses to the status file."""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status_dict, f)

def check_endpoint(url):
    """Check the given endpoint and return 'UP' if healthy, otherwise 'DOWN'."""
    try:
        response = requests.get(url, timeout=10)
        return "UP" if response.status_code == 200 else "DOWN"
    except Exception:
        return "DOWN"

def send_discord_notification(statuses):
    """Send a Discord notification with the current statuses."""
    message = (
        "**Server Status Update**\n"
        f"Marketplace: {'🟢 UP' if statuses['marketplace'] == 'UP' else '🔴 DOWN'}\n"
        f"Assistant: {'🟢 UP' if statuses['assistant'] == 'UP' else '🔴 DOWN'}"
    )
    payload = {
        "content": message,
        "username": "MAOTO Status",
    }
    response = requests.post(SERVER_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

def main():
    # Define the health check endpoints for each server
    endpoints = {
        "marketplace": "https://mp.maoto.world/healthz",
        "assistant": "https://telegram.maoto.world/healthz"
    }
    current_statuses = {}
    for key, url in endpoints.items():
        current_statuses[key] = check_endpoint(url)
    
    last_statuses = read_last_status()
    
    # Send notification only if statuses have changed
    if current_statuses != last_statuses:
        send_discord_notification(current_statuses)
        write_last_status(current_statuses)
    else:
        print("Status unchanged; no notification sent.")

if __name__ == "__main__":
    main()
