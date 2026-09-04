"""hillcreep as a browser demo: a hillslope, and the motion underneath it.

The k_hs is not a slider.  A student sets how fast soil creeps at the
surface per unit slope (k_u) and how quickly that motion dies away with depth
(H*), and D = k_u H* is reported back.  The lower panel draws the velocity
profile that D is a summary of.

Build and view it with::

    artesian build interactive_demo/hillcreep_panel.py -o _artesian_build \
        -p . -r numpy --serve
"""
import numpy as np
import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.models import LinearColorMapper
from bokeh.models import Range1d
from bokeh.palettes import RdBu11
from bokeh.plotting import figure

from artesian.live import animator, reset_button, responsive
from hillcreep import Hillslope

pn.extension()

#: The width this app is laid out for.  ``artesian build`` reads this constant
#: out of the source and records it in the compiled page; the embedding page
#: repeats it as ``data-design-width`` (see the GeomorphOnline exercise page for
#: why both are needed).  900 matches the other exercises on that site.
DESIGN_WIDTH = 900

#: Sliders stop here rather than spanning the pane.  The bound is in *layout*
#: pixels, so the embed's scaling still enlarges them: a bounded slider is not
#: a small slider on a large display.  Wider than corestone's because these
#: labels carry a symbol and a unit.
SLIDER_WIDTH = 420

LENGTH = 100.0                  # hillslope width [m]
N_NODES = 101

# Slider bounds.  The upper end of each is set by steepness, not by taste:
# probe_a shows that E = 0.2 mm/yr at the default k_u and H* gives a steady toe
# slope of 1.0 (45 degrees), well outside where a linear creep law is
# defensible.  See design/03.
KU_MIN, KU_MAX, KU0 = 0.01, 0.05, 0.02          # [m/yr] at unit slope
DZU_MIN, DZU_MAX, DZU0 = 0.25, 2.0, 0.5         # [m]
E_MIN, E_MAX, E0 = -0.05, 0.10, 0.05         # [mm/yr], positive = incising

#: How deep the velocity panel reaches, as a multiple of the *largest* H* the
#: slider offers.  Deriving it from the model's own depth scale means the panel
#: follows a rescaled model instead of needing a new hand-picked number; taking
#: the slider's upper bound rather than its current value means the axis does
#: not move under a student dragging the slider, which would destroy exactly
#: the comparison the panel exists to support.
#:
#: At 1.0 the deepest setting fills the panel and shows 63.2% of the flux,
#: while the default H* = 0.5 m keeps its motion in the top quarter.  At 1.5
#: the deepest setting shows 77.7% and the default is squeezed into the top
#: sixth.  One constant, and it is a proposal either way.  See design/04.
Z_DISPLAY_IN_DZU_MAX = 1.0

#: Depth shown in the velocity panel [m].  A viewing choice, not the base of
#: the soil -- there is no bedrock in this model.
Z_DISPLAY = Z_DISPLAY_IN_DZU_MAX * DZU_MAX
N_ZETA = 121

# Explicit diffusion is stable for dt <= dx**2 / 2D.  The sliders change D
# while it runs, so the step is sized from the largest D on offer, not the
# current one: a quarter of the limit at D = KU_MAX * DZU_MAX = 0.1 m2/yr.
DX = LENGTH / (N_NODES - 1)
DT = 0.25 * DX ** 2 / (KU_MAX * DZU_MAX)       # 2.5 yr

# probe_c, measured: 400 steps per frame reaches 95% of the steady crest in
# 307 frames (10.2 s at 30 fps) at the defaults, 1228 frames (40.9 s) at the
# slowest corner of the sliders, and 31 frames (1.0 s) at the fastest.
STEPS_PER_FRAME = 400

zeta = np.linspace(0.0, Z_DISPLAY, N_ZETA)


def _smooth_palette(anchors, n=256):
    """Interpolate a short palette to ``n`` colours.

    bokeh's ``diverging_palette(Blues256, Reds256)`` leaves a visible seam
    exactly at the midpoint, because the two sub-palettes end on different
    near-whites (#f7fbff and #fff5f0).  On this figure the midpoint is the
    drainage divide, so the artefact lands precisely where a student is meant
    to read "no motion here" -- and reads instead as a discontinuity in the
    hillslope.  Interpolating ColorBrewer RdBu through a single white removes
    it.  Caught by rendering the figure, not by reading the code.
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
sim = {"hill": Hillslope(length=LENGTH, n_nodes=N_NODES, k_u=KU0, dz_u=DZU0,
                         incision_rate=E0 * 1e-3)}

k_u = pn.widgets.FloatSlider(
    sizing_mode="stretch_width", max_width=SLIDER_WIDTH,
    name="Surface creep velocity at unit slope  k_u  [m/yr]",
    start=KU_MIN, end=KU_MAX, step=0.005, value=KU0, format="0.000")
dz_u = pn.widgets.FloatSlider(
    sizing_mode="stretch_width", max_width=SLIDER_WIDTH,
    name="Creep e-folding depth  \u0394z_u  [m]",
    start=DZU_MIN, end=DZU_MAX, step=0.05, value=DZU0, format="0.00")
E = pn.widgets.FloatSlider(
    sizing_mode="stretch_width", max_width=SLIDER_WIDTH,
    name="River incision rate  \u03b5\u0307  [mm/yr]   (negative = aggrading)",
    start=E_MIN, end=E_MAX, step=0.01, value=E0, format="0.00")

#: The diffusivity written out as a function of the two decay parameters, with
#: the current numbers substituted, plus how much hillslope is still exposed.
#: The product is the whole lesson, so it is shown being formed rather than
#: only as a result.
readout = pn.pane.Markdown("", sizing_mode="stretch_width",
                           styles={"font-size": "1.05em"})


def _sync():
    """Push the sliders into the model.  Read live, so they act while running."""
    hill = sim["hill"]
    hill.k_u = k_u.value
    hill.dz_u = dz_u.value
    hill.incision_rate = E.value * 1e-3
    return hill


def _elevation_range(hill):
    """Top of the elevation axis [m], from the steady crest for the sliders.

    A fixed axis cannot serve these sliders: the steady crest E L**2 / (8 D)
    spans 1.25 m to 50 m over their ranges, a factor of 40, so any single
    choice either clips the tall cases or renders the short ones as a flat
    line.  Scaling to the current steady crest instead makes the hill grow to
    fill the panel and stop there -- and because it depends only on the
    sliders, it does not rescale frame to frame while the animation runs.
    """
    steady_crest = (abs(hill.incision_rate) * hill.length ** 2
                    / (8.0 * hill.k_hs))
    return 1.18 * max(steady_crest,
                      float(np.max(hill.surface())) - hill.left.bed, 1.0)


def _colour_scale(hill):
    """Half-range of the velocity colour scale [m/yr].

    Fixed to the *steady* surface velocity at the toe, E L / (2 H*), which
    depends only on the sliders and so does not flicker frame to frame.  The
    colours therefore saturate as the hill approaches its steady form, which
    is a useful signal in itself.  When E is zero there is no steady velocity
    to scale by, so the present profile is used instead.
    """
    steady = abs(hill.incision_rate) * hill.length / (2.0 * hill.dz_u)
    return max(steady, np.max(np.abs(hill.surface_velocity())), 1e-9)


def step():
    """Advance one frame, reading the sliders as live forcing."""
    hill = _sync()
    for _ in range(STEPS_PER_FRAME):
        hill.advance(DT)
    _redraw()


def _redraw():
    hill = _sync()
    base = 0.5 * (hill.left.bed + hill.right.bed)

    profile.data = {"x": hill.x, "z": hill.surface() - base}
    # A hillslope whose base level is rising has no steady form to chase, so
    # the dashed curve is withdrawn rather than drawn as a meaningless
    # downward parabola.
    if hill.incision_rate > 0.0:
        steady.data = {"x": hill.x, "z": hill.steady_profile() - base}
    else:
        steady.data = {"x": [], "z": []}

    scale = _colour_scale(hill)
    velocity.data = {"u": [hill.velocity_field(zeta) * 1e3]}
    mapper.low, mapper.high = -scale * 1e3, scale * 1e3

    top = _elevation_range(hill)
    fig_z.y_range.start, fig_z.y_range.end = -0.06 * top, top
    valley.data = {"x": [0.0, hill.length], "y1": [-0.06 * top] * 2,
                   "y2": [0.0, 0.0]}

    fig_z.title.text = ("t = %.0f kyr        k_hs = k_u \u0394z_u = %.4g m\u00b2/yr"
                        % (hill.t / 1000.0, hill.k_hs))
    # Across the exposed span *inclusive of its bounding nodes*: the toe is a
    # boundary node and is never in the active mask, so a max over active
    # nodes alone reports the velocity one node inside the toe (4.90 rather
    # than 5.00 mm/yr at the shipped defaults).
    span = hill.exposed_span()
    u_toe = 0.0 if span is None else float(
        np.abs(hill.surface_velocity()[span[0]:span[1] + 1]).max())
    fig_u.title.text = ("surface creep velocity at the toe = %.2f mm/yr"
                        % (u_toe * 1e3))

    exposed = hill.exposed_length
    buried = "" if exposed >= hill.length else (
        "  \u00b7  **buried by aggradation:** %.0f m of hillslope, "
        "leaving **%.0f m** exposed" % (hill.length - exposed, exposed))
    steady_note = "" if hill.incision_rate > 0.0 else (
        "  \u00b7  *no steady form while base level is not falling*")
    readout.object = (
        "**k_hs = k_u \u00d7 \u0394z_u = %.3f \u00d7 %.2f "
        "= %.4f m\u00b2/yr**%s%s"
        % (hill.k_u, hill.dz_u, hill.k_hs, buried, steady_note))


def do_equilibrate():
    """Impose the steady form instead of waiting out a 1e5-year relaxation."""
    hill = _sync()
    if hill.incision_rate <= 0.0:
        readout.object = (
            "**No equilibrium to jump to.** A hillslope whose rivers are "
            "static or aggrading has no steady form \u2014 raise "
            "**\u03b5\u0307** above zero first.")
        return
    hill.equilibrate()
    _redraw()


def do_reset():
    sim["hill"] = Hillslope(length=LENGTH, n_nodes=N_NODES, k_u=k_u.value,
                            dz_u=dz_u.value, incision_rate=E.value * 1e-3)
    _redraw()


hill0 = sim["hill"]
profile = ColumnDataSource(data={"x": hill0.x, "z": hill0.surface()})
# The valley fill: everything below the rivers, which is where the alluvium is.
# Drawn under the profile, so a buried toe reads as a hillslope running into
# sediment rather than as a hillslope that has mysteriously gone flat.
valley = ColumnDataSource(data={"x": [0.0, LENGTH], "y1": [-1.0, -1.0],
                                "y2": [0.0, 0.0]})
steady = ColumnDataSource(data={"x": hill0.x, "z": hill0.steady_profile()})
velocity = ColumnDataSource(data={"u": [hill0.velocity_field(zeta) * 1e3]})

# Blue for material moving left, red for moving right, near-white at the
# divide where the velocity passes through zero.
mapper = LinearColorMapper(palette=_smooth_palette(RdBu11), low=-1.0, high=1.0)

fig_z = figure(height=320, width=880, title="",
               y_axis_label="Elevation above\nthe rivers [m]",
               toolbar_location=None)
fig_z.varea(x="x", y1="y1", y2="y2", source=valley,
            fill_color="#e0d3b8", fill_alpha=0.85, level="underlay")
fig_z.line("x", "z", source=steady, line_width=1, line_dash="dashed",
           color="gray", legend_label="steady form")
fig_z.line("x", "z", source=profile, line_width=3, color="black",
           legend_label="hillslope")
fig_z.x_range = Range1d(0.0, LENGTH)
fig_z.y_range = Range1d(-0.5, 10.0)      # replaced on every redraw
fig_z.legend.location = "top_left"
fig_z.legend.background_fill_alpha = 0.6

fig_u = figure(height=240, width=880, title="",
               x_axis_label="Distance across the hillslope [m]",
               y_axis_label="Depth below\nthe surface  ζ [m]",
               x_range=fig_z.x_range, toolbar_location=None)
# The depth axis runs downward: Range1d(Z_DISPLAY, 0) puts zeta = 0 at the top.
# Bokeh anchors image row 0 at the lower data coordinate, which after the flip
# is the top of the panel -- so row 0 is the surface, matching velocity_field.
fig_u.y_range = Range1d(Z_DISPLAY, 0.0)
fig_u.image(image="u", source=velocity, x=0.0, y=0.0, dw=LENGTH, dh=Z_DISPLAY,
            color_mapper=mapper)

responsive(fig_z)
responsive(fig_u)

run = animator(step)

for widget in (k_u, dz_u, E):
    widget.param.watch(lambda event: _redraw(), "value")

_redraw()

pn.Column(
    pn.pane.Markdown(
        "### Hillslope diffusivity, taken apart\n"
        "**k_hs** is the number everyone quotes and nobody measures. Here it "
        "is not a setting: you choose how fast soil creeps at the surface "
        "(**k_u**) and how quickly that motion dies away downward "
        "(**\u0394z_u**), and **k_hs = k_u \u0394z_u** is reported back.\n\n"
        "Press **\u25b6** and drag the sliders while it runs. Watch the lower "
        "panel: **k_u** and **\u0394z_u** can be traded against each other to "
        "give the same **k_hs** and the same hillslope \u2014 but not the same "
        "motion underneath it."),
    pn.Row(run, reset_button(do_reset, name="Flatten"),
           pn.widgets.Button(name="Jump to equilibrium", button_type="default",
                             on_click=lambda *a: do_equilibrate())),
    pn.Row(k_u, dz_u, sizing_mode="stretch_width", max_width=DESIGN_WIDTH),
    pn.Row(E, pn.Spacer(), sizing_mode="stretch_width", max_width=DESIGN_WIDTH),
    readout, fig_z, fig_u,
    sizing_mode="stretch_width", max_width=DESIGN_WIDTH,
).servable(title="Hillslope creep and diffusion")
