import serial
import os
from datetime import datetime

PORT = "COM11"
BAUD = 115200
END_MARKER = "End of Data."

OUT_DIR = r"C:\Users\brand\Downloads\Mechatronics\Lab\Lab_0x04"
os.makedirs(OUT_DIR, exist_ok=True)

fname = f"data.csv"
out_path = os.path.join(OUT_DIR, fname)

header = "t_left_us,val_left,t_right_us,val_right\n"

with serial.Serial(PORT, BAUD, timeout=1) as ser, open(out_path, "w", newline="") as f:
    f.write(header)
    print(f"[INFO] Listening on {PORT} @ {BAUD}...")
    print(f"[INFO] Writing to: {out_path}")

    while True:
        raw = ser.readline()
        if not raw:
            continue

        line = raw.decode("utf-8", "ignore").strip()
        if not line:
            continue

        # optional: show live in terminal
        print(line)

        if END_MARKER in line:
            break

        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 4:
            f.write(line + "\n")

print("[DONE] Wrote:", out_path)