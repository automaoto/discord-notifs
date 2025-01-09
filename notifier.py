import requests
import time
import os
from xml.etree import ElementTree
from dotenv import load_dotenv
load_dotenv()

# Your Discord webhook URL
PYPI_WEBHOOK_URL = os.getenv("PYPI_WEBHOOK_URL")

# PyPI RSS feed URL for the package
PYPI_RSS_FEED = "https://pypi.org/rss/project/maoto-agent/releases.xml"

# Track the latest version
latest_version = None


def get_latest_version():
    """Fetch the latest version of the package from the PyPI RSS feed."""
    response = requests.get(PYPI_RSS_FEED)
    response.raise_for_status()
    tree = ElementTree.fromstring(response.content)
    # Parse the first entry
    latest_entry = tree.find(".//item/title").text
    return latest_entry.split()[-1]  # Extract version (e.g., "1.0.5")


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
        "content": "🎉 A new release is live! @everyone",
        "embeds": [embed],
    }

    response = requests.post(PYPI_WEBHOOK_URL, json=message)
    response.raise_for_status()


def main():
    try:
        global latest_version
        current_version = get_latest_version()
        if current_version != latest_version:
            latest_version = current_version
            post_to_discord(latest_version)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
