"""The fault-scarp figure: the scarp above, the creep that flattens it below.

    python3 examples/figure_scarp.py --kyr 5 --out scarp.png
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from hillcreep import Scarp

ZETA_EFOLDINGS = 4.0        # same rule as the hillslope figure; 98.2% of the flux
N_ZETA = 121


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--k-u", type=float, default=0.02)
    p.add_argument("--dz-u", type=float, default=0.5)
    p.add_argument("--height", type=float, default=5.0)
    p.add_argument("--angle", type=float, default=30.0)
    p.add_argument("--kyr", type=float, default=5.0)
    p.add_argument("--out", default="scarp.png")
    a = p.parse_args()

    s = Scarp(k_u=a.k_u, dz_u=a.dz_u, height=a.height, angle=a.angle)
    s.run(a.kyr * 1e3)

    z_display = ZETA_EFOLDINGS * s.dz_u
    zeta = np.linspace(0.0, z_display, N_ZETA)
    u = s.velocity_field(zeta) * 1e3
    u_max = float(np.max(u)) or 1e-6

    fig, (ax_z, ax_u) = plt.subplots(
        2, 1, figsize=(8.4, 6.0), sharex=True,
        gridspec_kw={"height_ratios": [1.3, 1.0], "hspace": 0.12})

    ax_z.plot(s.x, s.initial_profile(), "--", color="0.55", lw=1.2,
              label="freshly cut, %.0f$^\\circ$" % a.angle)
    ax_z.plot(s.x, s.z, "k-", lw=2.5, label="after %.0f kyr" % a.kyr)
    ax_z.plot(s.x, s.analytic(), ":", color="#c0392b", lw=1.6,
              label="closed form")
    ax_z.set_ylabel("Elevation [m]")
    ax_z.legend(loc="upper right", frameon=False, fontsize=9)
    ax_z.set_title(
        r"$k_\mathrm{hs} = k_u \Delta z_u = %.4g$ m$^2$/yr"
        "        morphologic age  "
        r"$k_\mathrm{hs} t = %.0f$ m$^2$"
        "\nsteepest slope %.0f$^\\circ$ → %.1f$^\\circ$"
        % (s.k_hs, s.morphologic_age, a.angle,
           np.degrees(np.arctan(s.max_slope()))),
        fontsize=10, pad=10)

    mesh = ax_u.pcolormesh(s.x, zeta, u, cmap="Reds", shading="gouraud",
                           vmin=0.0, vmax=u_max)
    ax_u.invert_yaxis()
    ax_u.set_ylabel(r"Depth below the" "\n" r"surface  $\zeta$ [m]")
    ax_u.set_xlabel("Distance [m]")
    ax_u.set_xlim(s.x[0], s.x[-1])

    cb = fig.colorbar(mesh, ax=ax_u, pad=0.02, aspect=16)
    cb.set_label("Downslope creep velocity  $u$  [mm/yr]\n"
                 r"transport is left $\rightarrow$ right")

    ax_z.set_position([ax_z.get_position().x0, ax_z.get_position().y0,
                       ax_u.get_position().width, ax_z.get_position().height])
    fig.savefig(a.out, dpi=150, bbox_inches="tight")
    print("wrote %s" % a.out)
    print("  k_hs = %.5g m2/yr, k_hs*t = %.1f m2, slope %.0f -> %.2f deg,"
          " max |numerical - closed form| = %.2e m"
          % (s.k_hs, s.morphologic_age, a.angle,
             np.degrees(np.arctan(s.max_slope())),
             np.max(np.abs(s.z - s.analytic()))))


if __name__ == "__main__":
    main()
