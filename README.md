# Quadcopter Flight Controller

A 250mm-class quad flight controller, designed across three connected pieces: a custom PCB, a 3D-printed frame, and a control-systems simulation. None of this has been physically built or flown. It's a design and simulation project, stated plainly rather than implied otherwise.

## The integration story

The point of this project isn't any single piece, it's that each piece drove a real decision in another:

- **The simulation's control-loop speed requirement decided a wiring choice on the PCB.** The rate loop runs at 500Hz, which means the IMU needs to report data faster than 1kHz to keep up. That's why the ICM-42688-P is wired on SPI1 instead of I2C in the schematic, since I2C can't reliably keep pace with a loop that fast once you account for register-read overhead.
- **The PCB's real mounting-hole positions drove the CAD frame's geometry.** The board's STEP export (`pcb/exports/board.step`, once routing is finished) gets imported directly into the Fusion 360 frame model, and the center plate's mounting pattern is dimensioned straight off it, not measured by eye.
- **Every number in every phase traces back to one file, `spec.md`**, so a change to (say) the battery or frame size ripples outward instead of getting silently re-typed as a new assumption somewhere else.

## Repo layout

```
spec.md         master numbers every other file pulls from
pcb/            KiCad schematic + layout
cad/            exported Fusion 360 frame STEP
sim/            Python attitude-recovery simulation
```

## Status

| Phase | State |
|---|---|
| Spec (`spec.md`) | Done. Frame/motor/battery/IMU/MCU choices are real parts for this class of build; motor thrust/torque constants (kT, kQ) are documented estimates anchored to real bench-test data, not measured on this exact hardware. |
| PCB (`pcb/`) | Schematic done, ERC clean (0 errors, 2 benign warnings). Board outline, mounting holes, and component placement are done. Copper routing is not finished, so real DRC violations remain from auto-placement, left as the next real routing pass rather than papered over. |
| Frame (`cad/`) | Modeled in Fusion 360: center plate with the PCB's mounting pattern, 4 arms sized to the 250mm diagonal, motor mounts, battery deck. Exported to `cad/exports/frame_assembly.step`. Prop clearance checked analytically (adjacent motors clear by about 50mm at the prop tips). |
| Simulation (`sim/`) | A single-axis PD controller recovering a 20° tilt, settling in 0.13s. Deliberately simplified from an earlier, much larger 6-DOF version, see `sim/README.md` for why. Produces a plot (`sim/exports/recovery.png`). |
