# hillcreep

Project-scoped notes. Global standing instructions live in `~/.claude/CLAUDE.md`;
this file holds only what is specific to *this* model.

## Commands

```sh
pip install -e ".[test]"    # from a clone; needs setuptools>=77.0.3, so do NOT
                            # pass --no-build-isolation (the system setuptools
                            # rejects the PEP 639 `license` string)
pytest                      # the whole suite
python3 prototypes/probe_a_no_bedrock_scales.py     # any probe runs directly
artesian build interactive_demo/hillcreep_panel.py -o _artesian_build \
    -p . -p ../artesian -r numpy --serve
```

`artesian build` runs the app in the *building* environment to discover what it
serves, so `hillcreep` must be importable here, not merely wheeled for the
browser. `pip install -e .` first or the build fails with a bare
`ModuleNotFoundError`.

## Conventions

These are assumed silently by every routine, so an unstated one becomes a bug
that looks like a result. Change one only deliberately, and grep for what
depends on it.

- **Notation is the course notes' system**, not any one paper's: `k_hs`,
  `k_u`, `Δz_u`, `q_m`, and the deferred `h_m`, `z_r`, `w_0`, `δz_w`, `ρ_m/ρ_r`.
  `k_u` is the only new symbol — the notes' `k_hs` doubles for both the
  `[L²/T]` diffusivity and the `[L/T]` velocity coefficient, and code cannot
  carry that. Never import `D` or `K` from the literature: in this course `D`
  is grain size and `K` is turbulent diffusivity. Crosswalk in `README.md`.
- **Units**: metres and **years**. Not seconds — hillslope diffusivity is quoted
  in m²/yr everywhere in this literature, and the course scripts this grew from
  use years. Millimetres per year appear only at the slider and label edges, and
  the `1e-3` conversion is named where it happens.
- **`z` is elevation, positive up.** As in Landlab (`topographic__elevation`)
  and in Andy's course scripts.
- **`zeta` is depth below the land–air interface, positive down.** It is a
  *surface-following* coordinate: the interface moves as the hill erodes, so
  `zeta` is not a depth from any fixed datum. Deshpande et al. (2021) call this
  `z` and the course notes express it as `(z′ − z)`; naming it is deliberate and
  is the convention most likely to bite.
- **`k_u` is not the surface velocity.** `k_u` is the surface creep velocity at
  *unit slope* [m/yr]; the actual surface velocity `u_s = k_u·S(x)` varies along
  the hill and is a diagnostic, not a parameter.
- **`k_hs` is a read-only property.** If anything ever assigns a diffusivity, the
  model has lost its reason to exist.
- **`ε̇` is positive for incision**, matching `zdot_channel` in the 2013 course
  script. Negative aggrades.
- **Flux lives on faces; elevation lives on nodes.** With `k_u` and `Δz_u` uniform
  the face form is identical to the node-centred second difference, so it costs
  nothing today. It is the only form that survives `k_hs` becoming a function of
  `x` when soil thickness arrives, and `test_face_form_flux_matches_the_
  constant_diffusivity_stencil` is what lets that be claimed for free.
- **`np.gradient` needs `edge_order=2`.** The default first-order one-sided
  difference is not exact for a quadratic and biases the toe velocity low by
  1% — at exactly the nodes the demo draws attention to.
- **Boundaries are written in one place only**, `Hillslope.apply_boundaries()`,
  so that aggradation onlap can be added without touching the solver.

## Layout

- `src/hillcreep/hillslope.py` — the model: state, the transport law, stepping.
- `design/` — a design document per decision, written *before* the code.
- `prototypes/` — throwaway executable probes that settle a design question.
- `tests/` — one test per claim; the test name states the claim.
- `examples/` — runnable scripts and rendered previews, meant to be read.
- `interactive_demo/` — the artesian browser app.

## Working rules for this repo

- A design decision gets a `design/*.md` and a runnable probe in `prototypes/`
  **before** the implementation. If `prototypes/` is empty while `src/` is
  growing, that step is being skipped.
- **Every number in prose is pasted probe output**, never arithmetic done in
  a document. `prototypes/README.md` indexes which probe produced what.
- Any threshold, cut-off, filter, or default not asked for is a proposal. Say
  it in one sentence; do not implement it silently. The live ones are listed in
  `FRAME.md`.
- A regression test must be shown to fail without its fix.
- **Render the figure before believing the plotting code.** Two real defects
  here — a palette seam landing exactly on the drainage divide, and an
  elevation axis that could not span the slider range — were invisible in the
  source and obvious in the image.
