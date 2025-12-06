import requests
import os
import json

STATUS_URL = "https://kvn3s3cpcdk4fl6j-c.uvwx.xyz:8443/2222/status"
STATUS_FILE = "raw_status.json"

raw_status = None
raw_servers = None

def fetch_status():
    try:
        response = requests.get(STATUS_URL, stream=True)
        response.raise_for_status()

        with open(STATUS_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Fetched server status from arras.io successfully")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading status: {e}")



def load_status():
    global raw_status
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            raw_status = json.load(f)

def get_servers():
    global raw_servers
    if raw_status:
        raw_servers = raw_status["status"]

def print_servers():
    pretty_json = json.dumps(raw_servers, indent=4)
    print(pretty_json)

fetch_status()
load_status()
get_servers()
print_servers()