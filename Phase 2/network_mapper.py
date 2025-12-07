import socket
import concurrent.futures

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
        
        if '-' in part:
            try:
                start, end = part.split('-')
                start, end = int(start), int(end)
                if start > end: start, end = end, start
                for p in range(start, end + 1):
                    if 0 < p <= 65535:
                        ports.add(p)
            except ValueError:
                print(f"Warning: Invalid range format '{part}' ignored.")
        
        else:
            try:
                p = int(part)
                if 0 < p <= 65535:
                    ports.add(p)
            except ValueError:
                print(f"Warning: Invalid port '{part}' ignored.")
    
    return sorted(list(ports))

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        result = sock.connect_ex((ip, port))
        
        service = COMMON_PORTS.get(port, "Unknown")

        if result == 0:
            print(f"[OPEN] {ip}:{port}({service})")
        
        elif result == 11 or result == 10035:
            print(f"[TIMEOUT] {ip}:{port}({service}) (Firewalled?)")
        elif result == 111 or result == 10061:
            print(f"[CLOSED] {ip}:{port}({service}) (Host is up, but port is closed)")
        else:
            print(f"[ERR {result}] {ip}:{port}({service})")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] {ip}:{port}({service}) - {e}")
    finally:
        sock.close()

def scan_network(start_int, end_int, ports):
    print(f"\nStarting Scan with {THREAD_COUNT} threads...")
    print(f"Checking {len(COMMON_PORTS)} ports per IP...")
    print()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        future_to_ip = {}
        
        for ip_str in ip_iterator(start_int, end_int):
            for port in ports:
                future = executor.submit(check_port, ip_str, port)
                future_to_ip[future] = f"{ip_str}:{port}"
        
        for future in concurrent.futures.as_completed(future_to_ip):
            try:
                future.result()
            except Exception as exc:
                print(f"Thread generated an exception: {exc}")
    print("Scan complete")

try:
    cidr = input("Enter CIDR: ")
    print("Processing...")
    start, end = validate(cidr)
    total = end - start + 1
    print(f"CIDR validated. Subnet range: {int_to_ip(start)} to {int_to_ip(end)}")
    print(f"Number of IPs: {total}")
    
    print("\nEnter Ports to scan.(optional)")
    print("Examples: '80' OR '22, 443' OR '8000-8010'")
    port_input = input("Ports: ")
    user_ports = parse_ports(port_input)
    
    if not user_ports:
        print("\nNo user ports selected. Using standard ports.")
        scan_network(start,end,COMMON_PORTS)
    else:
        print(f"\nTarget ports: {user_ports}")
        scan_network(start,end,user_ports)
except ValueError as e:
    print(f"Error: {e}")
except ValueError as e:
        print(f"Error: {e}")
except KeyboardInterrupt:
        print("\n\nScan stopped by user.")