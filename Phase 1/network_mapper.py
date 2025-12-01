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

try:
    cidr = input("Enter CIDR: ")
    print("Processing...")
    start, end = validate(cidr)
    print(f"CIDR validated. Subnet range: {int_to_ip(start)} to {int_to_ip(end)}")
    ip_subnet=tuple(ip_iterator(start,end))
    for ip in ip_subnet:
        print(ip)
except ValueError as e:
    print(f"Error: {e}")