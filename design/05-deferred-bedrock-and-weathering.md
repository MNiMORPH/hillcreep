# 05 -- Bedrock and weathering, deferred

## What is deferred, and why

Bedrock, a finite mobile soil thickness, and soil production are all out of the
first version. They add a second state variable and a second exponential
profile, and the demo's one idea (`D = K·H*`, design 02) is sharper without
them. Deferred is not declined: this document exists so the path back stays
visible and so the first version does not accidentally foreclose it.

## What the first version gives up

**The saturation.** With a finite soil thickness `H` the law regains its full
form (design 01, Johnstone & Hilley 2015 / Landlab):

```
q = K * H_star * (1 - exp(-H / H_star)) * S  =  K * H_eff * S
```

Once `H*` exceeds `H`, deepening the mobile zone stops raising `D`, because
there is no more soil to move. That is the geomorphically interesting behaviour
of `H*` and the first thing worth buying back. It also restores the two
published limits as free tests: `H* → ∞` gives Heimsath et al. (2005)
`q = K·H·S`, and `H* → 0` gives constant-`D` diffusion.

**The honest bottom of the velocity panel.** With bedrock the lower panel gets
a real floor instead of the viewing choice of design 04. Note the law still
does *not* force velocity to zero at the contact: at `H = 1 m, H* = 0.5 m` the
basal velocity is `u_s·e^(-2) = 13.5%` of the surface value. That is inherited
from Johnstone & Hilley, not introduced here, and it will need saying in the
caption because students will ask.

## What the first version must not foreclose

- `z` is the surface elevation and must stay that. Adding bedrock means adding
  `z_b` and `H = z - z_b`, not redefining `z`.
- The flux must be computed at cell **faces** in flux form. With uniform `H`
  this is identical to the constant-`D` stencil, so it costs nothing now, and
  it is the only form that survives `D` becoming a function of `x`.
- `H_star` and the future `w_star` are different depths and must never share a
  name.

## The weathering step, when it comes

Landlab's `ExponentialWeatherer`, after Ahnert (1976):

```
soil_production = w_0 * exp(-H / w_star)
```

`w_0` = `soil_production_maximum_rate`, `w_star` =
`soil_production_decay_depth`. Coupling it means `H` becomes a field evolving
as production minus flux divergence, `z_b` lowers, and `D(x) = K·H_eff(x)`
becomes spatially variable -- which is why the flux must already be in face
form.

## The parameter this will force, flagged now

Converting bedrock to soil conserves mass only with a density ratio
`rho_r / rho_s` of about 1.5-2. **Proposal:** name the constant from the
outset and set it to 1.0 while there is no weathering, so that the day it turns
on, the bookkeeping is already in the right shape rather than being retrofitted
into a working model.
