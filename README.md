# Damn Simple Vulnerable Python Web Application

### Running a OWASP Dependency Check (SCA) Scan
Ensure that you have Docker installed.
Then run:
```bash
sh ./scripts/dependencycheck.sh
```

### Running a OWASP ZAProxy (DAST) Scan
Ensure that you have Docker installed.
Then run:
```bash
sh ./scripts/zap.sh
```

### Running SonarScanner
```bash
sh ./scripts/scanner.sh
```

## Usage

### Standalone

You can simply run the standalone application with:

    > python dsvpwa.py

### Docker

You can build and run the application with an interactive shell (`-it`) in a container that is automatically removed (`--rm`) and bind the container's default port to the host (`-p`):

    > docker build -t dsvpwa .
    > docker run --rm -it -p 127.0.0.1:65413:65413 dsvpwa

Note that ports which are not bound to the host (i.e., `-p 65413:65413` instead of `-p 127.0.0.1:65413:65413`) will be accessible from the outside.
