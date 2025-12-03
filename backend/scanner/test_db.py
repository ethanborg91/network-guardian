import os
from scanner import db

DB_PATH = os.path.join(os.path.dirname(__file__), "test_devices.db")

# Remove test DB if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("Initializing DB...")
db.init_db(DB_PATH)
print("Inserting device...")
db.insert_or_update_device(DB_PATH, ip="192.168.68.23", mac="AA:BB:CC:11:22:33", vendor="TestVendor")
print("Devices now:")
devices = db.get_all_devices(DB_PATH)
for d in devices:
    print(d)
print("Logging a scan entry...")
db.log_scan(DB_PATH, duration_seconds=1.2, scanned_count=1)
print("Creating an alert...")
db.create_alert(DB_PATH, alert_type="NEW_DEVICE", mac="AA:BB:CC:11:22:33", note="Test new device")
print("Alerts:")
print(db.get_alerts(DB_PATH))
print("Test complete.")
