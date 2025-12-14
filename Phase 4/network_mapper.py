import socket
import concurrent.futures
import sys
import os
import platform

THREAD_COUNT = 100
TIMEOUT = 0.5
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Proxy"
}

if platform.system() == "Windows":
    os.system('color')

USE_COLOR = sys.stdout.isatty()
class Colors:
    if USE_COLOR:
        RESET = "\033[0m"
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
    else:
        RESET = ""
        GREEN = ""
        RED = ""
        YELLOW = ""

def ip_to_int(ip_str):
    octets = ip_str.split('.')
    if len(octets) != 4:
        raise ValueError("IP must have exactly 4 octets.")
    
    ip_int = 0
    for octet in octets:
        if not octet.isdigit():
             raise ValueError(f"Octet '{octet}' is not a valid number.")
        val = int(octet)
        if not (0 <= val <= 255):
            raise ValueError(f"Octet {val} is out of range (0-255).")
        ip_int = (ip_int << 8) | val
    return ip_int

def int_to_ip(ip_int):
    return ".".join([
        str((ip_int >> 24) & 0xFF),
        str((ip_int >> 16) & 0xFF),
        str((ip_int >> 8) & 0xFF),
        str(ip_int & 0xFF)
    ])

def validate(address):
    if '/' not in address:
        raise ValueError("Invalid Format: Missing '/' separator.")

    ip, prefix = address.split('/')
    try:
        int_prefix = int(prefix)
    except ValueError:
        raise ValueError("Invalid Prefix: Must be an integer.") 
    if not (0 <= int_prefix <= 32):
        raise ValueError("Invalid Prefix: Must be between 0 and 32.")
    
    ip_int = ip_to_int(ip)

    if int_prefix == 0:
        mask = 0
    else:
        mask = (0xFFFFFFFF << (32 - int_prefix)) & 0xFFFFFFFF

    network_int = ip_int & mask
    broadcast_int = network_int | (~mask & 0xFFFFFFFF)

    return network_int, broadcast_int

def ip_iterator(start,end):
    for ip in range(start,end+1):
        yield int_to_ip(ip)

def parse_ports(input_str):
    ports = set()
    parts = input_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part: continue
        
        else:
            try:
                p = int(part)
                if 0 < p <= 65535:
                    ports.add(p)
            except ValueError:
                print(f"{Colors.YELLOW}[WW]{Colors.RESET}: Invalid port '{part}' ignored.")
    
    return sorted(list(ports))

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            service = COMMON_PORTS.get(port, "Unknown")
            return f"{ip}:{port} ({service})"
    except:
        pass
    finally:
        sock.close()
    return None

def scan_network_ip(start_int, end_int, ports, output_file=None):
    print(f"Sorting by {Colors.YELLOW}IP{Colors.RESET}...")
    print(f"Checking {Colors.YELLOW}{len(ports)}{Colors.RESET} ports per IP...")
    if output_file:
        print(f"Result will be saved to {Colors.YELLOW}{output_file}{Colors.RESET}")

    file_handle = None
    if output_file:
        try:
            file_handle = open(output_file, "w")
        except IOError as e:
            print(f"{Colors.RED}[ERR]{Colors.RESET} Error opening file: {e}")
            return

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = []
            for ip_str in ip_iterator(start_int, end_int):
                for port in ports:
                    futures.append(executor.submit(check_port, ip_str, port))
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                
                if result:
                    print(f"{Colors.GREEN}[OK]{Colors.RESET} {result}")
                    
                    if output_file:
                        file_handle.write(result + "\n")
                        file_handle.flush()
    finally:
        if output_file:
            file_handle.close()
    
    print(f"{Colors.GREEN}Scan complete{Colors.RESET}")

def scan_network_port(start_int, end_int, ports, output_file=None):
    print(f"Sorting by {Colors.YELLOW}PORT{Colors.RESET}...")
    print(f"Checking {Colors.YELLOW}{end_int - start_int + 1}{Colors.RESET} IPs per port...")
    if output_file:
        print(f"Result will be saved to {Colors.YELLOW}{output_file}{Colors.RESET}")

    file_handle = None
    if output_file:
        try:
            file_handle = open(output_file, "w")
        except IOError as e:
            print(f"{Colors.RED}[ERR]{Colors.RESET} Error opening file: {e}")
            return

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = []
            for port in ports:
                for ip_str in ip_iterator(start_int, end_int):
                    futures.append(executor.submit(check_port, ip_str, port))
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                
                if result:
                    print(f"{Colors.GREEN}[OK]{Colors.RESET} {result}")

                    if output_file:
                        file_handle.write(result + "\n")
                        file_handle.flush()
    finally:
        if output_file:
            file_handle.close()
    
    print(f"{Colors.GREEN}Scan complete{Colors.RESET}")

if __name__ == "__main__":

    args = sys.argv[1:]
    user_ports = []
    output = None
    clean_args = []
    sort_order = "IP"

    if len(args) < 1:
        print(f"{Colors.RED}[ERR]{Colors.RESET} Program called incorrectly!")
        print(f"Usage: network_mapper.py CIDR [-o|--output output_file] [-s|--sort PORT/IP] [port1, port2, ...]")
        sys.exit(1)

    i = 0
    while i < len(args):
        if args[i] == "--output" or args[i] == "-o":
            if i + 1 < len(args) and args[i+1].startswith("-") == False:
                output = args[i+1]
                i += 2
            else:
                print(f"{Colors.RED}[ERR]{Colors.RESET}: --output requires a filename")
                sys.exit(1)
        elif args[i] == "--sort" or args[i] == "-s":
            if i + 1 < len(args) and (args[i+1] == "PORT" or args[i+1] == "IP"):
                sort_order = args[i+1]
                i += 2
            else:
                print(f"{Colors.RED}[ERR]{Colors.RESET}: --sort requires a PORT/IP value")
                sys.exit(1)
        else:
            clean_args.append(args[i])
            i += 1

    try:
        cidr = args[0]
        start, end = validate(cidr)
        total = end - start + 1
        print(f"CIDR validated. Subnet range: {Colors.YELLOW}{int_to_ip(start)}{Colors.RESET} to {Colors.YELLOW}{int_to_ip(end)}{Colors.RESET}")
        print(f"Number of IPs: {Colors.YELLOW}{total}{Colors.RESET}")

        if len(clean_args) > 1:
            raw_ports = "".join(clean_args[1:])
            parsed = parse_ports(raw_ports)
            if parsed:
                user_ports = parsed
        
        if not user_ports:
            print("\nNo user ports selected. Using standard ports.")
            if sort_order == "IP":
                scan_network_ip(start,end,COMMON_PORTS,output)
            elif sort_order == "PORT":
                scan_network_port(start,end,COMMON_PORTS,output)
        else:
            print(f"\nTarget ports: {Colors.YELLOW}{user_ports}{Colors.RESET}")
            if sort_order == "IP":
                scan_network_ip(start,end,user_ports,output)
            elif sort_order == "PORT":
                scan_network_port(start,end,user_ports,output)

    except ValueError as e:
        print(f"{Colors.RED}[ERR]{Colors.RESET}: {e}")
    except KeyboardInterrupt:
            print("\n\nScan stopped by user.")