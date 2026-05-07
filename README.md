# sesame

a lightweight python script to automate the authentication process for the iiitg captive portal.

## usage

you can run the script directly with username and password:

```bash
python main.py <username> <password>
```

### profiles

save your credentials with a name to login faster:

```bash
python main.py add <name> <username> <password>
```

then just use the name or number to login:

```bash
python main.py meet
# or
python main.py 1
```

list all saved profiles:

```bash
python main.py list
```

## features

- automates login to the iiitg captive portal endpoint (`https://secure.iiitg.ac.in:8090/`).
- handles named profiles for quick access.
- seamlessly handles the portal's xml responses.
- built with standard python libraries.
- minimalist terminal output.
