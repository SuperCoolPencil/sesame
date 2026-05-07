# sesame

a lightweight python script to automate the authentication process for the iiitg captive portal.

## usage

you can run the script directly using python:

```bash
python main.py <username> <password>
```

alternatively, you can make the script executable and run it like a standard command:

```bash
chmod +x main.py
./main.py <username> <password>
```

## features

- automates login to the iiitg captive portal endpoint (`https://secure.iiitg.ac.in:8090/`).
- seamlessly handles the portal's xml responses to provide accurate connection status.
- built with standard python libraries (no `pip install` required).
- minimalist terminal output.
