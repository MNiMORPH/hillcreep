# 06 -- Steep slopes and mass wasting, deferred

## The known issue

The three sliders are each bounded so that no one of them alone produces an
indefensible hillslope, but they can be *combined* into one. From `probe_a`:
`E = 0.10 mm/yr` with `H* = 0.25 m` and `K = 0.02 m/yr` gives a steady toe slope
of 1.0 -- 45 degrees. A linear creep law has no business there. Real hillslopes
approaching a critical gradient stop behaving diffusively: transport diverges,
and material leaves by landsliding rather than by creeping.

Nothing clamps the sliders and nothing warns. That is deliberate, and Andy's
call: **left as a known issue, with mass wasting as the eventual answer rather
than a guard rail.**

## Why a warning is the wrong fix

A warning would tell a student that the model has stopped being trustworthy
without telling them anything about hillslopes. The physical answer is that a
steep hillslope *does something else*, and that something else is a process
worth teaching. Adding a threshold now would occupy the place the real
mechanism should take, and would have to be removed again when it arrives.

## What arriving would look like

Two routes, not mutually exclusive:

- **A nonlinear transport law.** Replace `u_s = K S` with a form that diverges
  as the slope approaches a critical value -- Roering et al.'s
  `1/(1 - (S/S_c)^2)`, or the exponential creep-fragility form from Jerolmack's
  group. Flanks become planar rather than parabolic, and the analytic steady
  parabola that this demo uses as a live check curve goes away. That loss is
  the main cost, and it is why `design/02` put a nonlinear law out of scope for
  the first version.
- **Explicit landsliding.** Leave the creep law linear and add a separate
  failure rule that removes material once a threshold gradient is exceeded.
  Keeps the parabola valid wherever the hill is below threshold, and separates
  the two processes visibly -- which suits a teaching model better than folding
  them into one coefficient.

The second is the better fit for this model's purpose, but that is a judgement
and not a decision. Neither is scheduled.

## Until then

The steep corner of the slider space is reachable and gives a hillslope that
would not exist. Recorded in `CHANGELOG.md` under known gaps and in `FRAME.md`
section (e), so it stays visible rather than being quietly assumed away.
