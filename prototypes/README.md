# prototypes

Throwaway executable probes, one per design decision, each written *before*
the implementation it settles.  Every number quoted in `design/` and in the
demo's comments comes from running one of these, not from arithmetic done in
prose.

Run any of them directly:

```sh
python3 prototypes/probe_a_no_bedrock_scales.py
```

| probe | question it settles | answer it gave |
|---|---|---|
| `probe_a_no_bedrock_scales.py` | What `K`, `H*`, `L` and `E` should ship as defaults? | `L = 100 m, K = 0.02 m/yr, H* = 0.5 m, E = 0.05 mm/yr` → `D = 0.01 m²/yr`, crest 6.25 m, toe slope 0.25 (14.0°), `u_s(toe) = 5.00 mm/yr` |
| `probe_b_steady_surface_velocity.py` | Is surface velocity a free parameter, i.e. is the velocity panel worth its space? | No, and yes. `u_s = E·x'/H*` at steady state, independent of `K` — verified against the parabola route to machine zero for `K = 0.005, 0.02, 0.08` |
| `probe_c_numerics_and_pacing.py` | Display depth, time step, steps per frame? | `Z_DISPLAY = 3 m`, `DT = 2.5 yr`, `STEPS_PER_FRAME = 400` → 10.2 s to steady at the defaults, measured |

`probe_c` carried a bug worth remembering: it compared absolute elevation
against a *relief* target while the river was falling, so every case ran to the
frame cap and reported "capped".  The comparison is now relative to the river
bed, and the fix is commented in place.
