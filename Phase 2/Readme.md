## Phase 2 — Basic connectivity scanning

  *  Implement a function to check whether an IP is online (e.g., via a ping or socket attempt).
  *  Limit checks to a predefined set of common ports or user-specified ports.
  *  Handle timeouts gracefully to avoid long delays.

**Functional result**: program identifies which IPs are online and which ports respond, without crashing on unreachable hosts.