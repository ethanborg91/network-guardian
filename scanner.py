import sqlite3
import time
from scapy.all import ARP, Ether, srp  # For ARP scanning

SUBNET = "192.168.68.0/22" 
SCAN_INTERVAL = 30  # Seconds

# DB setup
conn = sqlite3.connect('devices.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS devices 
             (mac TEXT PRIMARY KEY, ip TEXT, vendor TEXT, first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
              last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_new INTEGER DEFAULT 1)''')
conn.commit()

def get_vendor(mac):
    # Simple OUI lookup (expand with a dict or API later)
    oui = mac[:8].upper()
    vendors = {"00:1B:63": "Apple", "00:0C:29": "VMware", "B8:27:EB": "Raspberry Pi"}  # Add yours
    return vendors.get(oui, "Unknown")

def scan_network():
    print(f"Scanning {SUBNET}...")
    answered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=SUBNET), timeout=2, verbose=0)[0]
    
    devices = []
    for sent, received in answered:
        mac = received.hwsrc
        ip = received.psrc
        vendor = get_vendor(mac)
        
        # Log/update DB
        c.execute("SELECT mac FROM devices WHERE mac=?", (mac,))
        if not c.fetchone():
            c.execute("INSERT INTO devices (mac, ip, vendor) VALUES (?, ?, ?)", (mac, ip, vendor))
            print(f"New device: {ip} ({mac}) - {vendor}")
            # TODO: Trigger alert here (e.g., Slack webhook)
        else:
            c.execute("UPDATE devices SET ip=?, vendor=?, last_seen=CURRENT_TIMESTAMP, is_new=0 WHERE mac=?", (ip, vendor, mac))
        
        devices.append({"ip": ip, "mac": mac, "vendor": vendor})
    
    conn.commit()
    print(devices)
    return devices

# Run loop (for testing; daemonize later)
if __name__ == "__main__":
    while True:
        scan_network()
        time.sleep(SCAN_INTERVAL)