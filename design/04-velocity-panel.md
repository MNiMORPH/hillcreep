# 04 -- Drawing the velocity field

## The question

The whole point of the demo is that you can see the motion under the surface.
How is it drawn, given that the motion happens over ~1 m of depth on a hill
with tens of metres of relief?

## The scale problem, with the number

At the shipped defaults (`probe_a`) the steady crest stands **6.25 m** above
base level while the creep e-folding depth is **0.5 m** -- and at Andy's course
scale the ratio is 50 m against ~1 m, i.e. **50:1**. Anything drawn to true
vertical scale beneath the surface -- profile "hairs", arrows, a shaded ribbon
-- is a smear one pixel tall. This kills the obvious renderings outright, not
by taste but by geometry.

## Decision: two stacked panels sharing an x-axis

- **Top:** topography at true vertical scale, plus the dashed steady parabola
  it is chasing.
- **Bottom:** a dedicated axis of `zeta`, depth below the land-air interface,
  running 0 at the top to `Z_DISPLAY` at the bottom, filled with a colour field
  of the signed downslope velocity `u(x, zeta)`.

A diverging palette centred on zero does the work: one hue for material moving
left, the other for material moving right, neutral at the divide where velocity
is zero, fading downward as the exponential decays. Direction and magnitude in
one mark, and no vertical exaggeration to explain because the lower panel is
not a picture of space -- it is a picture of depth below a moving surface.

The field is separable, `u(x, zeta) = u_s(x) · exp(-zeta/H_star)`, so a frame
costs one outer product. `probe_c` measured the whole step at 1.3 ms/frame in
CPython at `STEPS_PER_FRAME = 400`, well inside a 33 ms frame budget even
allowing for Pyodide being several times slower.

## Rejected

- **Hairs (velocity profiles rooted at the surface).** The classic figure, and
  the most intuitive as "material moving". Rejected because in the lower panel
  it overloads the horizontal axis: distance and velocity would share one
  direction, which students routinely misread as material moving *further* to
  the right rather than *faster*.
- **Arrows.** Legible, but bokeh's `Arrow` annotation is clumsier to update per
  frame than an image glyph, for a strictly worse encoding of magnitude.
- **One panel with the soil vertically exaggerated.** The exaggeration factor
  would have to change whenever the relief does, or the ribbon vanishes again.

Arrows remain a cheap addition *on top of* the colour field if direction turns
out to read poorly in class. That is the fallback, and it does not require
redoing anything.

## The consequence to state in the caption

With no bedrock the field never reaches a floor -- colour fades toward the
bottom of the panel but does not stop at a contact, because there is no
contact. `Z_DISPLAY` is a viewing choice, not a physical boundary, and the
caption has to say so or students will read it as the base of the soil.

## Parameters chosen here

- **Panel depth is derived from the model's own depth scale, not hand-picked.**
  Andy's correction: how deep to draw depends on the scale of the model, so a
  bare number in metres is the wrong kind of constant -- it silently stops
  being right the moment the model is rescaled. The rule differs between the
  two renderings, for a reason:

  - **The static figure** has a single `H*`, so it follows that `H*` directly:
    `ZETA_EFOLDINGS = 4.0`, i.e. `Z_DISPLAY = 4 H*`. The panel then looks the
    same at every scale and always shows `1 - e^-4 = 98.2%` of the flux.
  - **The interactive demo** cannot do that: an axis derived from the *current*
    `H*` would move while a student drags the slider, destroying exactly the
    comparison the panel exists to support. It uses the slider's upper bound
    instead, `Z_DISPLAY = Z_DISPLAY_IN_HSTAR_MAX * HS_MAX`, which still follows
    a rescaled model but never moves during use.

  `Z_DISPLAY_IN_HSTAR_MAX = 1.0` is *a proposal*, and the one number left to
  taste. At 1.0 the deepest slider setting fills the panel and shows 63.2% of
  the flux while the default `H* = 0.5 m` keeps its motion in the top quarter;
  at 1.5 the deepest shows 77.7% and the default is squeezed into the top
  sixth. Flux fractions from `probe_c`.
- **Colour scale fixed to ±`E L / (2 H*)`**, the *steady* surface velocity at
  the toe. *A proposal.* This depends only on the sliders, so it does not
  flicker frame to frame, and the colours saturate as the hill approaches its
  steady form -- a useful signal in itself. When `E = 0` there is no steady
  velocity to scale by and the present profile is used instead.

  (As first written this bullet said "fixed to the steepest point of the
  current state, rather than renormalised per frame", which is a
  contradiction: the current state *is* the frame. Corrected when the app was
  implemented against it.)

- **Elevation axis tracks the steady crest** `E L² / (8 D)` for the current
  sliders, at 1.18×. *A proposal.* A fixed axis cannot serve these sliders:
  the steady crest spans 1.25 m to 50 m over their ranges, a factor of 40, so
  any one choice either clips the tall cases or draws the short ones as a flat
  line. Found by rendering the app, not by reasoning about it.
