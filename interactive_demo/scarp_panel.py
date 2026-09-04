"""A fault scarp diffusing away, in the browser.

The companion to ``hillcreep_panel.py``. Same two knobs, same transport law,
same velocity panel underneath -- and no rivers, so the scarp does nothing but
relax. Its shape is a clock, which is what makes it the place to meet
morphologic dating.

Build and view it with::

    artesian build interactive_demo/scarp_panel.py -o _artesian_build \
        -p . -p ../artesian -r numpy --serve
"""
import numpy as np
import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.models import LinearColorMapper
from bokeh.models import Range1d
from bokeh.palettes import RdBu11
from bokeh.plotting import figure

from artesian.live import animator, reset_button, responsive
from hillcreep import Scarp

pn.extension()

#: Laid out for this width, and scaled above it by the embedding page. Matches
#: the hillslope exercise so the two demos sit at the same size on the site.
DESIGN_WIDTH = 900
SLIDER_WIDTH = 420

LENGTH = 240.0                  # domain width [m]
N_NODES = 241                   # dx = 1 m
HEIGHT = 5.0                    # scarp height, crest to toe [m]
ANGLE = 30.0                    # initial face angle [degrees]

KU_MIN, KU_MAX, KU0 = 0.01, 0.05, 0.02       # [m/yr] at unit slope
DZU_MIN, DZU_MAX, DZU0 = 0.05, 0.40, 0.10      # [m]

#: Depth reached by the velocity panel, as a multiple of the largest e-folding
#: depth the slider offers. Derived from the model's own depth scale rather
#: than hand-picked, and taken from the slider's *bound* so the axis cannot
#: move while a student drags. Same rule as the hillslope demo.
Z_DISPLAY_IN_DZU_MAX = 1.0
Z_DISPLAY = Z_DISPLAY_IN_DZU_MAX * DZU_MAX
N_ZETA = 121

DX = LENGTH / (N_NODES - 1)
# Explicit diffusion is stable for dt <= dx**2 / 2 k_hs; a quarter of the limit
# at the largest k_hs the sliders allow.
DT = 0.25 * DX ** 2 / (KU_MAX * DZU_MAX)     # 2.5 yr

#: Measured: at the default settings this reaches a morphologic age of 200 m2
#: -- by which point a 30 degree face has relaxed to about 6 degrees -- in
#: roughly 320 frames, about 11 s at 30 fps.
STEPS_PER_FRAME = 25

zeta = np.linspace(0.0, Z_DISPLAY, N_ZETA)


def _smooth_palette(anchors, n=256):
    """Interpolate a short palette to ``n`` colours.

    bokeh's ``diverging_palette`` leaves a seam at its midpoint where two
    sub-palettes meet on different near-whites. Interpolating ColorBrewer RdBu
    through a single white removes it.
    """
    rgb = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in anchors]
    out = []
    for k in range(n):
        pos = k * (len(rgb) - 1) / (n - 1.0)
        i = min(int(pos), len(rgb) - 2)
        f = pos - i
        out.append("#%02x%02x%02x" % tuple(
            int(round(rgb[i][c] + f * (rgb[i + 1][c] - rgb[i][c])))
            for c in range(3)))
    return out


# `sim`, never `state`: panel exports pn.state, and shadowing it fails silently.
sim = {"scarp": Scarp(length=LENGTH, n_nodes=N_NODES, k_u=KU0, dz_u=DZU0,
                      height=HEIGHT, angle=ANGLE)}

k_u = pn.widgets.FloatSlider(
    sizing_mode="stretch_width", max_width=SLIDER_WIDTH,
    name="Surface creep velocity at unit slope  k_u  [m/yr]",
    start=KU_MIN, end=KU_MAX, step=0.005, value=KU0, format="0.000")
dz_u = pn.widgets.FloatSlider(
    sizing_mode="stretch_width", max_width=SLIDER_WIDTH,
    name="Creep e-folding depth  Δz_u  [m]",
    start=DZU_MIN, end=DZU_MAX, step=0.01, value=DZU0, format="0.00")

readout = pn.pane.Markdown("", sizing_mode="stretch_width",
                           styles={"font-size": "1.05em"})


def _sync():
    s = sim["scarp"]
    s.k_u = k_u.value
    s.dz_u = dz_u.value
    return s


def step():
    s = _sync()
    for _ in range(STEPS_PER_FRAME):
        s.advance(DT)
    _redraw()


def _redraw():
    s = _sync()
    profile.data = {"x": s.x, "z": s.z}
    initial.data = {"x": s.x, "z": s.initial_profile()}

    u = s.velocity_field(zeta) * 1e3          # mm/yr
    scale = max(float(np.max(np.abs(u))), 1e-9)
    velocity.data = {"u": [u]}
    mapper.low, mapper.high = 0.0, scale

    slope = s.max_slope()
    fig_z.title.text = (
        "t = %.1f kyr        k_hs = k_u Δz_u = %.4g m²/yr"
        % (s.t / 1000.0, s.k_hs))
    fig_u.title.text = ("fastest surface creep = %.2f mm/yr"
                        % (float(np.max(s.surface_velocity())) * 1e3))

    warn = "" if s.ends_are_quiet() else (
        "  ·  **the scarp has reached the ends of the domain** — the "
        "closed form assumes an infinite surface and no longer applies")
    readout.object = (
        "**k_hs = k_u × Δz_u = %.3f × %.2f = %.4f m²/yr**"
        "  ·  morphologic age **k_hs t = %.0f m²**"
        "  ·  steepest slope %.3f (%.1f°), from %.1f°%s"
        % (s.k_u, s.dz_u, s.k_hs, s.morphologic_age,
           slope, np.degrees(np.arctan(slope)), ANGLE, warn))


def do_reset():
    sim["scarp"] = Scarp(length=LENGTH, n_nodes=N_NODES, k_u=k_u.value,
                         dz_u=dz_u.value, height=HEIGHT, angle=ANGLE)
    _redraw()


s0 = sim["scarp"]
profile = ColumnDataSource(data={"x": s0.x, "z": s0.z})
initial = ColumnDataSource(data={"x": s0.x, "z": s0.initial_profile()})
velocity = ColumnDataSource(data={"u": [s0.velocity_field(zeta) * 1e3]})

# Transport is one-directional here -- everything moves right -- so only the
# warm half of the diverging palette is used: white is no motion, deep red is
# fastest. The hillslope demo needs both halves because its divide separates
# material moving in opposite directions.
mapper = LinearColorMapper(palette=_smooth_palette(RdBu11)[128:], low=0.0, high=1.0)

fig_z = figure(height=300, width=880, title="",
               y_axis_label="Elevation [m]", toolbar_location=None)
fig_z.line("x", "z", source=initial, line_width=1, line_dash="dashed",
           color="gray", legend_label="freshly cut, %.0f°" % ANGLE)
fig_z.line("x", "z", source=profile, line_width=3, color="black",
           legend_label="scarp now")
fig_z.x_range = Range1d(0.0, LENGTH)
fig_z.y_range = Range1d(-0.62 * HEIGHT, 0.62 * HEIGHT)
fig_z.legend.location = "top_right"
fig_z.legend.background_fill_alpha = 0.6

fig_u = figure(height=240, width=880, title="",
               x_axis_label="Distance [m]",
               y_axis_label="Depth below\nthe surface  ζ [m]",
               x_range=fig_z.x_range, toolbar_location=None)
fig_u.y_range = Range1d(Z_DISPLAY, 0.0)
fig_u.image(image="u", source=velocity, x=0.0, y=0.0, dw=LENGTH, dh=Z_DISPLAY,
            color_mapper=mapper)

responsive(fig_z)
responsive(fig_u)

run = animator(step)

for widget in (k_u, dz_u):
    widget.param.watch(lambda event: _redraw(), "value")

_redraw()

pn.Column(
    pn.pane.Markdown(
        "### A fault scarp, left alone\n"
        "A fault cuts the ground and leaves a step far steeper than creep "
        "could ever have built. Nothing holds it — no rivers, nothing "
        "carried away — so it simply relaxes, and its volume never "
        "changes: what leaves the face lands at its foot.\n\n"
        "Press **▶**. Watch the **morphologic age**, **k_hs t**, rather "
        "than the clock. The shape depends on those two only through their "
        "product, so a fast scarp seen early and a slow one seen late are the "
        "same scarp. That is what makes a surveyed scarp datable — and "
        "why it cannot be dated without knowing **k_hs** first."),
    pn.Row(run, reset_button(do_reset, name="Re-cut the scarp")),
    pn.Row(k_u, dz_u, sizing_mode="stretch_width", max_width=DESIGN_WIDTH),
    readout, fig_z, fig_u,
    sizing_mode="stretch_width", max_width=DESIGN_WIDTH,
).servable(title="A fault scarp diffusing")
