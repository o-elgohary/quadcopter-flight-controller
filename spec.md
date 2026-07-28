# Spec - Quadcopter Flight Controller

Every number used in `pcb/`, `cad/`, and `sim/` should trace back to this file. If you change something here, it should ripple out to the other phases, not get re-typed as a new magic number somewhere else.

## Airframe

| Parameter | Value |
|---|---|
| Frame class | 250 mm motor-to-motor diagonal (X config) |
| Motors | 2306, 2400 KV, 4x |
| Props | 5" (127 mm) |
| Battery | 4S LiPo, 1500 mAh, 14.8 V nominal |
| Target all-up weight (AUW) | ~650 g |
| Hover thrust per motor | ~1.6 N (650 g x 9.81 / 4) |

## Motor model

Real thrust-stand data for 2306/2400KV motors on 5" props (Emax RS2306 2400kv family, tested on miniquadtestbench.com) tops out around 1100-1400 g of thrust per motor at full throttle on 4S. That's the anchor point for the estimate below. I don't have a datasheet-grade thrust curve for this exact motor/prop/battery combo, so I derived kT and kQ instead of inventing precise-looking numbers. Treat these as reasonable-order-of-magnitude estimates, not verified hardware values.

Method:
- No-load speed at 4S: 2400 KV x 14.8 V ≈ 35,500 RPM. Under a real 5" prop load, racing motors typically sag to somewhere around 28,000 RPM at max sustained throttle.
- Picking max thrust ≈ 13 N (~1325 g, middle of the observed 1100-1400 g range) at ω_max ≈ 2930 rad/s gives:
  - **kT ≈ 1.5e-6 N·s²/rad²** (F = kT · ω²)
- Reaction torque (yaw authority) uses the common rule-of-thumb that a 5" multirotor prop's drag torque is roughly 3-8% of its thrust times the prop radius:
  - **kQ ≈ 7.5e-8 N·m·s²/rad²**
- Working these backwards, hover (1.6 N/motor) lands at ω_hover ≈ 1030 rad/s ≈ 9,800 RPM, which is about 28% of max RPM. That's a plausible hover throttle for a racing motor on a light 650 g frame (these motors are deliberately overpowered for punch-outs and recovery authority, so low hover throttle is expected, not a bug).
- Motor electrical/mechanical lag: **τ ≈ 0.02 s** (typical first-order response time for small FPV motor + ESC combos, per brief).

## Control loop rates

- Rate (inner) loop: 500 Hz
- Attitude (outer) loop: 250 Hz
- Rule used: IMU output data rate must be > 2x the fastest loop (500 Hz), so > 1 kHz minimum.

## IMU choice

ICM-42688-P, SPI. Datasheet specs (TDK InvenSense):
- Gyro noise density: 2.8 mdps/√Hz
- Accel noise density: 70 µg/√Hz
- Max ODR: 32 kHz (we'll run it far below that, e.g. 1-2 kHz, but it comfortably clears the >1 kHz requirement above)

This is why the IMU is on SPI1 rather than I2C in the schematic. I2C tops out well below what a 500 Hz rate loop wants once you account for register-read overhead.

## Barometer

BMP280 on I2C1 (altitude only, not latency-critical, so I2C is fine here).

## MCU

STM32F411CEU6, UFQFPN48. 100 MHz Cortex-M4F, enough headroom for 500 Hz control math plus sensor fusion.

## Board

- 36x36 mm outline
- 30.5x30.5 mm M3 mounting hole pattern (standard "FC30.5" footprint; this exact number is reused for the CAD frame's standoff pattern in Phase 2)

## Open assumptions to flag if anyone pushes back on this spec

- kT/kQ are derived estimates, not measured on this exact motor/prop/battery combination.
- τ (motor time constant) is a typical-value assumption, not measured.
- Everything else (frame size, battery, MCU, IMU, board size/hole pattern) is a normal, real part choice for this class of build.
