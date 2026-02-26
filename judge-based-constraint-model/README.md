# Recommended future architecture (UW-focused, precise version)

## 1) Keep the current layer: ELO engine (forward simulator)

This part is already your backbone and should stay:

* competition rosters
* date-group permutation averaging
* expected score calculation (multi-team generalized ELO)
* actual score construction from normalized competition scores
* ELO updates

ASA’s doc explicitly defines:

* equal 1500 initialization,
* pairwise expected scores aggregated and renormalized,
* actual scores that are monotone, last place = 0, sum to 1 via min-subtracted normalized score deltas.  

That engine is your “physics simulator.” Don’t mess with it much.

---

## 2) Add a new layer: Judge-score generative model (the precise part)

This is the real upgrade.

Instead of fitting only a single competition z-score per team, fit:

* **Judge-level category scores** for each team at a comp
* subject to rubric constraints and score bounds

### Proposed variable structure (per comp)

For competition (c), judge (j), team (t), category (k):

* (x_{c,j,t,k}) = judge raw score in category (k)

Categories are the rubric ones:

* Musical Composition (30%)
* Vocal Execution (30%)
* Visual Execution (25%)
* South-Asian Representation (15%) 

Then define:

* weighted raw per judge/team:
  [
  r_{c,j,t} = 0.30x_{MC}+0.30x_{VE}+0.25x_{Vis}+0.15x_{SAR}
  ]
* judge-normalized z-score across teams in that comp:
  [
  z_{c,j,t} = \frac{r_{c,j,t}-\mu_{c,j}}{\sigma_{c,j}}
  ]
* synthetic judge mean score:
  [
  \bar z_{c,t} = \frac{1}{J_c}\sum_j z_{c,j,t}
  ]
* then ASA actual score (S_{\text{actual}}) from (\bar z) using min-subtract + normalize. 

That gets you from “guessing z-scores” to “reconstructing a plausible judge table.”

---

## 3) Encode **real scoring bounds and granularity** (your precision goal)

You said you want to be “completely precise” because judges score categories on bounded scales.

That’s a great instinct. You can model this in stages:

### Stage A (continuous bounded)

Assume category scores are continuous in ([0,10]) for each judge/category.

* Much easier optimization
* Good first version

### Stage B (quantized / decimal grid)

If judges score in increments like 0.5 or 0.1, enforce:

* (x \in {0, 0.5, 1.0, \dots, 10}) or similar

### Stage C (true integer / rubric-specific granularity)

If rubric really uses exact category max points or integer-only:

* enforce exact discrete domains per category
* this becomes a **mixed-integer optimization** problem (MIP / CP-SAT style)

This is where the project gets deliciously nerdy.

---

## 4) Add UW-specific hard constraints from your real score sheets

This is the strongest UW-specific feature.

If you have UW’s actual judge sheets (or partial category totals), add them as constraints:

### Hard constraints (best)

If you know exact values:

* “Judge 2 gave UW Vocal Execution = 9”
* “UW total weighted raw for Judge 3 = 8.1”
* “UW category sum across judges in comp = X”

Then enforce exactly.

### Soft constraints (if uncertain)

If you only know approximate or remembered values:

* add penalty terms like ((x - x_{\text{known}})^2)
* or interval constraints: (x \in [8.5, 9.0])

This is huge because it pins the inverse problem to reality and reduces bogus degrees of freedom.

---

## 5) Make it a **constrained optimizer module** (SciPy first, then stronger solvers)

You mentioned “full constrained optimizer module (SciPy-based).” Yes.

### Start with SciPy (good first version)

Use `scipy.optimize.minimize` (SLSQP / trust-constr) or `least_squares` with penalties.

Parameterization tricks:

* use **softplus gap encoding** to force monotone placement order in synthetic scores
* use **sigmoid transforms** to keep category scores in [0,10]
* normalize or center judge score scales to avoid numerical weirdness

### But for true score granularity (0–10 discrete)

SciPy will struggle if you enforce exact discreteness.

Then upgrade to:

* **OR-Tools CP-SAT** (great for discrete constraints)
* **Pyomo + IPOPT / BONMIN** (if you want heavier optimization machinery)
* or hybrid:

  * SciPy for continuous fit
  * discrete rounding + local search repair

That hybrid is usually the sweet spot.

---

## 6) Generate multiple valid fits (uncertainty bands)

This is the most important scientific upgrade, because your inverse problem is underdetermined.

A single fit is *a story*.
A family of fits is *evidence*.

### What to do

Run many fits with:

* different random seeds
* different regularization weights
* different plausible assumptions for unknown teams
* bootstrap over uncertain comps / placements (if partial)

Then collect distributions of:

* UW’s inferred (S_{\text{actual}}) at each comp
* Stanford/Anokha inferred (S_{\text{actual}})
* final ELO ranks
* “UW finishes above Stanford?” probability
* “UW qualifies?” probability under your model assumptions

### Output

For each quantity, report:

* median
* 5th/95th percentiles
* sensitivity to assumptions

This gives you **uncertainty bands** instead of fake precision.

---

## 7) Estimate confidence intervals for inferred (S_{\text{actual}})

This is the natural consequence of step 6, and it’s exactly what you want.

### Example UW-specific outputs

* Jeena (S_{\text{actual}}(\text{UW})): median 0.18, 90% CI [0.16, 0.20]
* Davis Dhwani (S_{\text{actual}}(\text{UW})): median 0.17, 90% CI [0.15, 0.19]
* Probability UW > Stanford after remaining comps (under assumed Mehfil/Rang scenarios): X%

That’s a much stronger statement than “plausible shape.”

---

## 8) Add a “future outcomes” scenario engine specifically for UW

This is your endgame dashboard.

You already think in terms of:

* “If Dhunki does really well…”
* “If Sargam places 4th…”
* “Do Awaazein participants need to do badly for Stanford/Anokha to drop?”

Make this explicit.

### UW scenario engine inputs

* Remaining comp placements (partial or full)
* Optional score gap assumptions (close 1st/2nd vs blowout)
* Optional judge-score assumptions (if you’re doing judge-level mode)

### Outputs (UW-centric)

* UW final rank distribution
* UW gap to Stanford / Anokha
* sensitivity decomposition:

  * how much of Stanford’s rank is from Awaazein carryover?
  * how much does Dhunki’s Mehfil result move UW vs move Stanford?
* “Most favorable / most damaging outcomes” tables

This is the model equivalent of game tape.

---

# How to make it “precise” without overclaiming

This part matters a lot.

You can be **mathematically precise** while being **epistemically honest**.

## Precise:

* exact ASA scoring pipeline
* exact bounds/granularity on judge category scores
* exact known UW judge constraints
* exact permutation averaging for date groups

## Honest:

* other teams’ unobserved judge sheets remain latent
* many solutions can still fit
* rankings for teams below known cutoff remain less reliable
* future comps remain scenario-based, not prediction certainty

That combo builds trust.

---

# Suggested project modules (UW-focused)

Here’s a clean structure for a real repo:

* `asa_elo/core.py`

  * ELO engine, expected/actual, permutation averaging

* `asa_elo/rubric.py`

  * category weights, judge-score aggregation, z-normalization

* `asa_elo/constraints.py`

  * placement constraints
  * score bounds / granularity constraints
  * known leaderboard checkpoint constraints
  * UW known-score constraints

* `asa_elo/fit_scipy.py`

  * continuous constrained optimizer (SciPy)

* `asa_elo/fit_discrete.py`

  * optional discrete/quantized solver (OR-Tools / hybrid)

* `asa_elo/ensemble.py`

  * multi-fit generation, uncertainty bands, bootstrapping

* `asa_elo/uw_analysis.py`

  * UW-specific reports and “what helps UW” scenario analyses

* `notebooks/`

  * exploratory fits, diagnostics, sanity checks

* `data/`

  * competitions, rosters, known snapshots, UW score sheets (private/local)

This makes it a legit research-ish engineering project.

---

# One especially powerful UW-specific idea

You mentioned: *“ideally we can also input our team’s scores as an extra layer of constraint.”*

Yes — and here’s the move:

## Treat UW sheets as an anchor, not just extra data

Instead of only saying “UW got X z-score-ish,” encode:

* UW judge-category scores (or intervals)
* UW weighted totals per judge
* UW placement constraints
* maybe even judge comment-linked priors (soft only)

For example, repeated judge feedback about pitch/blend issues could justify a soft prior on Vocal Execution variance (not a hard score, but a prior). Your UW feedback PDF has category score examples and qualitative comments that can support this kind of structured prior design.  

That turns the UW portion from “guessed latent variable” into “observed anchor.” Huge upgrade.

---

# Practical roadmap (what to build next, in order)

## Phase 1 — UW-precise continuous model (fast win)

* Add rubric layer
* Add category weights
* Add bounded [0,10] judge-category variables
* Add UW score sheet constraints (whatever you have)
* Fit continuous solution with SciPy
* Output inferred (S_{\text{actual}}) CIs via multi-starts

## Phase 2 — Quantized scores

* Enforce 0.5 or 0.1 increments
* Hybrid solve (continuous fit → quantized repair)
* Compare how much quantization changes UW conclusions

## Phase 3 — Ensemble / uncertainty

* Generate many valid fits
* Plot UW rank distribution
* Plot sensitivity to Dhunki/Stanford/Anokha future outcomes

## Phase 4 — UW strategy dashboard

* “What outcomes maximize UW nats odds?”
* “What results hurt Stanford/Anokha relative to UW?”
* scenario explorer for Mehfil + Rang de Raaga

