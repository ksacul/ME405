''' UI task using a generator run() method (required by cotask). '''

import micropython
from pyb import USB_VCP, UART
from pyb import repl_uart
from task_share import Share, Queue
import os
import time

repl_uart(None)

S0_INIT = micropython.const(0)
S1_CMD  = micropython.const(1)
S2_RETURN_KP = micropython.const(2)
S3_GET_KI = micropython.const(3)
S4_GET_SETPOINT = micropython.const(4)
S5_COLLECT = micropython.const(5)
S6_PRINT = micropython.const(6)

UI_prompt = ">: "

LOG_DIR = "Collection Log"
CSV_HEADER = "t_left_us,val_left,t_right_us,val_right\r\n"


class task_user:
    def __init__(self, leftMotorGo, rightMotorGo, K_p, K_i, setpoint,
                 dataValuesr, timeValuesr, dataValuesl, timeValuesl):

        self._state: int = S0_INIT

        self._leftMotorGo: Share  = leftMotorGo
        self._rightMotorGo: Share = rightMotorGo

        self._K_p: Share = K_p
        self._K_i: Share = K_i
        self._setpoint: Share = setpoint
        self._K_p.put(1.3)
        self._K_i.put(2.9)
        self._setpoint.put(0.2)

        # PuTTY / UI stream (USB)
        self._ser = USB_VCP()

        # UART2 stream (ST-Link VCP / COM port)
        self._ser_uart = UART(2, 115200)
        self._ser_uart.write("UART2 ready @115200\r\n")

        # Queues
        self._dataValues_r: Queue = dataValuesr
        self._timeValues_r: Queue = timeValuesr
        self._dataValues_l: Queue = dataValuesl
        self._timeValues_l: Queue = timeValuesl

        # Data rows to write to CSV at the end
        self._rows = []

        # Input processing
        self._char_buf = ""
        self._digits = set(map(str, range(10)))
        self._term = {"\r", "\n"}

    def _ensure_dir(self, path):
        try:
            os.mkdir(path)
        except OSError:
            pass

    def _write_csv_from_rows(self):
        """Write collected rows to a CSV file on the board."""
        self._ensure_dir(LOG_DIR)
        csv_path = "{}/log_{}.csv".format(LOG_DIR, time.ticks_ms())

        try:
            with open(csv_path, "w") as f:
                f.write(CSV_HEADER)
                for (t_l, v_l, t_r, v_r) in self._rows:
                    # keep numeric formatting similar to printed output
                    f.write("{:.1f},{:.6f},{:.1f},{:.6f}\n".format(t_l, v_l, t_r, v_r))

            msg = "Wrote CSV: {}\r\n".format(csv_path)
            self._ser.write(msg)
            self._ser_uart.write(msg)

        except Exception as e:
            msg = "CSV write FAILED: {}\r\n".format(e)
            self._ser.write(msg)
            self._ser_uart.write(msg)

    def _print_help(self):
        self._ser.write("\r\n+-------------------------------------------------------------+\r\n")
        self._ser.write("| ME 405 Romi Tuning Interface Help Menu                      |\r\n")
        self._ser.write("+---+---------------------------------------------------------+\r\n")
        self._ser.write("| h | Print help menu                                         |\r\n")
        self._ser.write("| k | Enter new gain values                                   |\r\n")
        self._ser.write("| s | Choose a new setpoint                                   |\r\n")
        self._ser.write("| g | Trigger step response and print results                 |\r\n")
        self._ser.write("+---+---------------------------------------------------------+\r\n\n")

    def _process_input(self):
        """Return float when user hits Enter; None while typing; False if cancelled/empty."""
        if self._ser.any():
            char_in = self._ser.read(1).decode()

            if char_in in self._digits:
                self._ser.write(char_in)
                self._char_buf += char_in

            elif char_in == "." and "." not in self._char_buf:
                self._ser.write(char_in)
                self._char_buf += char_in

            elif char_in == "-" and len(self._char_buf) == 0:
                self._ser.write(char_in)
                self._char_buf += char_in

            elif char_in == "\x7f":  # backspace
                if len(self._char_buf) > 0:
                    self._ser.write(char_in)
                    self._char_buf = self._char_buf[:-1]

            elif char_in in self._term:
                if len(self._char_buf) == 0:
                    self._ser.write("\r\nValue not changed.\r\n")
                    return False
                elif self._char_buf not in {"-", "."}:
                    try:
                        val = float(self._char_buf)
                        self._ser.write("\r\n>>>: {}\r\n".format(val))
                        self._char_buf = ""
                        return val
                    except ValueError:
                        self._ser.write("\r\nInvalid Number\r\n")
                        self._char_buf = ""
                        return False

        return None

    def run(self):
        """Generator-based state machine (cotask requires yield)."""
        while True:

            if self._state == S0_INIT:
                self._ser.write("UI Task Initialized.\r\n")
                self._print_help()
                self._ser.write(UI_prompt)
                self._state = S1_CMD

            elif self._state == S1_CMD:
                if self._ser.any():
                    char_in = self._ser.read(1).decode()

                    if char_in == 'h':
                        self._print_help()
                        self._ser.write(UI_prompt)

                    elif char_in == 'g':
                        self._ser.write("Triggering Step Response.\r\n")
                        # Clear any previous run data
                        self._rows = []
                        # Trigger BOTH motors
                        self._leftMotorGo.put(1)
                        self._rightMotorGo.put(1)
                        self._state = S5_COLLECT

                    elif char_in == 'k':
                        self._ser.write("Enter Proportional Gain Kp: ")
                        self._char_buf = ""
                        self._state = S2_RETURN_KP

                    elif char_in == 's':
                        self._ser.write("Enter Setpoint: ")
                        self._char_buf = ""
                        self._state = S4_GET_SETPOINT

                    elif char_in in {"\r", "\n"}:
                        self._ser.write("\r\n" + UI_prompt)

            elif self._state == S2_RETURN_KP:
                val = self._process_input()
                if val is not None:
                    if val is not False:
                        self._K_p.put(val)
                    self._ser.write("Kp set to {}\r\n\n".format(self._K_p.get()))
                    self._ser.write("Enter Integral Gain Ki: ")
                    self._state = S3_GET_KI

            elif self._state == S3_GET_KI:
                val = self._process_input()
                if val is not None:
                    if val is not False:
                        self._K_i.put(val)
                    self._ser.write("Ki set to {}\r\n\n".format(self._K_i.get()))
                    self._ser.write(UI_prompt)
                    self._state = S1_CMD

            elif self._state == S4_GET_SETPOINT:
                val = self._process_input()
                if val is not None:
                    if val is not False:
                        self._setpoint.put(val)
                    self._ser.write("Setpoint set to {}\r\n\n".format(self._setpoint.get()))
                    self._ser.write(UI_prompt)
                    self._state = S1_CMD

            elif self._state == S5_COLLECT:
                # Wait for BOTH motor tasks to finish (flags go to 0)
                if (not self._leftMotorGo.get()) and (not self._rightMotorGo.get()):
                    self._ser.write("Collection complete. Printing Data.\r\n")
                    # send header over UART2 too (optional but nice)
                    self._ser_uart.write("TimeL,ValL,TimeR,ValR\r\n")
                    self._state = S6_PRINT

            elif self._state == S6_PRINT:
                # only pop when BOTH queues have data
                if self._dataValues_l.any() and self._dataValues_r.any():
                    t_l = self._timeValues_l.get()
                    v_l = self._dataValues_l.get()
                    t_r = self._timeValues_r.get()
                    v_r = self._dataValues_r.get()

                    # Save row for CSV
                    self._rows.append((t_l, v_l, t_r, v_r))

                    # Print row to PuTTY + UART2
                    line = "{:.1f},{:.6f},{:.1f},{:.6f}\r\n".format(t_l, v_l, t_r, v_r)
                    self._ser.write(line)
                    self._ser_uart.write(line)

                else:
                    # No more data: finish
                    self._ser.write("End of Data.\r\n" + UI_prompt)
                    self._ser_uart.write("End of Data.\r\n")

                    # Write CSV from collected rows (no UART reading)
                    self._write_csv_from_rows()

                    self._state = S1_CMD

            yield self._state