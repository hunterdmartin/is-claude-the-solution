# Evolutionary steering of antimicrobial resistance — a runnable model

This is the computational artifact accompanying [`../SOLUTION.md`](../SOLUTION.md).
It is a small, **dependency-free** (pure Python standard library) simulation
that asks a concrete question:

> Given several antibiotics and some knowledge of how resistance to one
> changes susceptibility to the others, does *how* you deploy them — the
> sequencing policy — change how often you cure the infection and how much
> resistance you breed along the way?

The answer the model gives is **yes, decisively**, and it shows *why the data
matters*: the policy that uses the resistance/collateral-sensitivity structure
(`steering`) is the only one that performs well across every drug-interaction
network we test. This is the in-silico backbone of Pillar 2 of the strategy.

> ⚠️ **This is an illustrative engine, not a clinical tool.** The numbers come
> from plausible but *invented* pharmacodynamic and collateral parameters. Its
> value is (a) demonstrating the mechanism cleanly and reproducibly and (b)
> being structured so a lab or hospital could drop in *empirical* collateral-
> sensitivity matrices and dose-response data and get meaningful output. See
> "Making it real" below.

## Quick start

```bash
cd evolutionary-steering
python3 -m steering.simulate --all-networks --replicates 400 --seed 1
python3 tests/test_steering.py          # qualitative test suite (no deps)
```

No `pip install` needed — Python 3.8+ only.

## What it models

- **Genotype** = a vector of integer *resistance levels*, one per drug (a
  coarse-grained log2-MIC). Level 0 = susceptible; the wild type starts at a
  small baseline tolerance so that *collateral sensitivity* can push a drug's
  MIC below baseline.
- **Pharmacodynamics** (`landscape.PDModel`): a logistic kill curve — a cell
  survives a generation of a drug with a probability that rises as its
  resistance level exceeds the applied dose. Carrying resistance costs growth.
- **Collateral network** (`landscape.CollateralNetwork`): a matrix `C[i][j]` =
  how a resistance mutation aimed at drug *i* shifts resistance to drug *j*.
  Negative = collateral **sensitivity** (the steerable case); positive =
  cross-**resistance** (the trap).
- **Evolution** (`population.Population`): a seedable Wright-Fisher-style
  birth/death/selection/mutation process with density regulation toward a
  carrying capacity, started from a realistic amount of **standing genetic
  variation** (rare pre-existing resistant cells — the dominant real-world
  route to treatment failure).
- **Policies** (`policies.py`): how the next drug is chosen each treatment
  interval, given only a *realistically observable* readout (mean resistance
  per drug + total burden):
  - `monotherapy` — one drug, always.
  - `fixed_cycle` — rotate in fixed order.
  - `random_cycle` — random drug each interval (mixing-like).
  - `reactive_switch` — stay until the infection rebounds, then rotate.
  - `steering` — **attack the weakest point**: pick the drug to which the
    population is currently least resistant. On a collateral-sensitivity
    network this keeps the population cornered in evolutionary dead-ends.

## Headline result (defaults, 400 replicates, seed 1)

`clearance` = infection cured; `MDR failure` = lost to a multidrug-resistant
load; `max breadth` = how many drugs the prevailing pathogen ended up able to
survive (lower = less resistance bred).

| network | policy | clearance | MDR failure | max breadth |
|---|---|--:|--:|--:|
| **cs_cycle** | steering | **100.0%** | 0.0% | 1.02 |
| (CS ring, ordered) | fixed_cycle | 100.0% | 0.0% | 1.01 |
| | reactive_switch | 100.0% | 0.0% | 1.02 |
| | monotherapy | 0.0% | 0.0% | 1.00 |
| **cs_cycle_scrambled** | **steering** | **100.0%** | 0.0% | **1.03** |
| (CS ring, shuffled) | fixed_cycle | 100.0% | 0.0% | 1.92 |
| | reactive_switch | 100.0% | 0.0% | 1.92 |
| | monotherapy | 0.0% | — | 1.00 |
| **cross_resistance** | **steering** | **87.0%** | **13.0%** | **1.82** |
| (the adversarial trap) | fixed_cycle | 71.5% | 28.5% | 2.51 |
| | random_cycle | 38.8% | 61.3% | 3.06 |
| | reactive_switch | 15.8% | 84.2% | 3.61 |
| | monotherapy | 0.0% | — | 1.00 |
| **independent** | **steering** | **100.0%** | 0.0% | **1.46** |
| (no coupling) | fixed_cycle | 98.2% | 1.8% | 1.98 |
| | reactive_switch | 43.5% | 56.5% | 3.08 |
| | monotherapy | 0.0% | — | 1.00 |

(Full numbers in [`results/policy_comparison.csv`](results/policy_comparison.csv);
console capture in [`results/canonical_run.txt`](results/canonical_run.txt).)

**Three robust take-aways:**

1. **Monotherapy collapses** — 0% clearance everywhere. A single drug against a
   population with any standing resistance is a near-certain loss. This is the
   real-world AMR story in one line.
2. **Information is the active ingredient.** `steering` is the *only* policy
   that stays strong on every network, and it consistently breeds the least
   resistance (lowest `max breadth`). Its advantage is biggest exactly where
   the drugs interact badly (`cross_resistance`: 87% vs 16% for blind reactive
   switching). The difference between steering and the blind policies is
   entirely the *use of the resistance-profile data*.
3. **Blind switching can be worse than nothing structural.** On cross-resistant
   or scrambled networks, rotating to the "next" drug hands the population a
   drug it can already partly resist, accelerating the climb to multidrug
   resistance. Diversity helps only when it is *informed*.

This is why the policy half of the solution centres on **rapid diagnostics +
an open collateral-sensitivity data commons**: steering is only as good as the
susceptibility information feeding it, and that information is a public good we
do not yet systematically produce.

## Making it real (how to extend)

The engine is deliberately small so it can be re-grounded in data:

- **Drop in empirical collateral-sensitivity matrices.** Replace the example
  networks in `data/*.json` (or `landscape.py`) with measured cross-resistance/
  collateral-sensitivity values for a real pathogen-drug panel (e.g. published
  *E. coli*, *P. aeruginosa*, or *S. aureus* networks). `CollateralNetwork.from_json`
  loads them directly.
- **Calibrate the pharmacodynamics** (`PDModel`) to measured dose-response /
  MIC distributions and fitness costs.
- **Add pharmacokinetics** — time-varying drug concentration, adherence, tissue
  penetration — by making `concentration` a function of time.
- **Add combination therapy** — the current engine deploys one drug per
  interval (the *sequencing* question); extending `survival` to multiple
  simultaneous drugs enables combination/synergy policies.
- **Learn the policy** — `steering` is a hand-written heuristic; the same
  observation/action interface supports a reinforcement-learning controller.

## Layout

```
evolutionary-steering/
├── steering/
│   ├── landscape.py    # genotypes, pharmacodynamics, collateral networks
│   ├── population.py    # stochastic evolutionary dynamics
│   ├── policies.py      # deployment policies incl. collateral-sensitivity steering
│   └── simulate.py      # experiment runner / CLI
├── data/                # example collateral networks as JSON (swap in real data)
├── results/             # generated CSV + console capture
└── tests/test_steering.py
```

## Provenance & honesty

The model's *structure* is grounded in the published evolutionary-medicine
literature on collateral sensitivity and evolutionary steering (e.g. Imamovic &
Sommer 2013; Nichol et al. 2015; Barbosa et al. 2017; the "antibiotic time
machine" line of work). The specific parameter values here are **illustrative
and chosen by the author of this branch**, not fitted to data. Treat the
results as a proof-of-mechanism and a reusable scaffold, not as clinical
evidence.
