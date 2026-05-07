#!/usr/bin/env python3
import urllib.request
import urllib.parse
import ssl
import sys
import time

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
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        sys.exit(1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Attempting to authenticate user '{username}'...")
    login(username, password)
