import requests
import os
from xml.etree import ElementTree
from dotenv import load_dotenv
import re

load_dotenv()

# Your Discord webhook URL
PYPI_WEBHOOK_URL = os.getenv("PYPI_WEBHOOK_URL")
DISCORD_ROLE_ID = os.getenv("DISCORD_ROLE_ID")
PYPI_RSS_FEED = "https://pypi.org/rss/project/maoto-agent/releases.xml"

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

def post_to_discord(version):
    """Send an advanced notification to Discord."""
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

        # Get the last notified version from the environment
        last_version = os.getenv("LATEST_VERSION")
        # print(f"Last version: {last_version}, Latest version: {latest_version}")

        # Post to Discord if the version is new
        if latest_version != last_version:
            print(f"New version detected: {latest_version}. Sending notification.")
            post_to_discord(latest_version)

            # Save the latest version to the GitHub environment
            with open(os.getenv("GITHUB_ENV"), "a") as env_file:
                env_file.write(f"LATEST_VERSION={latest_version}\n")
        # else:
            # print("No new version detected.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
