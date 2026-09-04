# 02 -- Teaching scope

## The one idea

**Hillslope diffusivity is not a property of a hillslope. It is a shorthand for
motion you could go and measure.**

`k_hs` is the most-used number in hillslope geomorphology and the least physical:
it is fitted to topography, quoted in m²/yr, and rarely connected to anything a
person could watch happen. This demo takes it apart. A student sets two
quantities that *are* measurable -- how fast soil creeps at the surface per unit
slope (`k_u`), and how fast that motion decays downward (`Δz_u`) -- and
`k_hs = k_u·Δz_u`
is reported back as a consequence, never as an input.

## What has to be honest about this

Mathematically the model is **exactly linear diffusion**, identical to
`artesian`'s existing `examples/hillslope.py`. Nothing about the evolving
topography is new. The entire contribution is that `k_hs` is factored into two
measurable pieces and that the subsurface motion those pieces describe is drawn
on the screen. Saying otherwise would oversell it.

## The second lesson, which is the better one

`probe_b` found something not obvious enough to have been the plan: at steady
state, **the surface creep velocity does not depend on `k_u` at all.**

Mass balance over the upslope half requires every grain eroded above a point to
pass that point, so `q(x') = E·x'` and therefore

```
u_s(x') = ε̇ * x' / Δz_u
```

with `x'` the distance from the divide. Verified against the independent route
(`u_s = K·S(x)` from the steady parabola) to machine zero for
`K = 0.005, 0.02, 0.08`.

Run out over the sliders (`probe_a`), that is:

| slider moved | `k_hs` | steady crest | surface velocity |
|---|---|---|---|
| `k_u`: 0.01 → 0.05 m/yr | 0.001 → 0.005 | 12.5 → 2.5 m | **5.00 mm/yr throughout** |
| `Δz_u`: 0.03 → 0.20 m | 0.0006 → 0.004 | 20.8 → 3.13 m | 16.7 → 2.5 mm/yr |

So the two knobs are *not* interchangeable even though their product is all
that `k_hs` sees. `k_u` sets **how steep the hill has to be** to carry the flux;
`Δz_u` sets **how fast the surface actually moves**. Two hillslopes with the same
`k_hs`, the same shape, and the same erosion rate can have surface velocities
differing by 20×. Only the lower panel can show that, which is what justifies
its space.

## The anomaly worth showing a class

Andy's 2013 course script uses `k = 5e-3` with `dx = 10 m`, i.e. an effective
`D = k·dx² = 0.5 m²/yr`, on a 1 km hillslope incising at 0.2 mm/yr. Factored
through this transport law (`probe_a`), those parameters imply a **surface
creep velocity of 200 mm/yr** -- one to two orders of magnitude above measured
soil creep. The numbers were chosen so the hill relaxes in 400 kyr, and they
do; they are simply not consistent with a creep profile anyone has measured.

This is not a criticism of the script, which never claimed a creep profile. It
is the demo's own premise working: once `k_hs` is factored, parameter choices
become checkable against field measurements, and some of them fail.

## Scope, explicitly

In:

- one symmetric hillslope, two rivers, prescribed incision
- `k_u` and `Δz_u` as the student's knobs; `ε̇` as the forcing
- `k_hs` displayed as a consequence
- the velocity field `u(x, zeta)` drawn beneath the surface

Out, deliberately, each with its own design doc or a line in 05:

- bedrock and finite soil thickness (05)
- soil production / weathering (05)
- rivers that aggrade and bury the hillslope toe (03, hook built, code not)
- any nonlinear or slope-threshold transport law
- two-dimensional velocity: only the downslope component is modelled
