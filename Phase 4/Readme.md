## Phase 4 — Robustness & polish

  *  Handle invalid inputs (bad CIDR, invalid port numbers).
  *  Implement basic exception handling for network errors.
  *  Ensure program exits cleanly if interrupted.
  *  Allow sorting of output by IP or by port, for clarity.
  *  Make the CLI easy to interact with and visually pleasant, using coloured text output.
  *  Allow saving the identified IP:port pairs to a `.txt` file.

  * Correct usage: `network_mapper.py CIDR [-o|--output output_file] [-s|--sort PORT/IP] [port1, port2, ...]`

**Functional result**: program is stable, handles edge cases gracefully, and consistently produces correct results for valid inputs.