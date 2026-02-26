# ASA ELO Reverse-Engineering Methodology

This project reverse-engineers **plausible per-competition score distributions** (the hidden score inputs used to compute `S_actual`) from partially observed circuit data:

* known competition fields (who attended)
* known placements for top teams
* known ELO leaderboard snapshots (e.g. 02/07 and 02/20)

The goal is **not** to recover exact judge sheets, but to recover score shapes that are:

* **consistent with the ASA ELO algorithm**
* **consistent with observed leaderboard snapshots**
* **consistent with known placements and competition participation**

---

## What We Are Solving

We know the **outputs** (ELO ratings at checkpoints), but we do **not** know the exact normalized competition scores that fed the rating system.

We want to infer a set of per-team competition scores (`z`-scores / score proxies) such that, after running the ASA-style ELO updates and permutation averaging, the resulting ratings closely match the published standings.

In short:

* **Known:** fields + placements + leaderboard snapshots
* **Unknown:** per-competition score distributions
* **Goal:** reconstruct plausible hidden score distributions

---

## Forward Model (How Ratings Are Computed)

The simulator implements the ASA-style ELO pipeline:

### 1) Compute `S_actual` from per-comp scores

For each competition:

* subtract the minimum score in the field
* normalize by the sum of score gaps

This gives each team an **actual score share** (`S_actual`) within that competition.

### 2) Compute `S_expected` from current ELO

For each team in a competition:

* compute pairwise Elo expected scores against every other team in the field
* aggregate and normalize into a competition-level expected share (`S_expected`)

### 3) Apply ELO update

For each team:

* `ΔR = K * (N - 1) * (S_actual - S_expected)`

Where:

* `N` = number of teams in the competition
* `K` follows the ASA-style logic (e.g. 20 for early comps, 16 after)

### 4) Average across permutations

Because chronological order introduces bias, ratings are averaged across many possible competition orderings (with date-group permutation logic).

---

## Why Initial Error Was Large

The first reverse-engineering attempts produced a relatively large error because the optimization method was not well-suited to the problem structure.

### The inverse problem is underdetermined

For the 5-comp case:

* **40 score parameters** (5 comps × 8 teams)
* only **~10 known rating constraints**

This means there are **many valid solutions**.

### Why Nelder–Mead struggled

Nelder–Mead (a gradient-free optimizer) was used initially. In this setting, it performs poorly because:

* the search space is high-dimensional
* the objective has many flat directions
* many parameter changes do not significantly affect the fitted ratings

Result: it found “pretty good” regions (e.g. RMSE ≈ 6) but failed to converge to exact or near-exact fits.

---

## Key Insight: This Is an Underdetermined Inverse Problem

This is not a “solve one exact system of equations” problem.

Instead, it is an **inverse problem with infinitely many solutions**:

* more unknowns than constraints
* no unique reconstruction
* objective is to find **any valid fit** that also looks reasonable

This changes the strategy from:

> “Find the exact answer”

to:

> “Find a plausible answer that satisfies all known structure.”

---

## Reduced-Parameter Fitting Strategy

A major improvement came from reducing the number of optimized parameters.

### Why reducing parameters helps

The known top-team ratings are driven mostly by:

* the placed teams they directly faced
* the score gaps among those high-impact teams

Unplaced teams often matter less in a first-pass fit, so we can:

* assign them reasonable defaults
* optimize only the scores for relevant/placed teams

This makes the optimization much more tractable.

### Typical reduced parameter set

The first targeted fits focused on teams that:

* appeared in the known top 10
* had known placements in the competitions

Examples included:

* Dhamakapella
* TAMU Swaram
* UTD Dhunki
* UCD Jhankaar
* MN Fitoor
* Illini Awaaz
* UMD Anokha
* Humraah at IU
* UGA Kalakaar
* Stanford Raagapella
* UW Awaaz

---

## Enforcing Score Ordering with Softplus Gap Encoding

A crucial technique was to parameterize score vectors using **positive gaps** rather than raw scores.

### Why this matters

Known placements imply a monotonic ordering (e.g. 1st > 2nd > 3rd).
Directly optimizing raw scores can violate this.

### Softplus gap encoding

For each competition, define scores as:

* `score_1 = fixed value` (e.g. 1.0)
* `score_2 = score_1 - gap_1`
* `score_3 = score_2 - gap_2`
* ...

Each `gap_i` is constrained positive by:

* `gap_i = softplus(theta_i)`

This guarantees:

* strictly decreasing score order
* smooth differentiable optimization
* no fragile hard inequality constraints

---

## Why “Exact Fit” Was Still Wrong (Important Pitfall)

At one point, extremely low RMSE (near-zero) was achieved against the chosen known targets — but the reconstructed **full standings were still wrong**.

### What went wrong

The optimization objective only enforced:

* exact values for selected known teams
* within-comp score ordering

It did **not** enforce:

* top-10 membership consistency
* leaderboard cutoff constraints
* global ranking structure

This allowed unconstrained teams (e.g. Hum A Cappella, Penn State Fanaa) to end up unrealistically high while the fitted teams matched perfectly.

### Lesson

Low RMSE on a partial target set **does not imply** a valid global reconstruction.

---

## Fixing the Global Ranking Problem

To solve this, the fit objective was expanded beyond exact rating matching.

### Added constraints / penalties

The optimization was updated to include penalties for:

* non-top10 teams rising above the top-10 cutoff
* violations of known leaderboard membership
* (optionally) known relative ordering among top teams

This turned the problem into a **leaderboard-consistent fit**, not just a target-value fit.

### Result

The reconstruction became much more trustworthy:

* slightly higher RMSE (expected)
* much better full-standings consistency

This is a tradeoff worth making.

---

## Why Unplaced Teams Eventually Had to Be Optimized Too

A reduced-parameter approach works well initially, but fixing unplaced teams too aggressively can create unrealistic or degenerate solutions.

### What happened

When “placed > unplaced” constraints were introduced while keeping unplaced scores fixed, the optimizer began to produce strange score shapes (e.g. compressed placed scores) and degraded fits.

### Better approach

Optimize **all per-comp scores** (or at least a much larger subset), while still enforcing:

* monotonic ordering
* placement consistency
* leaderboard constraints

This gave:

* realistic score distributions
* valid ordering
* strong fit quality

---

## Joint Constrained Fit Across Multiple Snapshots

Once additional competitions (e.g. Jeena, Awaazein, Boston Bandish) were added, fitting only one snapshot was no longer enough.

### Why joint fitting is necessary

A solution that matches 02/20 can still:

* break 02/07
* violate earlier leaderboard membership
* overfit late-season dependencies

### Joint fit objective

The final methodology included constraints for both:

* **02/07 leaderboard snapshot**
* **02/20 leaderboard snapshot**

Plus:

* top-10 membership / cutoff penalties for each checkpoint
* placement order constraints
* regularization toward plausible score shapes

This substantially reduced “fake exact” solutions.

---

## Snapshot Permutation Bug (and Fix)

A subtle bug appeared in the extended simulator:

* the 02/07 snapshot was being averaged using the first 5 comps extracted from full 8-comp permutations
* which accidentally let later competitions affect the 02/07 snapshot in some orderings

### Correct behavior

Snapshots must be computed independently:

* **02/07:** average only over permutations of the first 5 comps
* **02/20:** average over permutations of all 8 comps

Fixing this improved conceptual correctness and stabilized the fit.

---

## Final Practical Workflow

### Step 1 — Build the forward simulator

Implement:

* `S_actual` from score vectors
* `S_expected` from Elo ratings
* ELO updates
* permutation averaging by date-group

### Step 2 — Seed plausible score vectors

Start with reasonable z-score guesses based on:

* known placements
* rough competition strength assumptions
* prior fitted values (if available)

### Step 3 — Parameterize score ordering safely

Use softplus gap encoding to guarantee monotonic score order.

### Step 4 — Fit in stages

* fit reduced parameters first (high-impact comps/teams)
* inspect error + standings
* expand to broader/full score optimization
* apply joint constraints across snapshots

### Step 5 — Validate globally

Check:

* RMSE vs known targets
* full standings consistency
* top-10 membership
* score shape plausibility
* inferred `S_actual` sanity

---

## What This Method Can and Cannot Claim

### What it can claim

This methodology can produce score distributions that are:

* **consistent with the ASA ELO model**
* **consistent with observed placements**
* **consistent with leaderboard snapshots**
* **useful for scenario analysis and dependency reasoning**

### What it cannot claim

It cannot uniquely reconstruct the “true” judge scores.

Because the problem is underdetermined:

* multiple hidden score configurations can produce nearly identical ELO outputs

So outputs should be interpreted as:

> **model-consistent plausible reconstructions**, not literal score sheets.

---

## Practical Value of This Approach

This reverse-engineered model is useful for:

* understanding why certain teams are overrated/underrated in ELO
* simulating future competition outcomes
* identifying which teams’ results most affect a team’s ranking
* stress-testing rule changes (e.g. minimum number of comps)
* explaining late-season “dependency graph” effects

---

## Key Lessons Learned

1. **Underdetermined inverse problems require structure, not just better optimization.**
2. **Low RMSE is not enough — leaderboard membership constraints matter.**
3. **Softplus gap encoding is a robust way to enforce score ordering.**
4. **Joint checkpoint fitting is much stronger than single-snapshot fitting.**
5. **Snapshot permutation logic must be implemented carefully.**
6. **Global validation (full standings) is essential.**

---

## Future Improvements

Potential upgrades for this project:

* add a full constrained optimizer module (SciPy-based)
* generate **multiple valid fits** (uncertainty bands)
* estimate confidence intervals for inferred `S_actual`
* compare alternative ranking systems (flat K, end-of-season-only Elo, minimum-comp filters)
* build an interactive dashboard for scenario simulations

---

## TL;DR

This project reverse-engineers hidden competition score distributions by treating the ASA ELO pipeline as a deterministic forward model and solving a constrained inverse problem. The methodology evolved from naive optimization (high error, misleading exact fits) into a **joint, leaderboard-consistent, multi-snapshot constrained fit** that produces realistic and useful score reconstructions — while still acknowledging that the solution is not unique.
