"""
Minimal quad attitude simulation.

Deliberately simplified from a full 6-DOF coupled model: each rotation axis
(roll, pitch, yaw) is treated independently with its own PID controller. That's
not physically complete (real axes interact a bit), but it's enough to show
the thing that actually matters for this project: the flight-control loop can
recover from a tilt fast, and that speed requirement is why the IMU on the PCB
is wired on SPI instead of I2C (see spec.md).

Numbers used here (mass, arm length, control loop rate) come from spec.md.
Everything else (PID gains, inertia estimate) is worked out below.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- from spec.md ---
MASS = 0.650                       # kg, all-up weight
ARM = 0.125                        # m, center-to-motor distance (250mm diagonal / 2)
LOOP_HZ = 500                      # control loop rate
DT = 1.0 / LOOP_HZ

# Rough per-axis inertia: 4 motors (~30g each incl. prop) at the arm tips,
# 45 degrees off-axis in the X layout, spinning around roll or pitch.
MOTOR_MASS = 0.030                 # kg
I_AXIS = 4 * MOTOR_MASS * (ARM * np.sin(np.radians(45))) ** 2   # kg*m^2

# PD gains (no integral term -- keeps this simple model numerically stable
# and avoids windup; a real firmware PID would add a small I term, see
# spec.md's controller notes). Chosen so the torque at a 20 deg error is a
# realistic fraction of a newton-meter for this size of quad.
KP, KD = 0.5, 0.035


def simulate(initial_tilt_deg, t_end=1.0):
    """Recover a single axis from initial_tilt_deg back to 0, PD control +
    simple Euler integration (torque -> angular accel -> rate -> angle)."""
    n = int(t_end / DT)
    theta = np.radians(initial_tilt_deg)
    rate = 0.0
    t_log = np.zeros(n)
    theta_log = np.zeros(n)

    for i in range(n):
        error = -theta
        torque = KP * error - KD * rate
        rate += (torque / I_AXIS) * DT
        theta += rate * DT
        t_log[i] = i * DT
        theta_log[i] = np.degrees(theta)

    return t_log, theta_log


def settling_time(t, theta, band_deg=2.0):
    outside = np.where(np.abs(theta) > band_deg)[0]
    return t[outside[-1]] if len(outside) else 0.0


def make_plot(t, theta, settle_t):
    plt.figure(figsize=(7, 4))
    plt.plot(t, theta)
    plt.axhline(0, color="gray", ls="--", lw=0.8)
    plt.axvline(settle_t, color="red", ls=":", lw=0.8, label=f"settled at {settle_t:.2f}s")
    plt.xlabel("time (s)")
    plt.ylabel("tilt angle (deg)")
    plt.title("Quad recovering from a 20 deg tilt (single-axis PID)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("exports/recovery.png", dpi=110)
    plt.close()


if __name__ == "__main__":
    t, theta = simulate(initial_tilt_deg=20.0)
    settle_t = settling_time(t, theta)
    print(f"Settled within 2 deg at t={settle_t:.2f}s")

    make_plot(t, theta, settle_t)
    print("saved exports/recovery.png")
