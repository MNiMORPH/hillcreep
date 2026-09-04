"""Probe A -- do measurable creep velocities give a watchable demo?

Settles: the default k_u, dz_u, L and E that ship in the demo.

No bedrock: the mobile layer is semi-infinite, so

    u(zeta) = k_u * S * exp(-zeta / dz_u)          [m/yr]
    q       = integral_0^inf u dzeta = k_u * dz_u * S
    D       = k_u * dz_u                           [m2/yr], exactly

Steady state under uniform base-level lowering at rate E:
    crest above base level   = E * L**2 / (8 * D)
    toe slope                = 4 * crest / L
    slowest relaxation mode  = L**2 / (pi**2 * D)
    surface velocity at toe  = E * L / (2 * dz_u)     (mass balance; see probe B)

Run:  python3 prototypes/probe_a_no_bedrock_scales.py
"""
import numpy as np


def report(L, k_u, dz_u, E_mm):
    E = E_mm * 1e-3
    D = k_u * dz_u
    crest = E * L**2 / (8.0 * D)
    S_toe = 4.0 * crest / L
    tau = L**2 / (np.pi**2 * D)
    u_s_toe = k_u * S_toe
    print("  L=%6.0f k_u=%.4f H*=%.2f E=%.3f mm/yr | D=%.5f m2/yr crest=%7.2f m"
          " S_toe=%.3f (%4.1f deg) u_s(toe)=%6.2f mm/yr tau=%.3g yr"
          % (L, k_u, dz_u, E_mm, D, crest, S_toe, np.degrees(np.arctan(S_toe)),
             u_s_toe * 1e3, tau))


print("Andy's 2013 course script: D_eff = k*dx**2 = 5e-3 * 10**2 = 0.5 m2/yr,")
print("L = 1000 m, E = 0.2 mm/yr.  Factored through this transport law it needs")
print("k_u*dz_u = 0.5; at a plausible dz_u = 0.5 m that is k_u = 1.0 m/yr:")
report(1000., 1.0, 0.5, 0.2)

print()
print("Measured soil creep: surface velocities of order mm/yr.")
print("Proposed demo defaults:")
report(100., 0.02, 0.5, 0.05)

print()
print("Sensitivity of the proposed defaults to each slider, one at a time:")
print(" k_u sweep (H*=0.5, L=100, E=0.05):")
for k_u in (0.005, 0.01, 0.02, 0.05, 0.1):
    report(100., k_u, 0.5, 0.05)
print(" H* sweep (k_u=0.02, L=100, E=0.05):")
for Hs in (0.1, 0.25, 0.5, 1.0, 2.0):
    report(100., 0.02, Hs, 0.05)
print(" E sweep (k_u=0.02, H*=0.5, L=100):")
for E in (0.0, 0.02, 0.05, 0.1, 0.2):
    report(100., 0.02, 0.5, E)
