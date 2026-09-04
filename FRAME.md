# Frame -- read this first

The read-first frame for this repo, per `~/.claude/COMPACTION_PLAYBOOK.md`.
After a compaction, read this **before** acting, and verify every structural
claim below against git and disk before trusting it. Current to `b78e87b`.

## (a) Origin -- why this model exists

To teach one idea: **hillslope diffusivity is not a property of a hillslope, it
is a shorthand for motion you could go and measure.** `D` is fitted to
topography and quoted in m²/yr, and almost never connected to anything a person
could watch happen. Here a student sets two measurable quantities -- the surface
creep velocity at unit slope `K`, and the e-folding depth `H*` over which that
motion decays -- and `D = K H*` is reported back as a consequence.

It grew from Andy's 2013 course script,
`~/Dropbox/Courses/Computational-Methods-in-Earth-Sciences/code/Numerical/hillslope_diffusion_no_matrix.py`,
which solves the same equation with `D` asserted.

Delivery is an interactive browser demo built with
[artesian](https://github.com/MNiMORPH/artesian), which constrains the model: it
must run under Pyodide, so numpy only, nothing compiled, and fast enough to press
Run. **Verified, not assumed:** `artesian check numpy` reports it bundled by
Pyodide, and the compiled build has been loaded in headless Chrome and run --
see `examples/browser_running.png`.

## (b) Plan and trajectory -- as the next action

1. **Two parameter proposals are waiting on Andy** (see (e)); neither blocks
   anything.
2. **Next: decide whether bedrock comes back**, per
   `design/05-deferred-bedrock-and-weathering.md`. Andy dropped it deliberately
   to keep `D = K H*` exact. The cost is that `H*` cannot do the one thing that
   makes it geomorphically interesting -- saturate once it exceeds the soil
   thickness. This is the largest open design question.
3. Aggradation onlap: the hook is built (`River` objects, `active` mask, one
   `apply_boundaries()`), the code is not written. `apply_boundaries()` raises
   `NotImplementedError` rather than misbehaving quietly.
4. Weathering, after bedrock. Landlab's `ExponentialWeatherer` form; the
   density ratio `rho_r/rho_s` should be named before it is needed.
5. Not yet done: no git remote, nothing pushed, no `docs/`, and the demo is not
   embedded in any course page.

## (c) Key current data and objects

Branch `master`, HEAD `b78e87b`, **everything unpushed** (there is no remote).
`hillcreep` is `pip install -e`-installed into `~/.local` with
`--break-system-packages`, matching how `artesian` and `corestone` are installed
on this machine.

- `src/hillcreep/hillslope.py` -- **the model**. `Hillslope` and `River`.
  `Hillslope.diffusivity` is a read-only property returning `K * H_star`.
- `interactive_demo/hillcreep_panel.py` -- the artesian demo. Two stacked
  bokeh panels sharing an x-axis; sliders `K`, `H*`, `E`.
- `examples/figure_two_panel.py` -- the same figure in matplotlib,
  parameterised: `--K --H-star --E --length --kyr --out`.
- `prototypes/probe_[a-c]_*.py` -- the evidence behind every quoted number.
  `prototypes/README.md` indexes which probe produced what.
- `design/01`-`design/05` -- one document per decision, each written before
  its code.
- `tests/` -- 13 tests, all passing, one claim each.

## (d) Results, with the method that verified them

- **`D = K H*`, and the amplitude slider does not change steady surface
  velocity.** `u_s(x') = E x' / H*` by mass balance. Verified two independent
  ways (mass balance vs. the steady parabola) agreeing to machine zero for
  `K = 0.005, 0.02, 0.08`:
  `python3 prototypes/probe_b_steady_surface_velocity.py`, and as
  `test_steady_surface_velocity_does_not_depend_on_K`.
- **Shipped defaults** `L = 100 m, K = 0.02 m/yr, H* = 0.5 m, E = 0.05 mm/yr`
  give `D = 0.01 m²/yr`, crest 6.25 m, toe slope 0.25 (14.0°), `u_s` at the toe
  5.00 mm/yr, relaxation 1.01e5 yr.
  `python3 prototypes/probe_a_no_bedrock_scales.py`.
- **The 2013 course parameters imply 200 mm/yr of surface creep** -- one to two
  orders above measured soil creep. Same probe. This is the demo's premise
  working, not a criticism of a script that never claimed a creep profile.
- **Pacing, measured not guessed:** `STEPS_PER_FRAME = 400` reaches 95% of the
  steady crest in 307 frames (10.2 s at 30 fps) at the defaults, 1228 frames
  (40.9 s) at the slowest slider corner, 31 frames (1.0 s) at the fastest;
  1.3 ms/frame in CPython. `python3 prototypes/probe_c_numerics_and_pacing.py`.
- **The compiled demo runs.** `artesian build ... -p . -p ../artesian -r numpy`,
  then loaded in headless Chrome: reaches steady state, no console errors, and
  reports a toe velocity of 5.00 mm/yr -- matching the analytic `E L / (2 H*)`
  through the WASM build, independently of the Python tests.

### Negative results and dead ends, so they are not re-walked

- **Hairs, arrows and an exaggerated soil ribbon are all unusable** for drawing
  the velocity at true scale: the crest is 6.25 m against a 0.5 m e-folding
  depth, and 50:1 at the course scale. Rejected on geometry in `design/04`.
- **`bokeh.palettes.diverging_palette(Blues256, Reds256)` has a seam at its
  midpoint** -- which on this figure is the drainage divide. Replaced with an
  interpolated ColorBrewer RdBu.
- **A fixed elevation axis cannot serve these sliders**: the steady crest spans
  1.25 m to 50 m across their ranges.
- **`np.gradient` default `edge_order=1`** is not exact for a quadratic and
  biased the toe velocity low by 1%. Fixed; the fix is shown to be load-bearing
  by reverting it and watching two tests fail.
- **`pip install -e . --no-build-isolation` fails**: the system setuptools
  predates PEP 639 and rejects the `license` string.

## (e) Parameters chosen but not asked for -- proposals, still open

1. **`Z_DISPLAY = 3.0 m`**, the depth shown in the velocity panel, fixed rather
   than scaled to `H*`. Holds 99.8% of the flux at the default `H*` and 77.7%
   at the largest. At the default it leaves the lower two-thirds of the panel
   nearly empty; `2.0 m` would fill it better and still hold 98.2%. Surfaced to
   Andy; not yet decided.
2. **Slider ranges** `K ∈ [0.01, 0.05]`, `H* ∈ [0.25, 2.0]`, `E ∈ [-0.05, 0.10]`
   mm/yr, bounded above by steepness -- `E = 0.2 mm/yr` at the default `K` and
   `H*` gives a 45° toe slope, outside where a linear creep law is defensible.
   Note the ranges can still be *combined* into steep states; nothing clamps
   them and nothing warns.
3. **Colour scale** fixed to the steady toe velocity `E L / (2 H*)`; **elevation
   axis** to 1.18× the steady crest. Both depend only on the sliders, so neither
   rescales frame to frame.
4. **`rho_r/rho_s` is not yet named anywhere.** It will be needed the moment
   weathering exists; `design/05` proposes naming it now and setting it to 1.0.

## (f) Guardrails

- Nothing has been pushed, tagged, or released, and there is no remote. Every
  one of those needs explicit authorisation in the message that asks for it.
- `D` must never become assignable.
- Every number in prose is pasted probe output. If a number cannot be traced to
  a probe or a cited paper, it does not go in.
