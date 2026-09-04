"""Probe C -- three numerical questions the demo cannot be written without.

Settles: (1) the display depth of the velocity panel, (2) the time step, and
(3) how many model steps to advance per animation frame.

(1) With no bedrock the mobile layer is semi-infinite, so the velocity panel
    has to be truncated somewhere.  How much of the flux is below the cut?
(2) Explicit diffusion is stable for dt <= dx**2 / (2 D).  D = k_u*dz_u varies
    with the sliders, so the step must be safe at the largest D on offer.
(3) The relaxation time is ~1e5 yr.  Drawn one step per frame that is hours of
    animation, so a frame must advance many steps.  How many, measured.

Run:  python3 prototypes/probe_c_numerics_and_pacing.py
"""
import time

import numpy as np

L, NX = 100., 101
DX = L / (NX - 1)
KU_MIN, KU_MAX, KU0 = 0.01, 0.05, 0.02       # [m/yr]
DZU_MIN, DZU_MAX, DZU0 = 0.05, 0.40, 0.10      # [m]
E0 = 0.01e-3                              # [m/yr]

print("(1) Flux captured above a truncation depth Z_DISPLAY, as a fraction of")
print("    the full integral k_u*dz_u*S.  Fraction = 1 - exp(-Z/dz_u).")
for Z in (1.0, 2.0, 3.0, 5.0):
    print("    Z_DISPLAY=%.1f m:" % Z, "  ".join(
        "H*=%.2f -> %5.1f%%" % (dzu, 100. * (1. - np.exp(-Z / dzu)))
        for dzu in (DZU_MIN, DZU0, 1.0, DZU_MAX)))

print()
print("(2) Stability.  D_max = K_max * H*_max = %.3f m2/yr" % (KU_MAX * DZU_MAX))
D_max = KU_MAX * DZU_MAX
dt_stab = DX ** 2 / (2. * D_max)
DT = 0.25 * DX ** 2 / D_max
print("    dx = %.2f m, dt_stability = %.2f yr, chosen DT = %.2f yr (quarter of it)"
      % (DX, dt_stab, DT))

print()
print("(3) Pacing.  Steps to reach 95%% of the steady crest, from flat, and the")
print("    frames that implies at STEPS_PER_FRAME, with measured wall time.")

x = np.linspace(0., L, NX)


def run_to_95(k_u, dz_u, E, steps_per_frame, max_frames=2000):
    D = k_u * dz_u
    crest_target = 0.95 * E * L ** 2 / (8. * D)
    z = np.zeros(NX)
    z_river = 0.
    frames = 0
    t0 = time.perf_counter()
    # Relief, not elevation: the river falls, so the whole profile falls with
    # it and z.max() alone never reaches the target.  (This probe reported
    # "capped" for every case until the comparison was made relative.)
    while (z.max() - z_river) < crest_target and frames < max_frames:
        for _ in range(steps_per_frame):
            z[1:-1] += DT * D * (z[:-2] - 2. * z[1:-1] + z[2:]) / DX ** 2
            z_river -= E * DT
            z[0] = z[-1] = z_river
        frames += 1
    wall = time.perf_counter() - t0
    return frames, wall, z.max() - z_river


for spf in (100, 200, 400):
    print("    STEPS_PER_FRAME = %3d:" % spf)
    for k_u, dzu in ((KU0, DZU0), (KU_MIN, DZU_MIN), (KU_MAX, DZU_MAX)):
        f, wall, relief = run_to_95(k_u, dzu, E0, spf)
        hit = "capped" if f >= 2000 else "reached"
        print("      k_u=%.2f H*=%.2f (D=%.4f): %5d frames (%s), %5.1f s at 30 fps,"
              "  compute %6.3f ms/frame,  relief %.2f m"
              % (k_u, dzu, k_u * dzu, f, hit, f / 30., 1e3 * wall / max(f, 1), relief))
