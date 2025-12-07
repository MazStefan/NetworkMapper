## Phase 3 — Command-line interface & output formatting

  *  Accept input from command line: `network_mapper.py 192.168.0.0/24 [port1, port2, ...]`.
  *  Display results in a readable format, e.g.:
  ```
  192.168.0.1:80 (HTTP)
            :443 (HTTPS)
  192.168.0.105:445 (SMB)
  ```
  *  Map common ports to service names where possible.

**Functional result**: user runs the program and receives a clean, readable summary of online hosts and their open ports.