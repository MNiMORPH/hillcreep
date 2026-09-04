"""Probe C -- three numerical questions the demo cannot be written without.

Settles: (1) the display depth of the velocity panel, (2) the time step, and
(3) how many model steps to advance per animation frame.

(1) With no bedrock the mobile layer is semi-infinite, so the velocity panel
    has to be truncated somewhere.  How much of the flux is below the cut?
(2) Explicit diffusion is stable for dt <= dx**2 / (2 D).  D = K*H_star varies
    with the sliders, so the step must be safe at the largest D on offer.
(3) The relaxation time is ~1e5 yr.  Drawn one step per frame that is hours of
    animation, so a frame must advance many steps.  How many, measured.

Run:  python3 prototypes/probe_c_numerics_and_pacing.py
"""
import time

import numpy as np

L, NX = 100., 101
DX = L / (NX - 1)
K_MIN, K_MAX, K0 = 0.01, 0.05, 0.02       # [m/yr]
HS_MIN, HS_MAX, HS0 = 0.25, 2.0, 0.5      # [m]
E0 = 0.05e-3                              # [m/yr]

print("(1) Flux captured above a truncation depth Z_DISPLAY, as a fraction of")
print("    the full integral K*H_star*S.  Fraction = 1 - exp(-Z/H_star).")
for Z in (1.0, 2.0, 3.0, 5.0):
    print("    Z_DISPLAY=%.1f m:" % Z, "  ".join(
        "H*=%.2f -> %5.1f%%" % (hs, 100. * (1. - np.exp(-Z / hs)))
        for hs in (HS_MIN, HS0, 1.0, HS_MAX)))

print()
print("(2) Stability.  D_max = K_max * H*_max = %.3f m2/yr" % (K_MAX * HS_MAX))
D_max = K_MAX * HS_MAX
dt_stab = DX ** 2 / (2. * D_max)
DT = 0.25 * DX ** 2 / D_max
print("    dx = %.2f m, dt_stability = %.2f yr, chosen DT = %.2f yr (quarter of it)"
      % (DX, dt_stab, DT))

print()
print("(3) Pacing.  Steps to reach 95%% of the steady crest, from flat, and the")
print("    frames that implies at STEPS_PER_FRAME, with measured wall time.")

x = np.linspace(0., L, NX)


def run_to_95(K, H_star, E, steps_per_frame, max_frames=2000):
    D = K * H_star
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
    for K, hs in ((K0, HS0), (K_MIN, HS_MIN), (K_MAX, HS_MAX)):
        f, wall, relief = run_to_95(K, hs, E0, spf)
        hit = "capped" if f >= 2000 else "reached"
        print("      K=%.2f H*=%.2f (D=%.4f): %5d frames (%s), %5.1f s at 30 fps,"
              "  compute %6.3f ms/frame,  relief %.2f m"
              % (K, hs, K * hs, f, hit, f / 30., 1e3 * wall / max(f, 1), relief))
