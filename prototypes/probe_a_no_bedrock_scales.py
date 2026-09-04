"""Probe A -- do measurable creep velocities give a watchable demo?

Settles: the default K, H_star, L and E that ship in the demo.

No bedrock: the mobile layer is semi-infinite, so

    u(zeta) = K * S * exp(-zeta / H_star)          [m/yr]
    q       = integral_0^inf u dzeta = K * H_star * S
    D       = K * H_star                           [m2/yr], exactly

Steady state under uniform base-level lowering at rate E:
    crest above base level   = E * L**2 / (8 * D)
    toe slope                = 4 * crest / L
    slowest relaxation mode  = L**2 / (pi**2 * D)
    surface velocity at toe  = E * L / (2 * H_star)     (mass balance; see probe B)

Run:  python3 prototypes/probe_a_no_bedrock_scales.py
"""
import numpy as np


def report(L, K, H_star, E_mm):
    E = E_mm * 1e-3
    D = K * H_star
    crest = E * L**2 / (8.0 * D)
    S_toe = 4.0 * crest / L
    tau = L**2 / (np.pi**2 * D)
    u_s_toe = K * S_toe
    print("  L=%6.0f K=%.4f H*=%.2f E=%.3f mm/yr | D=%.5f m2/yr crest=%7.2f m"
          " S_toe=%.3f (%4.1f deg) u_s(toe)=%6.2f mm/yr tau=%.3g yr"
          % (L, K, H_star, E_mm, D, crest, S_toe, np.degrees(np.arctan(S_toe)),
             u_s_toe * 1e3, tau))


print("Andy's 2013 course script: D_eff = k*dx**2 = 5e-3 * 10**2 = 0.5 m2/yr,")
print("L = 1000 m, E = 0.2 mm/yr.  Factored through this transport law it needs")
print("K*H_star = 0.5; at a plausible H_star = 0.5 m that is K = 1.0 m/yr:")
report(1000., 1.0, 0.5, 0.2)

print()
print("Measured soil creep: surface velocities of order mm/yr.")
print("Proposed demo defaults:")
report(100., 0.02, 0.5, 0.05)

print()
print("Sensitivity of the proposed defaults to each slider, one at a time:")
print(" K sweep (H*=0.5, L=100, E=0.05):")
for K in (0.005, 0.01, 0.02, 0.05, 0.1):
    report(100., K, 0.5, 0.05)
print(" H* sweep (K=0.02, L=100, E=0.05):")
for Hs in (0.1, 0.25, 0.5, 1.0, 2.0):
    report(100., 0.02, Hs, 0.05)
print(" E sweep (K=0.02, H*=0.5, L=100):")
for E in (0.0, 0.02, 0.05, 0.1, 0.2):
    report(100., 0.02, 0.5, E)
