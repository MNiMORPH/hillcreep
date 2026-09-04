# 05 -- Bedrock and weathering, deferred

## Status: decided, not merely postponed

**Andy's call, confirmed: no bedrock.** This is settled rather than pending, and
should not be reopened as an oversight. The document stays because the *cost*
below is real and needs to remain visible, and because the path back must not be
foreclosed by anything written in the meantime.

## What is deferred, and why

Bedrock, a finite mobile soil thickness, and soil production are all out of the
first version. They add a second state variable and a second exponential
profile, and the demo's one idea (`k_hs = k_u·Δz_u`, design 02) is sharper without
them. Deferred is not declined: this document exists so the path back stays
visible and so the first version does not accidentally foreclose it.

## What the first version gives up

**The saturation.** With a finite soil thickness `h_m` the law regains its full
form (design 01, Johnstone & Hilley 2015 / Landlab):

```
q_m = k_u * Δz_u * (1 - exp(-h_m / Δz_u)) * S  =  k_u * Δz_eff * S
```

Once `Δz_u` exceeds `h_m`, deepening the mobile zone stops raising `k_hs`, because
there is no more soil to move. That is the geomorphically interesting behaviour
of `Δz_u` and the first thing worth buying back. It also restores the two
published limits as free tests: `Δz_u → ∞` gives Heimsath et al. (2005)
`q_m = k_u·h_m·S`, and `Δz_u → 0` gives constant-`k_hs` diffusion.

**The honest bottom of the velocity panel.** With bedrock the lower panel gets
a real floor instead of the viewing choice of design 04. Note the law still
does *not* force velocity to zero at the contact: at `h_m = 1 m, Δz_u = 0.5 m` the
basal velocity is `u_s·e^(-2) = 13.5%` of the surface value. That is inherited
from Johnstone & Hilley, not introduced here, and it will need saying in the
caption because students will ask.

## What the first version must not foreclose

- `z` is the surface elevation and must stay that. Adding bedrock means adding
  `z_r` and `h_m = z - z_r`, not redefining `z`.
- The flux must be computed at cell **faces** in flux form. With uniform `h_m`
  this is identical to the constant-`k_hs` stencil, so it costs nothing now, and
  it is the only form that survives `k_hs` becoming a function of `x`.
- `Δz_u` and the future `δz_w` are different depths and must never share a
  name.

## The weathering step, when it comes

Landlab's `ExponentialWeatherer`, after Ahnert (1976):

```
w = w_0 * exp(-h_m / δz_w)
```

The notes use exactly these symbols; Landlab calls them
`soil_production_maximum_rate` and `soil_production_decay_depth`. Coupling it means `h_m` becomes a field evolving
as production minus flux divergence, `z_r` lowers, and `k_hs(x) = k_u·Δz_eff(x)`
becomes spatially variable -- which is why the flux must already be in face
form.

## The parameter this will force

Converting bedrock to soil conserves mass only with a density ratio
`ρ_m/ρ_r` of about 1.5-2. Andy has confirmed this is needed.

It is **recorded here and deliberately not written into the code yet.** With no
bedrock there is nothing for it to convert, so a named constant fixed at 1.0
would be dead code -- a parameter that appears in the source, participates in
nothing, and reads to anyone else as though the model accounts for a density
contrast it has never seen. The commitment is that it goes in *with* the first
line of bedrock, not after the model is already working without it.
