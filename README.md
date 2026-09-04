# hillcreep

**Hillslope diffusivity, taken apart.**

`k_hs` is the most-quoted number in hillslope geomorphology and among the least
physical: fitted to topography, reported in m²/yr, and rarely connected to
anything anyone could watch happen. This model does not accept it as an input.
You set two quantities that *are* measurable — how fast soil creeps at the
surface per unit slope, and how quickly that motion dies away with depth — and
the diffusivity comes out the other end.

```
u(x, ζ)  = -k_u ∂z/∂x · exp(-ζ / Δz_u)     downslope creep velocity
q_m(x)   = ∫₀^∞ u dζ = -k_u Δz_u ∂z/∂x     depth-integrated flux
k_hs     = k_u Δz_u                         reported, never set
```

`ζ` is depth below the land–air interface, positive downward. The interface
itself is moving: the hill is eroding.

## The two lessons

**`k_hs = k_u Δz_u`.** Two knobs whose product is the diffusivity. Landlab's
`DepthDependentDiffuser` says the same thing in its own docstring — "the
commonly used 'hillslope diffusivity' coefficient is equal to the product of K
and H\*" — so this is the community's law, not a new one. What is new here is
that you can see the motion it summarises.

Notation follows Andy's Geomorphology course notes, not any one paper: the
literature has three notations for this one law, and its obvious symbols are
already taken in the course (`D` is grain size, `K` is turbulent diffusivity).
The crosswalk is below.

**Surface velocity is not yours to choose.** At steady state, every grain
eroded above a point must pass that point, so `q(x') = E x'` and

```
u_s(x') = ε̇ x' / Δz_u          no k_u in it
```

Move `k_u` across its whole range and the diffusivity changes 20-fold, the hill
gets 20 times flatter — and the surface creep velocity does not move at all.
Move `Δz_u` and everything changes together. Two hillslopes with the same `k_hs`,
the same shape and the same erosion rate can differ 20-fold in how fast their
surfaces are actually moving. That is what the lower panel is for.

![the compiled demo running](examples/browser_running.png)

## Install and run

```sh
pip install -e ".[test]"     # from a clone
pytest                       # 13 tests, one per claim
```

```python
from hillcreep import Hillslope

hill = Hillslope(length=100., k_u=0.02, dz_u=0.10, incision_rate=0.01e-3)
hill.run(3.0e5)                       # years

hill.k_hs                             # 0.002 m2/yr  = k_u * dz_u
hill.equilibrate()                    # impose the steady form directly

hill.incision_rate = -0.01e-3         # rivers aggrade instead
hill.run(6.0e4)
hill.exposed_length                   # m of hillslope not yet buried

hill.incision_rate = 0.05e-3          # rivers cut back down
hill.run(1.0e4)                       # the fill is left as a terrace
hill.surface_velocity()               # m/yr at each node, signed
hill.velocity_field(zeta)             # the field the diffusivity summarises
```

## The browser demo

Compiled to WebAssembly with [artesian](https://github.com/MNiMORPH/artesian),
so it runs in the reader's browser with no server:

```sh
pip install -e ".[demo]"
artesian build interactive_demo/hillcreep_panel.py -o _artesian_build \
    -p . -p ../artesian -r numpy --serve
```

`artesian build` runs the app in *this* environment to discover what it serves,
so `hillcreep` must be installed here, not merely wheeled for the browser.

## Defaults, and where they come from

| | value | |
|---|---|---|
| `L` | 100 m | hillslope width |
| `k_u` | 0.02 m/yr | surface creep velocity at unit slope |
| `Δz_u` | 0.10 m | creep e-folding depth, from Hooke's Bevens Creek profiles |
| `ε̇` | 0.01 mm/yr | river incision rate, **forced** by `u_s = ε̇L/2Δz_u` |
| → `k_hs` | 0.002 m²/yr | |
| → crest | 6.25 m | above base level, at steady state |
| → toe slope | 0.25 (14.0°) | |
| → `u_s` at the toe | 5.00 mm/yr | measurable, and measured |

Every one of those numbers is output from
`prototypes/probe_a_no_bedrock_scales.py`, not arithmetic done in prose.

They are deliberately **not** the parameters of the course script this model
grew out of. That script uses an effective `k_hs = 0.5 m²/yr` on a 1 km hillslope,
which — factored through this transport law — implies a surface creep velocity
of 200 mm/yr, one to two orders above anything measured. The script never
claimed a creep profile, so this is not a criticism of it; it is the premise of
this model working. Once `k_hs` is factored, parameter choices become checkable,
and some of them fail.

The same check caught one of my own. An earlier version of this model shipped
`Δz_u = 0.5 m`, anchored on Landlab's `soil_transport_decay_depth` default of
1.0 m — which is a placeholder in a function signature, not a measurement.
Roger Hooke's Bevens Creek profiles put the whole soil at 0.42 m with motion in
the top 5–15 cm, so 0.5 m was deeper than the soil it was supposed to describe.
Correcting it moved the predicted surface creep from 5 mm/yr onto the measured
range, and `k_hs` fell from 0.01 to 0.002 m²/yr — which is what it should do,
since `k_hs` is a result here and not an input.

## What this model does not do

No bedrock, no soil thickness, no weathering. Consequently it cannot show the
saturation of `k_hs` once `Δz_u` exceeds the mobile soil thickness, which is
the behaviour that makes `Δz_u` interesting to a geomorphologist. The path back
is kept open and written down in `design/05-deferred-bedrock-and-weathering.md`;
the flux is already computed on cell faces so that `k_hs` can become a function
of `x` without the solver being rewritten.

Alluvium does not creep: once buried, ground stops moving entirely, where a
real valley fill has transport of its own. And no sediment volume is tracked —
the alluvial surface is a level, which is enough to move the hillslope's
boundary but means mass is not conserved within the hillslope. It should not
be: the river delivers material from outside it.

## Layout

- `src/hillcreep/` — the model.
- `design/` — one document per decision, written *before* the code.
- `prototypes/` — the runnable probe that settled each decision, and its output.
- `tests/` — one test per claim; the test name states the claim.
- `examples/` — the static figure, and rendered previews.
- `interactive_demo/` — the `artesian` browser app.

## Notation crosswalk

| this model | course notes | Johnstone & Hilley / Landlab | Deshpande et al. | Heimsath et al. |
|---|---|---|---|---|
| `k_hs` hillslope diffusivity [m²/yr] | `k_hs` | `K·H*` / `linear_diffusivity` | – | linear diffusivity |
| `k_u` surface velocity at unit slope [m/yr] | `k_hs`, overloaded | `K` / `soil_transport_velocity` | – | `K_h` |
| `dz_u` creep e-folding depth [m] | `Δz_u` | `H*` / `soil_transport_decay_depth` | `λ` | – |
| `q_m` depth-integrated flux [m²/yr] | `q_m` | `q_s` / `soil__flux` | – | `H q̄_s` |
| `u_s` surface creep velocity [m/yr] | `u` at the surface | – | `u₀` | – |
| `zeta` depth below the surface [m] | `−(z′ − z)` | – | `z` | – |
| `incision_rate` [m/yr] | `ε̇` | – | – | – |
| *deferred:* soil thickness | `h_m` | `H` / `soil__depth` | – | `H` |
| *deferred:* rock surface | `z_r` | `bedrock__elevation` | – | – |
| *deferred:* weathering | `w_0`, `δz_w`, `ρ_m/ρ_r` | `soil_production_*` | – | `ε(H)` |

Why the course notation and not the literature's: there is no single literature
convention for this law, and its obvious symbols are taken. Full reasoning in
`design/01-transport-law.md`; the model's derivation lineage, including the two
corrections it carries over from the notes, is in
`docs/course-notes-provenance.md`.

## References

Deshpande, N.S., Furbish, D.J., Arratia, P.E., and Jerolmack, D.J., 2021,
The perpetual fragility of creeping hillslopes: *Nature Communications*, v. 12,
3909, [doi:10.1038/s41467-021-23979-z](https://doi.org/10.1038/s41467-021-23979-z).

Heimsath, A.M., Furbish, D.J., and Dietrich, W.E., 2005, The illusion of
diffusion: Field evidence for depth-dependent sediment transport: *Geology*,
v. 33, p. 949–952, [doi:10.1130/G21868.1](https://doi.org/10.1130/G21868.1).

Johnstone, S.A., and Hilley, G.E., 2015, Lithologic control on the form of
soil-mantled hillslopes: *Geology*, v. 43, p. 83–86,
[doi:10.1130/G36052.1](https://doi.org/10.1130/G36052.1).
