# YPIM (Your Password Is Mine)

<img width="635" height="368" alt="image" src="https://github.com/user-attachments/assets/1fdc3e86-c2eb-4c51-93e2-0c6f80b07a2e" />

YPIM is a simple command-line tool designed to query the official [BreachDirectory API](https://breachdirectory.org/). It retrieves censored passwords and SHA-1 hashes associated with compromised email addresses, allowing you to view the data quickly in your terminal without dealing with website captchas.

⚠️ **IMPORTANT: API Key Required** 
You cannot use this script without an API key. You must register on RapidAPI and subscribe to the [BreachDirectory API](https://rapidapi.com/rohan-patra/api/breachdirectory) to get your personal key.

## Dependencies

The script requires Python 3. It uses the `requests` library to handle API calls, and optionally uses `rich` to display beautiful tables and terminal output.

Install the required dependencies using pip:

```bash
pip install requests rich
```
*(Note: If `rich` is not installed, the script will still work using standard text output).*

## Setup & Configuration

Before querying an email, the script needs your RapidAPI key. You have three ways to provide it:

**1. Save it permanently (Recommended)**
You can save your API key so you don't have to type it every time. It will be stored securely in `~/.config/ypim/api_key.txt`.
```bash
python ypim.py --save-key YOUR_RAPIDAPI_KEY
```

**2. Pass it directly**
```bash
python ypim.py email@example.com --api-key YOUR_RAPIDAPI_KEY
```

**3. Use an environment variable**
```bash
export BD_API_KEY="YOUR_RAPIDAPI_KEY"
python ypim.py email@example.com
```

## Usage Examples

Once your API key is configured, you can simply run:

```bash
# Basic query
python ypim.py email@example.com

# Query an email and save the results to a text file
python ypim.py email@example.com -o results.txt

# Run the script without the ASCII art banner
python ypim.py email@example.com --no-banner
```

<img width="989" height="788" alt="image" src="https://github.com/user-attachments/assets/0b1b8996-eed0-4884-8048-34fac9fca535" />

## Help

To see all available options at any time, run:

```bash
python ypim.py -h
```

---
Made by [@D4vKry](https://d4vkry.github.io)
