# A method for revising the course notation

Written at Andy's request, after the notation work on this model surfaced
concrete evidence about the state of his Geomorphology notes. He has said the
notes can wait; this records the method while it is fresh, so that when they
come up the thinking does not have to be redone.

Everything below is grounded in what actually happened building `hillcreep`,
not in general advice about writing.

---

## The situation, measured

Not remembered — counted, on 2026-09-04, by grepping every `.tex` under
`~/Dropbox/Courses/Geomorphology` (33 files, ~10,479 lines, excluding `2016/`):

- **Not under version control.** No git repository.
- **Five chapters have year-suffixed duplicates** (`01_Surveying_Lab_Assignment`,
  `02_03_Hillslopes`, `05-field-data-flow-problem-set`, `05_Flow`,
  `RainfallRunoffGame`), so "which file is canonical" is unanswered.
- **The site serves a stale build.** `geomorphonline.github.io/schedule/` week 4
  links `/assets/notes/02_03_Hillslopes.pdf`, not the 2022 revision.

## The system is already there, and it is good

The notes have a real notational grammar. It is nowhere written down, but it
can be read off the corpus:

| pattern | meaning | instances found |
|---|---|---|
| `k_x` | a coefficient, subscript naming what it scales | `k_hs`, `k_a`, `k_b`, `k_s`, `k_S`, `k_{Sn}`, `k_m`, `k_ω`, `k_{ε̇}` |
| `Δz_x` / `δz_x` | a length scale of process `x` | `Δz_u` (creep), `δz_w` (weathering) |
| `ẋ_p` | a rate, subscript naming the process | `ż_q`, `ż_a`, `ż_w`, `ż_d`, `ḣ_m`, `ε̇` |
| material subscripts | `m` mobile, `r` rock, `w` water | `h_m`, `q_m`, `z_r`, `ρ_m`, `ρ_r`, `ρ_w` |

**This grammar is why the notes work.** It is precisely what let `D` stay grain
size and `K` stay turbulent diffusivity without ambiguity — two symbols the
hillslope literature would otherwise have claimed. A revision should sharpen
this system, not replace it.

## The flaws are specific and findable

Found without looking for them, while doing something else:

1. **`k_s` and `k_S` differ only by letter case** and coexist in
   `06_rivers.tex` — Nikuradse roughness height (`k_s = nD`, `[L]`) against the
   steepness index — with `k_{Sn}` alongside. Dangerous spoken aloud, on a
   board, or skimmed.
2. **`k_hs` carries two dimensions** in the hillslope chapter: `[L²/T]` in
   Eq. `q_m`, `[L/T]` in Eq. `q_m_RLBH` where it multiplies `Δz_u`.
3. **`δz_w` against `Δz_u`** — the same kind of quantity, different Greek.
4. **`ż` and `ḣ_m` mixed across one equation's two sides.**
5. **The `h` family is crowded**: flow depth `h`, `h_m`, `h_bf`, `h_w`.

## The method

### 0. A clean repository, not a `git init` in place

Andy's objection to `git init` is correct: the directory is too messy, and
committing that mess is not a baseline, it is a photograph of a mess.

The move instead is a **new, clean repository containing only the canonical
sources** — one `.tex` per chapter, their figures, and the bibliography —
built by copying, never moving. The Dropbox directory stays exactly as it is
and remains the archive of everything else. Cost: one decision per duplicated
chapter about which version is canonical, which has to be made anyway.

Without this, step 6 is unsafe. A scripted rename across 10,000 lines with no
rollback is how a good afternoon becomes a bad week.

### 1. Census the symbols before changing any

Machine-generate one table: every symbol, in every chapter, with its meaning
and its dimensions. Generated from the TeX, not from memory, so that it is
complete rather than what came to mind. Every collision above was found this
way in minutes; the rest will be too.

This is the artifact the whole revision hangs on, and it is cheap,
non-destructive, and useful even if nothing else follows.

### 2. Write the grammar down explicitly

The table in "The system is already there" is a first draft. Making the rules
explicit turns "does this symbol feel right?" into "does this symbol follow the
rule?", which is a question that can be answered by someone other than the
author — including a script.

### 3. Fix the dimensions before the aesthetics

A symbol carrying two dimensions is a defect. A symbol that is merely
inelegant is a preference. Do the first pass on dimensions alone: every
equation's units checked, every symbol assigned exactly one dimension. That
pass is objective, and it is where the real errors live — flaw 2 above, and
`ḣ_m,q = ∂²z/∂x²` (units `1/L`, missing `k_hs`), were both dimensional.

### 4. The deference rule, stated once and applied everywhere

> **Defer to the literature where it is unanimous and uncollided. Use the
> course system otherwise, and record the reason in one line.**

This resolves the tension that prompted the whole question. It is not
"my system" against "the literature" — it is a test applied symbol by symbol:

- `τ`, `u_*`, `S`, `D_50`, `ρ`, `ν`, `Re` — unanimous, uncollided → defer.
- Hillslope diffusivity — the literature offers `D`, `K`, `κ`, `k_d`; and `D`
  and `K` are both taken elsewhere in this course → course system, `k_hs`.
- Creep decay depth — `H*`, `λ`, `δ` in three papers → course system, `Δz_u`.

Every departure carries its one-line reason in the census table, so no future
reader — or future Andy — has to reconstruct the argument.

### 5. Test the notation against runnable models

**This is the part that came out of building `hillcreep`, and it is the reason
to pair the two projects.**

The `k_hs` dimensional overload sat in the TeX for years. It surfaced within
minutes of writing the model, because code cannot let one name carry two
dimensions and two meanings — the moment you must type an identifier, the
ambiguity becomes a decision. The same pass caught a lost sign that the notes'
own stated limit contradicted, and it produced `k_u`, the missing symbol, as a
by-product of needing something to call the coefficient.

A prose derivation can be internally inconsistent and read perfectly well. An
executable one cannot. So: **for each chapter with a live equation, a small
runnable model in the chapter's notation**, checked against an analytic limit.
`hillcreep` is the prototype of this for hillslopes.

### 6. Then change the TeX, one chapter per commit

With 0–5 done, this is mechanical and safe:

- one chapter per commit, message naming the symbols changed and why;
- rebuild the PDF and diff the equations, not just the source;
- after any scripted edit, verify that *only* the intended change landed —
  a `\bK\b` regex will happily rewrite an author's initial, and a quoted
  passage from another source must keep its original symbols.

That last point is not hypothetical: renaming this model's symbols mangled a
verbatim Landlab docstring quote, doubled a coefficient in a design document,
and rewrote English prose where a word happened to match an identifier. All
three were caught by re-reading the diff, and none by running the tests.

### 7. Ship a crosswalk

An appendix mapping every course symbol to what the literature calls it, per
paper. This removes the entire objection to using a local system: a student
going to Landlab, or to Roering, or to a thesis committee, has the translation
in front of them. `hillcreep`'s `README.md` has a working example of the form.

## What this costs, honestly

Steps 0–2 are cheap, reversible, and worth doing regardless — they tell you the
true size of the problem before you commit to anything. Step 3 is where the
real errors get fixed and is worth doing even if the notation never changes.
Steps 4–7 are the actual revision, and should be decided *after* seeing the
census, not before.

The risk that matters is not effort, it is **timing**: students hold PDFs with
the old symbols, and the site serves a stale build. A notation change lands
cleanly between offerings and badly in the middle of one.

## What was decided on 2026-09-04

- The notes wait. `hillcreep` was built first, using the course notation.
- No `git init` in the Dropbox course directory.
- `k_u` is a proposal *for the notes*, arrived at by writing the model.
- The errata for `02_03_Hillslopes_2022.tex` — four substantive items, a
  dimensional slip, notation and spelling — was handed to Andy as a separate
  file and deliberately not filed in this repo, since it is course material.
  The two items that touch this model are recorded in
  `docs/course-notes-provenance.md`.
