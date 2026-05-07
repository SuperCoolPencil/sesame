#!/usr/bin/env python3
import urllib.request
import urllib.parse
import ssl
import sys
import time
import json
import os

PROFILES_FILE = os.path.join(os.path.dirname(__file__), "profiles.json")

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

def add_profile(name, username, password):
    profiles = load_profiles()
    # Replace existing profile with same name if it exists
    profiles = [p for p in profiles if p.get('name') != name]
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
                print("Sesame opened! You should be connected to the internet.")
            elif 'maximum login limit' in resp_lower:
                print("Maximum login limit reached for this user.")
            elif 'could not be authenticated' in resp_lower or 'login failed' in resp_lower or '<status><![cdata[login]]></status>' in resp_lower:
                print("Authentication failed. Check your username and password.")
            else:
                # If we get here, it might still have worked but the response format was unexpected
                print("Got a response, but couldn't verify if it succeeded. Response:")
                print(resp_body.strip())
                
    except urllib.error.URLError as e:
        print(f"Network error: Could not reach the captive portal ({e.reason}).")
        print("Make sure you are currently connected to the IIITG Wi-Fi network.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0:
        print(f"usage:")
        print(f"  {sys.argv[0]} <username> <password>       (direct login)")
        print(f"  {sys.argv[0]} <name_or_number>            (use saved profile)")
        print(f"  {sys.argv[0]} add <name> <user> <pass>    (save profile)")
        print(f"  {sys.argv[0]} list                        (list profiles)")
        sys.exit(0)

    if args[0] == "list":
        list_profiles()
        sys.exit(0)

    if args[0] == "add":
        if len(args) != 4:
            print("usage: add <name> <username> <password>")
            sys.exit(1)
        add_profile(args[1], args[2], args[3])
        sys.exit(0)

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

    # Default to direct login if 2 args provided
    if len(args) == 2:
        username = args[0]
        password = args[1]
        print(f"attempting to authenticate user '{username}'...")
        login(username, password)
    elif not target.isdigit() or len(profiles) > 0:
        print(f"profile '{target}' not found. use 'list' to see available profiles.")
        sys.exit(1)
    else:
        print("invalid arguments. run without args for usage.")
        sys.exit(1)
