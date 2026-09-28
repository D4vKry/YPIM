#!/usr/bin/env python3
"""
YPIM (Your Password Is Mine) - Console client to query the BreachDirectory API
Made by @D4vKry - https://d4vkry.github.io
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] Missing 'requests' module. Install it with: pip install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ---
# Configuration
# ---

API_HOST = "breachdirectory.p.rapidapi.com"
API_URL = f"https://{API_HOST}/"
CONFIG_FILE = Path.home() / ".config" / "ypim" / "api_key.txt"

ASCII_ART = r"""
      ,  ,  , , ,
     <(__)> | | |
     | \/ | \_|_/
     \^  ^/   |
     /\--/\  /|
    /  \/  \/ |

"""
# ASCII art: https://www.asciiart.eu/art/f4ff9994556ecc15
TOOL_NAME = "YPIM - Your Password Is Mine"
AUTHOR_LINE = "Made by @D4vKry"
WEBSITE_LINE = "Website: https://d4vkry.github.io"

console = Console() if RICH_AVAILABLE else None


# ---
# Presentation utilities
# ---

def print_banner():
    if RICH_AVAILABLE:
        console.print(f"[bold bright_green]{ASCII_ART}[/bold bright_green]")
        console.print(f"[bold white]{TOOL_NAME}[/bold white]")
        console.print(f"[dim]{AUTHOR_LINE}[/dim]")
        console.print(f"[dim]{WEBSITE_LINE}[/dim]")
        console.print()
    else:
        print(ASCII_ART)
        print(TOOL_NAME)
        print(AUTHOR_LINE)
        print(WEBSITE_LINE)
        print()


def info(msg):
    if RICH_AVAILABLE:
        console.print(f"[cyan][*][/cyan] {msg}")
    else:
        print(f"[*] {msg}")


def error(msg):
    if RICH_AVAILABLE:
        console.print(f"[bold red][!][/bold red] {msg}")
    else:
        print(f"[!] {msg}")


def success(msg):
    if RICH_AVAILABLE:
        console.print(f"[bold green][+][/bold green] {msg}")
    else:
        print(f"[+] {msg}")


# ---
# API key management
# ---

def load_api_key(cli_key: str | None) -> str:
    """
    Priority: --api-key > BD_API_KEY environment variable > config file
    """
    if cli_key:
        return cli_key.strip()

    env_key = os.environ.get("BD_API_KEY")
    if env_key:
        return env_key.strip()

    if CONFIG_FILE.exists():
        key = CONFIG_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key

    error("API key not found.")
    print(
        "\nOptions to configure it:\n"
        f"  1) Save it in {CONFIG_FILE}\n"
        "  2) Export it as an environment variable: export BD_API_KEY='your_key'\n"
        "  3) Pass it directly: python ypim.py email@example.com --api-key YOUR_KEY\n"
    )
    sys.exit(1)


def save_api_key(key: str):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(key.strip(), encoding="utf-8")
    CONFIG_FILE.chmod(0o600)
    success(f"API key saved to {CONFIG_FILE}")


# ---
# API Query
# ---

def query_breachdirectory(email: str, api_key: str) -> dict:
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {"func": "auto", "term": email}

    try:
        resp = requests.get(API_URL, headers=headers, params=params, timeout=20)
    except requests.RequestException as e:
        error(f"Connection error: {e}")
        sys.exit(1)

    if resp.status_code == 403:
        error("Invalid API key or lacking permissions (403).")
        sys.exit(1)
    if resp.status_code == 429:
        error("Rate limit reached (429). Try again later.")
        sys.exit(1)
    if resp.status_code != 200:
        error(f"API responded with status code {resp.status_code}: {resp.text[:200]}")
        sys.exit(1)

    try:
        return resp.json()
    except json.JSONDecodeError:
        error("Could not parse JSON response from the API.")
        sys.exit(1)


# ---
# Results presentation
# ---

def show_results(email: str, data: dict, save_path: str | None):
    entries = data.get("result") or []
    found = data.get("found", len(entries))

    if not entries:
        info(f"No breaches found for: {email}")
        return

    success(f"Found {found} result(s) for: {email}\n")

    rows = []
    for entry in entries:
        password = entry.get("password") or "-"
        sha1 = entry.get("sha1") or "-"
        rows.append((password, sha1))

    if RICH_AVAILABLE:
        table = Table(show_lines=True)
        table.add_column("Password (censored)", style="yellow")
        table.add_column("SHA-1", style="magenta", overflow="fold")
        for pw, sha1 in rows:
            table.add_row(pw, sha1)
        console.print(table)
    else:
        for i, (pw, sha1) in enumerate(rows, 1):
            print(f"\n#{i}")
            print(f"  Password : {pw}")
            print(f"  SHA-1    : {sha1}")

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"Results for: {email}\n")
            f.write(f"Total found: {found}\n\n")
            for i, (pw, sha1) in enumerate(rows, 1):
                f.write(f"[{i}] Password: {pw} | SHA-1: {sha1}\n")
        success(f"Results saved to: {save_path}")


# ---
# Main
# ---

def main():
    parser = argparse.ArgumentParser(
        description="YPIM (Your Password Is Mine) - Query BreachDirectory (official API) from the terminal."
    )
    parser.add_argument("email", nargs="?", help="Email address to query")
    parser.add_argument("--api-key", help="BreachDirectory (RapidAPI) API key")
    parser.add_argument("--save-key", metavar="KEY", help="Save the API key for future use")
    parser.add_argument("-o", "--output", metavar="FILE", help="Save results to a .txt file")
    parser.add_argument("--no-banner", action="store_true", help="Do not show the ASCII banner")

    args = parser.parse_args()

    if not args.no_banner:
        print_banner()

    if args.save_key:
        save_api_key(args.save_key)
        if not args.email:
            return

    if not args.email:
        parser.print_usage()
        error("You must specify an email address. Example: python ypim.py email@example.com")
        sys.exit(1)

    api_key = load_api_key(args.api_key)

    info(f"Querying: {args.email} ...")
    data = query_breachdirectory(args.email, api_key)
    show_results(args.email, data, args.output)


if __name__ == "__main__":
    main()
