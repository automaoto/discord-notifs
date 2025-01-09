import requests
import os
from xml.etree import ElementTree
from dotenv import load_dotenv
import re

load_dotenv()

# Your Discord webhook URL
PYPI_WEBHOOK_URL = os.getenv("PYPI_WEBHOOK_URL")

# PyPI RSS feed URL for the package
PYPI_RSS_FEED = "https://pypi.org/rss/project/maoto-agent/releases.xml"

# File to store the last notified version
LATEST_VERSION_FILE = "latest_version.txt"


def is_stable_version(version):
    """
    Check if a version is a stable release.
    Stable versions do not contain pre-release identifiers like 'a', 'b', 'rc', etc.
    """
    # Regex to exclude pre-releases (e.g., 1.0.5-alpha, 1.0.5-beta, 1.0.5rc1)
    return not re.search(r"(a|b|rc|alpha|beta|dev|pre)", version, re.IGNORECASE)


def get_latest_version():
    """
    Fetch the latest stable version of the package from the PyPI RSS feed.
    """
    response = requests.get(PYPI_RSS_FEED)
    response.raise_for_status()
    tree = ElementTree.fromstring(response.content)
    
    # Extract all versions from the RSS feed
    versions = []
    for item in tree.findall(".//item"):
        title = item.find("title").text
        version = title.split()[-1]  # Extract version (e.g., "1.0.5")
        if is_stable_version(version):
            versions.append(version)
    
    if versions:
        # Sort versions and return the latest (stable)
        return sorted(versions, key=lambda v: list(map(int, v.split("."))), reverse=True)[0]
    return None  # Return None if no stable version is found


def read_last_version():
    """Read the last notified version from the file."""
    if os.path.exists(LATEST_VERSION_FILE):
        with open(LATEST_VERSION_FILE, "r") as f:
            return f.read().strip()
    return None


def write_last_version(version):
    """Write the last notified version to the file."""
    with open(LATEST_VERSION_FILE, "w") as f:
        f.write(version)


def post_to_discord(version):
    """Send an advanced notification to Discord."""
    embed = {
        "title": f"🚀 New Release: maoto-agent v{version}",
        "description": (
            f"The `maoto-agent` package has just been updated to version `{version}`!\n\n"
            "📥 **[Download Now](https://pypi.org/project/maoto-agent/{version}/)**\n"
        ),
        "color": 16777215,  # White
        "fields": [
            {"name": "What's New?", "value": "• Bug fixes\n• Performance improvements\n• New features", "inline": False},
            {"name": "Changelog", "value": f"[View Release Notes](https://pypi.org/project/maoto-agent/{version}/#history)", "inline": False},
        ],
        "footer": {"text": "Powered by Maoto", "icon_url": "https://example.com/footer-icon.png"},
    }

    message = {
        "content": "🎉 A new release is live! @here",
        "embeds": [embed],
    }

    response = requests.post(PYPI_WEBHOOK_URL, json=message)
    response.raise_for_status()


def main():
    try:
        current_version = get_latest_version()
        last_version = read_last_version()

        if current_version and current_version != last_version:
            # Post to Discord and update the last version file
            post_to_discord(current_version)
            write_last_version(current_version)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
