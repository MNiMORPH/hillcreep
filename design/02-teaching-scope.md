# 02 -- Teaching scope

## The one idea

**Hillslope diffusivity is not a property of a hillslope. It is a shorthand for
motion you could go and measure.**

`D` is the most-used number in hillslope geomorphology and the least physical:
it is fitted to topography, quoted in m²/yr, and rarely connected to anything a
person could watch happen. This demo takes it apart. A student sets two
quantities that *are* measurable -- how fast soil creeps at the surface per unit
slope (`K`), and how fast that motion decays downward (`H*`) -- and `D = K·H*`
is reported back as a consequence, never as an input.

## What has to be honest about this

Mathematically the model is **exactly linear diffusion**, identical to
`artesian`'s existing `examples/hillslope.py`. Nothing about the evolving
topography is new. The entire contribution is that `D` is factored into two
measurable pieces and that the subsurface motion those pieces describe is drawn
on the screen. Saying otherwise would oversell it.

## The second lesson, which is the better one

`probe_b` found something not obvious enough to have been the plan: at steady
state, **the surface creep velocity does not depend on `K` at all.**

Mass balance over the upslope half requires every grain eroded above a point to
pass that point, so `q(x') = E·x'` and therefore

```
u_s(x') = E * x' / H_star
```

with `x'` the distance from the divide. Verified against the independent route
(`u_s = K·S(x)` from the steady parabola) to machine zero for
`K = 0.005, 0.02, 0.08`.

Run out over the sliders (`probe_a`), that is:

| slider moved | `D` | steady crest | surface velocity |
|---|---|---|---|
| `K`: 0.005 → 0.1 m/yr | 0.0025 → 0.05 | 25.0 → 1.25 m | **5.00 mm/yr throughout** |
| `H*`: 0.1 → 2.0 m | 0.002 → 0.04 | 31.25 → 1.56 m | 25.0 → 1.25 mm/yr |

So the two knobs are *not* interchangeable even though their product is all
that `D` sees. `K` sets **how steep the hill has to be** to carry the flux;
`H*` sets **how fast the surface actually moves**. Two hillslopes with the same
`D`, the same shape, and the same erosion rate can have surface velocities
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
is the demo's own premise working: once `D` is factored, parameter choices
become checkable against field measurements, and some of them fail.

## Scope, explicitly

In:

- one symmetric hillslope, two rivers, prescribed incision
- `K` and `H*` as the student's knobs; `E` as the forcing
- `D` displayed as a consequence
- the velocity field `u(x, zeta)` drawn beneath the surface

Out, deliberately, each with its own design doc or a line in 05:

- bedrock and finite soil thickness (05)
- soil production / weathering (05)
- rivers that aggrade and bury the hillslope toe (03, hook built, code not)
- any nonlinear or slope-threshold transport law
- two-dimensional velocity: only the downslope component is modelled
