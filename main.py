#!/usr/bin/env python3
import urllib.request
import urllib.parse
import ssl
import sys
import time
import json
import os

import pathlib

# Store profiles in the user's config directory so they aren't lost when updating the tool
if sys.platform == "win32":
    CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "sesame")
elif sys.platform == "darwin":
    CONFIG_DIR = os.path.expanduser("~/Library/Application Support/sesame")
else:
    CONFIG_DIR = os.path.expanduser("~/.config/sesame")
PROFILES_FILE = os.path.join(CONFIG_DIR, "profiles.json")

def _ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_profiles(profiles):
    _ensure_config_dir()
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)
    os.chmod(PROFILES_FILE, 0o600)

def add_profile(name, username, password):
    profiles = load_profiles()
    # Check if profile with same name already exists
    if any(p.get('name') == name for p in profiles):
        print(f"error: profile '{name}' already exists.")
        sys.exit(1)
    profiles.append({'name': name, 'username': username, 'password': password})
    save_profiles(profiles)
    print(f"saved profile: {name}")

def list_profiles():
    profiles = load_profiles()
    if not profiles:
        print("no profiles saved. use 'add <name> <user> <pass>' to save one.")
        return
    print("saved profiles:")
    for i, p in enumerate(profiles, 1):
        name = p.get('name', f"profile {i}")
        print(f"{i}: {name} ({p['username']})")

def login(username, password):
    # Standard endpoint for Sophos/Cyberoam captive portal clients
    url = "https://secure.iiitg.ac.in:8090/login.xml"
    
    timestamp = str(int(time.time() * 1000))
    data = {
        'mode': '191',
        'username': username,
        'password': password,
        'a': timestamp,
        'producttype': '0'
    }
    
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    
    # Captive portals typically have self-signed certificates for their local IP/hostname
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, data=encoded_data, method='POST')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            resp_body = response.read().decode('utf-8', errors='ignore')
            
            # The portal responds with XML. We check for specific success/failure patterns.
            resp_lower = resp_body.lower()
            if 'login successful' in resp_lower or 'you are signed in as' in resp_lower or '<status><![cdata[live]]></status>' in resp_lower:
                print("sesame opened. you should be connected to the internet.")
                return True
            elif 'maximum login limit' in resp_lower:
                print("maximum login limit reached for this user.")
                return False
            elif 'could not be authenticated' in resp_lower or 'login failed' in resp_lower or '<status><![cdata[login]]></status>' in resp_lower:
                print("authentication failed. check your username and password.")
                return False
            else:
                # If we get here, it might still have worked but the response format was unexpected
                print("got a response, but couldn't verify if it succeeded. response:")
                print(resp_body.strip())
                return False
                
    except urllib.error.URLError as e:
        print(f"network error: could not reach the captive portal ({e.reason}).")
        print("make sure you are currently connected to the iiitg wi-fi network.")
        return False
    except Exception as e:
        print(f"unexpected error occurred: {e}")
        return False
def init_sesame():
    import subprocess
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(os.path.join(project_dir, "pyproject.toml")):
        print("error: 'sesame init' must be run from the source code directory.")
        print("it looks like sesame is already installed or running as a binary.")
        return

    print("installing sesame using uv...")
    try:
        subprocess.check_call(["uv", "tool", "install", "--force", "."], cwd=project_dir)
        print("successfully installed 'sesame'.")
        print("you can now use the 'sesame' command from anywhere.")
    except subprocess.CalledProcessError as e:
        print(f"failed to install sesame: {e}")
    except FileNotFoundError:
        print("uv not found. please ensure uv is installed and in your PATH.")

def open_config():
    if not os.path.exists(PROFILES_FILE):
        _ensure_config_dir()
        with open(PROFILES_FILE, 'w') as f:
            f.write("[]\n")
            
    if sys.platform == "win32":
        os.startfile(PROFILES_FILE)
        return

    import subprocess
    if sys.platform == "darwin":
        try:
            subprocess.call(["open", PROFILES_FILE])
        except Exception as e:
            print(f"failed to open config: {e}")
        return

    editor = os.environ.get('EDITOR', 'nano')
    try:
        subprocess.call([editor, PROFILES_FILE])
    except Exception as e:
        print(f"failed to open config: {e}")

def main():
    args = sys.argv[1:]
    
    if len(args) == 0:
        profiles = load_profiles()
        if not profiles:
            print("no profiles saved. use 'sesame add <name> <user> <pass>' to save one.")
            print("run 'sesame help' for usage.")
            sys.exit(1)
            
        for p in profiles:
            user = p['username']
            pw = p['password']
            name = p.get('name', "unknown")
            print(f"attempting profile: {name} ({user})")
            if login(user, pw):
                sys.exit(0)
        
        print("all profiles failed to connect.")
        sys.exit(1)

    if args[0] in ("help", "--help", "-h"):
        print(f"usage:")
        print(f"  sesame                             (auto-login using saved profiles)")
        print(f"  sesame <username> <password>       (direct login)")
        print(f"  sesame <name_or_number>            (use specific saved profile)")
        print(f"  sesame add <name> <user> <pass>    (save profile)")
        print(f"  sesame list                        (list profiles)")
        print(f"  sesame config                      (open config file)")
        print(f"  sesame init                        (install 'sesame' to PATH)")
        sys.exit(0)

    if args[0] == "init":
        init_sesame()
        sys.exit(0)

    if args[0] == "list":
        list_profiles()
        sys.exit(0)

    if args[0] == "config":
        open_config()
        sys.exit(0)

    if args[0] == "add":
        if len(args) != 4:
            print("usage: add <name> <username> <password>")
            sys.exit(1)
        add_profile(args[1], args[2], args[3])
        sys.exit(0)

    if len(args) == 2:
        username = args[0]
        password = args[1]
        print(f"attempting to authenticate user '{username}'...")
        login(username, password)
        sys.exit(0)

    if len(args) == 1:
        # Check if arg is a profile number or name
        profiles = load_profiles()
        target = args[0]
        
        selected_profile = None
        
        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(profiles):
                selected_profile = profiles[idx]
        else:
            for p in profiles:
                if p.get('name') == target:
                    selected_profile = p
                    break

        if selected_profile:
            user = selected_profile['username']
            pw = selected_profile['password']
            name = selected_profile.get('name', "unknown")
            print(f"using profile: {name} ({user})")
            login(user, pw)
            sys.exit(0)
        else:
            print(f"profile '{target}' not found. use 'list' to see available profiles.")
            sys.exit(1)

    print("invalid arguments. run without args for usage.")
    sys.exit(1)

if __name__ == "__main__":
    main()
