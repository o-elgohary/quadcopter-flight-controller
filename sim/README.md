# Quadcopter Flight Controller - Simulation (Phase 3)

A minimal single-axis attitude simulation: a PD controller recovering a
quadcopter from an initial tilt. Simplified on purpose, see "Why simplified"
below. Every physical constant traces back to `../spec.md`.

## Files

| File | Role |
|---|---|
| `quad_sim.py` | Everything: constants, the PD control loop, and the plot. |

Run it from this `sim/` directory:

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python quad_sim.py
```

Writes `exports/recovery.png` (tilt angle vs. time, with the settling point
marked).

An animated version (drone icon banking back to level) was attempted but
dropped. matplotlib's GIF-writing path (`animation.PillowWriter`, a manual
canvas-buffer grab, and a `savefig`-per-frame plus Pillow `save_all` combine)
all silently produced a GIF where every frame showed the same final state,
in this specific environment. Root cause wasn't nailed down after several
different fixes, so the static plot below reliably shows the same result
without depending on that broken path.

## Results

Recovering from a 20 deg initial tilt, PD control settles within a 2 deg band
at **t = 0.13 s**.

Gains (in `quad_sim.py`): `KP = 0.5`, `KD = 0.035`. No integral term, since
this model is deliberately simple enough that a small P+D loop is enough to
show the point, and skipping I avoids windup entirely rather than adding an
anti-windup clamp for a demo this small.

## Why simplified

An earlier version of this modeled full 6-DOF coupled dynamics across 8 files
(quaternion attitude, IMU sensor noise, a complementary filter, cascaded
dual-rate PID, a 3D video render), around 700 lines. That was cut down to
this single ~110-line file on purpose. It keeps the same core idea (a
tilted quad correcting itself via feedback control) without machinery that
made the project harder to explain than it needed to be for its scope.

## What's estimated vs. from spec.md

From `spec.md` directly: mass (0.650 kg), arm length (0.125 m, half the
250 mm diagonal), control loop rate (500 Hz).

Estimated here (not in spec.md, no CAD to measure from): the per-axis
rotational inertia, modeled as just the 4 motors (30 g each) as point masses
at the arm tips, 45 deg off-axis in the X layout: `I = 4 * m_motor *
(ARM * sin(45°))^2`. This ignores the central body's own inertia contribution,
which is a real simplification, not an oversight. It keeps the number easy
to derive and explain, at the cost of being a slight underestimate. The PD
gains were tuned against this specific number, so if the inertia estimate is
refined later, the gains would need retuning too.
