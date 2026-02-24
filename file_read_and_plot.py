from matplotlib import pyplot

pyplot.figure()

time_l, vel_l = [], []
time_r, vel_r = [], []

def not_a_float(x):
    try:
        float(x)
        return False
    except ValueError:
        return True

with open("data.csv", "r") as file:
    for idx, line in enumerate(file, start=1):
        if idx == 1:
            headers = [h.strip() for h in line.split(",")]
            if len(headers) >= 4:
                xL_name, yL_name, xR_name, yR_name = headers[:4]
            else:
                xL_name, yL_name = headers[:2]
                xR_name, yR_name = xL_name, yL_name
            continue

        if line.startswith("#") or line.strip() == "":
            continue

        line = line.split("#", 1)[0]
        parts = [p.strip() for p in line.split(",")]

        if len(parts) >= 4:
            if any(not_a_float(p) for p in parts[:4]):
                continue
            tL, yL, tR, yR = map(float, parts[:4])
            time_l.append(tL); vel_l.append(yL)
            time_r.append(tR); vel_r.append(yR)

        elif len(parts) == 2:
            if any(not_a_float(p) for p in parts[:2]):
                continue
            t, y = map(float, parts[:2])
            time_l.append(t); vel_l.append(y)

print("Displaying plot.")

pyplot.scatter(time_l, vel_l, marker='o', label="Left")
if len(time_r) > 0:
    pyplot.scatter(time_r, vel_r, marker='o', label="Right")

pyplot.title("Step Response (Left + Right)")
pyplot.xlabel("Time [s]")
pyplot.ylabel("Angular Velocity [rad/s]")
pyplot.grid()
pyplot.legend()
pyplot.show()
