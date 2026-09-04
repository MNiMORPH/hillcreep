"""The two-panel figure the interactive demo is built around.

Top: the hillslope at true vertical scale, with the steady parabola it chases.
Bottom: downslope creep velocity on its own depth axis, because the motion
happens over ~1 m while the hill has metres of relief (design 04).

    python3 examples/figure_two_panel.py --out hillcreep_two_panel.png
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

from hillcreep import Hillslope

#: How deep the lower panel reaches, in e-folding depths.  A static figure has
#: a single H*, so unlike the interactive demo it can follow that H* directly:
#: the panel then looks the same whatever the model's scale, and always shows
#: the same 1 - exp(-4) = 98.2% of the flux.  The demo cannot do this, because
#: its axis would move while a student drags the slider (design 04).
ZETA_EFOLDINGS = 4.0
N_ZETA = 121


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--k-u", type=float, default=0.02,
                   help="surface creep velocity at unit slope [m/yr]")
    p.add_argument("--dz-u", type=float, default=0.5,
                   help="creep e-folding depth, the notes' Delta z_u [m]")
    p.add_argument("--edot", type=float, default=0.05,
                   help="river incision rate [mm/yr]")
    p.add_argument("--length", type=float, default=100.0, help="hillslope width [m]")
    p.add_argument("--kyr", type=float, default=300.0, help="run duration [kyr]")
    p.add_argument("--out", default="hillcreep_two_panel.png")
    a = p.parse_args()

    h = Hillslope(length=a.length, k_u=a.k_u, dz_u=a.dz_u,
                  incision_rate=a.edot * 1e-3)
    h.run(a.kyr * 1e3)

    z_display = ZETA_EFOLDINGS * h.dz_u
    zeta = np.linspace(0.0, z_display, N_ZETA)
    u = h.velocity_field(zeta) * 1e3                 # mm/yr
    u_max = np.max(np.abs(u))

    fig, (ax_z, ax_u) = plt.subplots(
        2, 1, figsize=(8.0, 6.4), sharex=True,
        gridspec_kw={"height_ratios": [1.45, 1.0], "hspace": 0.12})

    base = h.left.bed
    ax_z.plot(h.x, h.steady_profile() - base, "--", color="0.55", lw=1.2,
              label="steady form")
    ax_z.plot(h.x, h.z - base, "k-", lw=2.5, label="hillslope")
    ax_z.axhline(0.0, color="#2b6cb0", lw=1.2)
    ax_z.plot([h.x[0], h.x[-1]], [0.0, 0.0], "v", color="#2b6cb0", ms=9,
              clip_on=False, label="rivers")
    ax_z.set_ylabel("Elevation above\nthe rivers [m]")
    ax_z.legend(loc="upper right", frameon=False, fontsize=9)
    ax_z.set_title(
        r"$k_\mathrm{hs} = k_u \Delta z_u = %.4g$ m$^2$/yr"
        "   is a consequence, not a setting\n"
        r"($k_u$ = %.3g m/yr,   $\Delta z_u$ = %.2g m,"
        r"   $\dot{\varepsilon}$ = %.3g mm/yr)"
        % (h.k_hs, h.k_u, h.dz_u, h.incision_rate * 1e3),
        fontsize=10, pad=10)

    mesh = ax_u.pcolormesh(
        h.x, zeta, u, cmap="RdBu_r", shading="gouraud",
        norm=TwoSlopeNorm(vmin=-u_max, vcenter=0.0, vmax=u_max))
    ax_u.invert_yaxis()
    ax_u.set_ylabel(r"Depth below the" "\n" r"surface  $\zeta$ [m]")
    ax_u.set_xlabel("Distance across the hillslope [m]")
    ax_u.set_xlim(h.x[0], h.x[-1])

    # Colorbar on the velocity panel only: it describes that panel, and
    # spanning both implies the topography is on the same scale.
    cb = fig.colorbar(mesh, ax=ax_u, pad=0.02, aspect=16)
    cb.set_label("Downslope creep velocity  $u$  [mm/yr]\n"
                 r"$\leftarrow$ moving left      moving right $\rightarrow$")

    ax_u.text(0.5 * h.length, 0.30 * z_display,
              "no bedrock: the panel bottom is a viewing\n"
              "depth, not the base of the soil",
              ha="center", va="center", fontsize=8, color="0.35")
    ax_u.annotate("surface: $u_s$ = %.2f mm/yr"
                  % (abs(h.surface_velocity()[-1]) * 1e3),
                  xy=(h.x[-1], 0.0), xytext=(-10, 16), textcoords="offset points",
                  ha="right", va="bottom", fontsize=9, color="#7f1d1d")

    ax_z.set_position([ax_z.get_position().x0, ax_z.get_position().y0,
                       ax_u.get_position().width, ax_z.get_position().height])

    fig.savefig(a.out, dpi=150, bbox_inches="tight")
    print("wrote %s" % a.out)
    print("  k_hs = %.5g m2/yr, relief = %.3f m (steady %.3f m),"
          " u_s(toe) = %.3f mm/yr"
          % (h.k_hs, h.z.max() - base, h.steady_profile().max() - base,
             abs(h.surface_velocity()[-1]) * 1e3))


if __name__ == "__main__":
    main()
