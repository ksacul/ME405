from pyb import UART
import os
import time

END_MARKER = "End of Data."
LOG_DIR = "Collection Log"

# Option A: Nucleo VCP is typically USART2
ser_uart = UART(2, 115200)

def ensure_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass

def flush_all(uart):
    while uart.any():
        uart.read()

def read_until_marker(uart):
    lines = []
    while True:
        raw = uart.readline()   # expects '\n' at end of each line
        if not raw:
            continue
        line = raw.decode("utf-8", "ignore").strip()
        if not line:
            continue

        lines.append(line)
        if END_MARKER in line:
            break
    return lines

def parse_data(lines):
    header = ["t_left_us", "val_left", "t_right_us", "val_right"]
    rows = []

    for line in lines:
        if END_MARKER in line:
            break

        # skip non-data lines (same intent as your PC script)
        if ("Time(" in line) or ("Setpoint" in line) or ("----" in line) or ("|   Time" in line):
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            continue

        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue

    return header, rows

def write_csv(path, header, rows):
    with open(path, "w") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write("{},{},{},{}\n".format(r[0], r[1], r[2], r[3]))

def main():
    ensure_dir(LOG_DIR)

    csv_path = "{}/log_{}.csv".format(LOG_DIR, time.ticks_ms())

    print("[INFO] Waiting for UART2 data at 115200...")
    flush_all(ser_uart)

    lines = read_until_marker(ser_uart)
    print("[INFO] Got {} lines. Parsing...".format(len(lines)))

    header, rows = parse_data(lines)
    if not rows:
        print("[ERROR] No numeric rows parsed. Check sender format + newline + end marker.")
        return

    write_csv(csv_path, header, rows)
    print("[DONE] Wrote:", csv_path)

if __name__ == "__main__":
    main()