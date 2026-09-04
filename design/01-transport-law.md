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
`~/Dropbox/Courses/Geomorphology/02-hillslopes/02_03_Hillslopes_2022.tex`,
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
u(x, zeta) = K * S(x) * exp(-zeta / H_star)        [m/yr]
q(x)       = integral_0^inf u dzeta = K * H_star * S(x)   [m2/yr]
D          = K * H_star                             [m2/yr]   exactly
```

This is the cleanest possible statement of the idea: **two sliders whose
product is the diffusivity, with nothing in between them.** The cost is real
and stated here so it stays visible: without a soil thickness the model cannot
show the saturation that makes `H*` interesting to a geomorphologist -- that
once `H*` exceeds the soil thickness, deepening the mobile zone stops raising
`D` because there is no more soil to move. That is the first thing design 05
buys back.

Verified by `probe_c`: `int(u dzeta)` matches `K H_star S` to 6e-15 relative.

## Notation

`z` keeps its usual meaning -- elevation, positive up -- as in Landlab and in
Andy's own course scripts. Deshpande et al.'s depth-below-surface `z` is
therefore renamed `zeta`. It is a **surface-following** coordinate: depth below
the land-air interface, which is itself moving downward as the hill erodes, not
a depth from any fixed datum.

| symbol | meaning | units | source |
|---|---|---|---|
| `x` | horizontal distance | m | |
| `z` | surface elevation, positive up | m | Landlab `topographic__elevation` |
| `zeta` | depth below the land-air interface, positive down | m | Deshpande et al.'s `z` |
| `S` | slope, `dz/dx` | - | |
| `K` | soil transport velocity coefficient | m/yr | Landlab `soil_transport_velocity`; Heimsath et al. `K_h` |
| `H_star` | creep e-folding depth | m | Landlab `soil_transport_decay_depth`; Deshpande et al. `lambda` |
| `u_s` | surface creep velocity, `K*S` | m/yr | Deshpande et al. `u_0` |
| `u` | `u(x, zeta) = u_s(x) * exp(-zeta/H_star)` | m/yr | |
| `q` | depth-integrated flux, `K*H_star*S` | m²/yr | Landlab `soil__flux` |
| `D` | hillslope diffusivity, `K*H_star` | m²/yr | **displayed, never set** |
| `E` | river incision rate, positive = incising | m/yr | Andy's `zdot_channel` |

Three deliberate departures, each with a reason:

- **`u_s`, not Deshpande's `u_0`.** In a time-stepping model `u_0` reads as
  "value at t = 0".
- **`H_star`, not `lambda`.** `lambda` is a Python keyword, Landlab and
  Johnstone & Hilley use `H*`, and it pairs with `w_star` when weathering
  arrives.
- **`zeta`, not `z`.** See above. This is the convention most likely to bite.

## The distinction that matters most in the code

`K` is *not* the surface velocity. `u_s = K * S(x)` varies along the hill --
zero at the divide, largest at the toe. `K` is the surface velocity **at unit
slope**, and it is the slider; `u_s` is a diagnostic, and it is what the
velocity panel draws.

## Parameters chosen here

None. Every number in this document is quoted from a probe or from a cited
paper.
