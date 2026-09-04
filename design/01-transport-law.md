# 01 -- The transport law, and its notation

## The question

The demo's premise is that hillslope diffusivity should not be *asserted*. It
should fall out of something a person can measure: how fast soil creeps at the
surface, and how quickly that motion dies away downward. What law expresses
that, what symbols does the literature already use for it, and does anything
in it need inventing?

## What the literature actually says

Nothing here needs inventing. Two independent lines converge on the same law.

**The velocity profile is measured, and it is exponential.** Deshpande,
Furbish, Arratia & Jerolmack (2021), *Nature Communications* 12:3909,
"The perpetual fragility of creeping hillslopes", write it as

```
u / u_0 = e^(-z / lambda)
```

with `z` the depth below the surface, positive downward, `u_0` the surface
velocity, and `lambda` a decay length obtained by fitting. They report field
surface velocities of order `u_0 ~ 1e-9 m/s` (about 30 mm/yr).

**The depth-integrated law is standard, and it is in Landlab.** Johnstone &
Hilley (2015), *Geology* 43(1) 83-86, doi:10.1130/G36052.1, give the flux that
this profile integrates to. It is implemented as Landlab's
`DepthDependentDiffuser`; quoting its docstring verbatim
(`landlab/components/depth_dependent_diffusion/hillslope_depth_dependent_linear_flux.py:20`):

```
q_s = K H^* (1.0 - exp[-H / H^*]) S
```

> Note that the commonly used "hillslope diffusivity" coefficient is equal to
> the product of :math:`K` and :math:`H^*`.

That note *is* this model's teaching point, already stated by the community.
The related depth-slope law of Heimsath, Furbish & Dietrich (2005), *Geology*
33(12) 949-952 -- `H q̄s = -K_h H ∇z`, with `K_h` in units of L/T -- is the
`H* → ∞` limit of the same expression.

**Not verified:** Johnstone & Hilley's own symbols. Their paper is paywalled;
the equation above is Landlab's transcription of it. Landlab's class docstring
says "Johnstone and Hilley (2014)" while its reference list says 2015 -- the
2015 *Geology* entry is the one with a DOI and is used here.

## A third, closer source: Andy's own course notes

The same law is derived independently in
Andy's Geomorphology course notes (unpublished),
§"Explicit consideration of soils in hillslope transport", from Roger Hooke's
Bevens Creek creep measurements. The notes use `k_hs`, `Δz_u` and `h_m` where
Johnstone & Hilley use `K`, `H*` and `H`. See
`docs/course-notes-provenance.md`, which also records the two corrections this
model carries over: a lost sign in the substituted flux equation, and `k_hs`
being used for two quantities that differ by one power of length.

## The decision: no bedrock, so the layer is semi-infinite

Bedrock, a finite soil thickness `H`, and weathering are all deferred (design
05). With no lower boundary the integral runs to infinity and the law loses its
saturation factor entirely:

```
u(x, zeta) = k_u * S(x) * exp(-zeta / dz_u)              [m/yr]
q_m(x)     = integral_0^inf u dzeta = k_u * dz_u * S(x)  [m2/yr]
k_hs       = k_u * dz_u                                  [m2/yr]   exactly
```

This is the cleanest possible statement of the idea: **two sliders whose
product is the diffusivity, with nothing in between them.** The cost is real
and stated here so it stays visible: without a soil thickness the model cannot
show the saturation that makes `Δz_u` interesting to a geomorphologist -- that
once `Δz_u` exceeds the soil thickness, deepening the mobile zone stops raising
`k_hs` because there is no more soil to move. That is the first thing design 05
buys back.

Verified by `probe_c`: `int(u dzeta)` matches `k_u dz_u S` to 6e-15 relative.

## Notation: the course notes' system, not any one paper's

The literature offers no single convention to defer to. One law, three papers,
three notations: Deshpande et al. write `λ` and `u_0`; Johnstone & Hilley and
Landlab write `H*` and `K`; Heimsath et al. write `K_h` and `H`. "Use the
literature name" does not name a choice here.

Worse, the obvious literature symbols are **already taken elsewhere in Andy's
course**, verified by grepping all 33 `.tex` files:

- **`D` is grain size** — `D_50`, `D_84`, `D_90` throughout the sediment-
  transport material. `05_Flow` even asks students to "find the dimensions of
  `$K$` and `$D$`."
- **A bare `$K$` is turbulent diffusivity** (26 occurrences in open-channel
  flow, replacing `μ` in the turbulent rheology). Importing Landlab's `K` — a
  *velocity* coefficient — would collide head-on with a chapter where `K` is
  already a diffusivity. That is the worst kind of collision, because both
  readings are plausible.

So the model uses the course notation. The rule applied, and worth stating
because it will recur: **defer to the literature where it is unanimous and
uncollided; use the course system otherwise, and record the reason.**

### `k_u`, the one new symbol

The notes' `k_hs` does double duty — `[L²/T]` in their Eq. `q_m`, `[L/T]` in
their Eq. `q_m_RLBH`, where it multiplies `Δz_u` (see
`docs/course-notes-provenance.md`). Code cannot carry that ambiguity, so the
velocity coefficient gets its own name. `k_u` pairs with `Δz_u` — both
subscripted for the velocity profile they describe — and it fits the notes'
existing `k_x` family (`k_a`, `k_b`, `k_s`, `k_S`, `k_ω`, `k_{ε̇}`) without
colliding with any of them. It makes the model's whole lesson readable:

```
k_hs = k_u * Δz_u
```

which is invisible in `D = K H*`.

### The symbols

| symbol | meaning | units |
|---|---|---|
| `x` | horizontal distance | m |
| `z` | surface elevation, positive up | m |
| `zeta` | depth below the land-air interface, positive down | m |
| `S` | slope, `dz/dx` | - |
| `k_u` | surface creep velocity at unit slope | m/yr |
| `dz_u` | creep e-folding depth (`Δz_u`) | m |
| `u_s` | surface creep velocity, `k_u S` | m/yr |
| `u` | `u(x, zeta) = u_s(x) exp(-zeta/dz_u)` | m/yr |
| `q_m` | depth-integrated flux of mobile material, `k_u dz_u S` | m²/yr |
| `k_hs` | hillslope diffusivity, `k_u dz_u` | m²/yr |
| `incision_rate` | river incision (`ε̇`), positive = incising | m/yr |

`zeta` is the one departure from the notes, which express the same thing as
`(z′ − z)` with `z′` the elevation of a soil parcel. Andy settled on a named
depth for this model: it is depth below the land-air interface, and that
interface is itself moving as the hill erodes, so it is a *surface-following*
coordinate and not a depth from any fixed datum. This is the convention most
likely to bite.

### Crosswalk

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


## The distinction that matters most in the code

`k_u` is *not* the surface velocity. `u_s = k_u * S(x)` varies along the hill
-- zero at the divide, largest at the toe. `k_u` is the surface velocity **at unit
slope**, and it is the slider; `u_s` is a diagnostic, and it is what the
velocity panel draws.

## Parameters chosen here

None. Every number in this document is quoted from a probe or from a cited
paper.
