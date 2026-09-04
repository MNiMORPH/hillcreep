"""Probe A -- what do measured creep profiles say the parameters must be?

Settles: the defaults and slider ranges that ship in both demos.

Derived from measurement rather than chosen, after an earlier version of this
probe anchored the e-folding depth on Landlab's `soil_transport_decay_depth`
default of 1.0 m.  That is a placeholder in a component's signature, not a
measurement, and it was five to twenty times too deep.

The measurement is Roger Hooke's, from the Bevens Creek creep stations in the
Minnesota River Valley: segmented dowels set into vertical holes in 1968 and
excavated 9.5 years later.  Read off his six profiles:

  * the whole soil profile is **0 to 42 cm**;
  * displacement is concentrated in the top 5-15 cm and gone by 20-40 cm, so
    the e-folding depth is of order **0.03-0.2 m**;
  * surface displacements are 1.0-8.0 cm over 9.5 years, i.e. **1.1-8.4 mm/yr**.

Independently, applications of the Johnstone & Hilley (2015) law in the
literature set the transport decay depth to 0.1 m, and Deshpande et al. (2021)
report field surface velocities of order 1e-9 m/s, about 32 mm/yr.

Run:  python3 prototypes/probe_a_no_bedrock_scales.py
"""
import numpy as np

L = 100.0                       # hillslope width [m]

print("(1) Hooke's surface displacements, converted to velocities")
disp_cm = [("1", 1.0), ("2", 2.4), ("2", 2.2), ("3", 4.2), ("3", 4.5), ("4", 8.0)]
us = [d / 9.5 * 10.0 for _, d in disp_cm]
for (st, d), u in zip(disp_cm, us):
    print("    station %-2s  %4.1f cm / 9.5 yr  =  %.2f mm/yr" % (st, d, u))
print("    range %.1f-%.1f mm/yr, mean %.1f" % (min(us), max(us), np.mean(us)))

print()
print("(2) dz_u is pinned directly, because steady surface velocity does not")
print("    involve k_u at all:  u_s = edot L / (2 dz_u)")
print("     dz_u [m]   u_s at the toe [mm/yr] for edot = 0.01 mm/yr")
for dz in (0.03, 0.05, 0.10, 0.20, 0.40, 0.50, 1.00, 2.00):
    print("      %5.2f      %8.2f%s" % (dz, 0.01e-3 * L / (2 * dz) * 1e3,
                                        "   <- shipped" if dz == 0.10 else
                                        "   <- old default, deeper than Hooke's whole soil"
                                        if dz == 0.50 else ""))

print()
print("(3) The self-consistent set, worked forward from the measurement")
dz_u, u_s = 0.10, 0.005          # 5 mm/yr, mid-range of Hooke
edot = 2.0 * u_s * dz_u / L
print("    dz_u = %.2f m (Hooke), u_s = %.1f mm/yr (Hooke)" % (dz_u, u_s * 1e3))
print("    => edot = 2 u_s dz_u / L = %.3f mm/yr, forced, not chosen" % (edot * 1e3))
print("    k_u = u_s / S, so it needs a slope; the model's own steady toe slope")
print("    closes the loop:")
print("      toe slope   k_u [m/yr]   k_hs [m2/yr]   crest [m]   relax [yr]")
for S in (0.15, 0.25, 0.35):
    k_u = u_s / S
    k_hs = k_u * dz_u
    print("        %.2f       %.3f        %.4f       %6.2f     %.2e"
          % (S, k_u, k_hs, edot * L ** 2 / (8 * k_hs),
             L ** 2 / (np.pi ** 2 * k_hs)))

print()
print("(4) Shipped defaults and ranges")
K_U, DZ_U, EDOT = 0.02, 0.10, 0.01e-3
k_hs = K_U * DZ_U
print("    k_u = %.3f m/yr, dz_u = %.2f m, edot = %.3f mm/yr" % (K_U, DZ_U, EDOT * 1e3))
print("    -> k_hs = %.4f m2/yr (a result), crest %.2f m, toe slope %.3f (%.1f deg),"
      % (k_hs, EDOT * L**2 / (8*k_hs), 4*(EDOT*L**2/(8*k_hs))/L,
         np.degrees(np.arctan(4*(EDOT*L**2/(8*k_hs))/L))))
print("       u_s at the toe %.2f mm/yr, relaxation %.2e yr"
      % (EDOT * L / (2*DZ_U) * 1e3, L**2/(np.pi**2*k_hs)))
print()
print("    ranges: k_u 0.010-0.050, dz_u 0.05-0.40, edot -0.002 to +0.020 mm/yr")
print("      k_hs spans %.4f to %.4f m2/yr" % (0.010*0.05, 0.050*0.40))
print("      measured hillslope diffusivities are commonly 0.001-0.01 m2/yr,")
print("      so the range brackets them rather than sitting above them.")
print()
print("(5) The time step follows the largest k_hs on offer, so it grows with the")
print("    same factor k_hs shrank by, and the animation keeps its pace:")
DX = 1.0
for kmax, label in ((0.100, "old"), (0.050 * 0.40, "new")):
    dt = 0.25 * DX**2 / kmax
    print("      %s: k_hs_max %.3f -> dt %.1f yr, and 400 steps a frame = %.0f yr/frame"
          % (label, kmax, dt, 400*dt))
