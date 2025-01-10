import requests
import os
from xml.etree import ElementTree
from dotenv import load_dotenv
import re
import subprocess

load_dotenv()

# Environment variables
PYPI_WEBHOOK_URL = os.getenv("PYPI_WEBHOOK_URL")
DISCORD_ROLE_ID = os.getenv("DISCORD_ROLE_ID")
PYPI_RSS_FEED = "https://pypi.org/rss/project/maoto-agent/releases.xml"
LATEST_VERSION_FILE = "pypi-release-discord/latest_version.txt"
STATE_BRANCH = "state"

def is_stable_version(version):
    """Check if a version is a stable release."""
    return not re.search(r"(a|b|rc|alpha|beta|dev|pre)", version, re.IGNORECASE)

def get_latest_version():
    """Fetch the latest stable version of the package from the PyPI RSS feed."""
    response = requests.get(PYPI_RSS_FEED)
    response.raise_for_status()
    tree = ElementTree.fromstring(response.content)

    stable_versions = [
        item.find("title").text.split()[-1]
        for item in tree.findall(".//item")
        if is_stable_version(item.find("title").text.split()[-1])
    ]
    if stable_versions:
        return sorted(stable_versions, key=lambda v: list(map(int, v.split("."))), reverse=True)[0]
    return None

def read_last_version():
    """Read the last notified version from the state branch."""
    try:
        # Checkout the state branch and fetch the latest_version.txt
        subprocess.run(["git", "fetch", "origin", STATE_BRANCH], check=True)
        subprocess.run(["git", "checkout", STATE_BRANCH], check=True)

        if os.path.exists(LATEST_VERSION_FILE):
            with open(LATEST_VERSION_FILE, "r") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading last version: {e}")
    return None

def write_last_version(version):
    """Write the last notified version to the state branch."""
    try:
        with open(LATEST_VERSION_FILE, "w") as f:
            f.write(version)

        # Commit the updated file to the state branch
        subprocess.run(["git", "add", LATEST_VERSION_FILE], check=True)
        subprocess.run(["git", "commit", "-m", f"Update latest version to {version}"], check=True)
        subprocess.run(["git", "push", "origin", STATE_BRANCH], check=True)
    except Exception as e:
        print(f"Error writing last version: {e}")

def post_to_discord(version):
    """Send a notification to Discord."""
    embed = {
        "title": f"🚀 New Stable Release",
        "description": (
            f"### **[maoto-agent v{version}](https://pypi.org/project/maoto-agent/{version}/)**\n\n"
            f"The `maoto-agent` package has just been updated to version `{version}`!\n\n"
        ),
        "color": 16777215,
        "fields": [
            {"name": "What's New?", "value": "• Bug fixes\n• Performance improvements\n• New features", "inline": False},
            {"name": "Changelog", "value": f"[View Release Notes](https://pypi.org/project/maoto-agent/{version}/#history)", "inline": False},
        ],
        "footer": {"text": "Powered by Maoto", "icon_url": "https://media.licdn.com/dms/image/v2/D560BAQG20uEQ9O819w/company-logo_100_100/company-logo_100_100/0/1721651548902/automaoto_logo?e=1744243200&v=beta&t=9Ar-aVbEIp4YZOwPWlOJgGvcSnBICEw4iqrdTsVtdeg"},
    }

    role_mention = f"<@&{DISCORD_ROLE_ID}>"
    message = {
        "content": f"🎉 {role_mention} Our new stable release is live! 🎉",
        "embeds": [embed],
    }

    response = requests.post(PYPI_WEBHOOK_URL, json=message)
    response.raise_for_status()

def main():
    try:
        # Fetch the latest version from PyPI
        latest_version = get_latest_version()
        if not latest_version:
            print("No stable version found.")
            return

        # Read the last notified version from the state branch
        last_version = read_last_version()
        print(f"Last version: {last_version}, Latest version: {latest_version}")

        # Post to Discord if the version is new
        if latest_version != last_version:
            print(f"New version detected: {latest_version}. Sending notification.")
            post_to_discord(latest_version)
            write_last_version(latest_version)
        else:
            print("No new version detected. Latest version already notified.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
