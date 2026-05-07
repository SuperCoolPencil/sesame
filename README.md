# sesame

a lightweight python script to automate the authentication process for the iiitg captive portal.

## installation

you can install `sesame` globally using `uv` to use it from anywhere in your terminal. just run the `init` command from the repository root:

```bash
uv run main.py init
```

once installed, you can use the `sesame` command instead of `python main.py`.

## usage

you can run the script directly with username and password:

```bash
sesame <username> <password>
```

### profiles

save your credentials with a name to login faster:

```bash
sesame add <name> <username> <password>
```

then just use the name or number to login:

```bash
sesame meet
# or
sesame 1
```

list all saved profiles:

```bash
sesame list
```

## features

- automates login to the iiitg captive portal endpoint (`https://secure.iiitg.ac.in:8090/`).
- handles named profiles for quick access.
- seamlessly handles the portal's xml responses.
- built with standard python libraries.
- minimalist terminal output.
- os-agnostic global installation via `uv`.
