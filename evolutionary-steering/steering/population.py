"""Stochastic evolutionary dynamics of a pathogen population under
antibiotic treatment.

The model is a Wright-Fisher-style birth/death/selection process over
discrete resistance genotypes, with density-dependent regulation toward a
carrying capacity and stochastic mutation that follows the collateral
network. It is deliberately small and seedable so results are
reproducible and the *mechanism* (not numerical noise) drives the
comparison between policies.

Each generation:
  1. Selection: every genotype's expected contribution is its count times
     its survival under the currently applied drug times its growth factor.
  2. Density regulation: the expected pool is capped at carrying capacity K.
  3. Stochastic resampling: actual integer counts are drawn (Poisson) so
     small populations can stochastically go extinct -- i.e. be *cleared*.
  4. Mutation: a binomial fraction of new cells acquire a resistance
     mutation aimed at a random drug, with collateral effects applied.

A treatment "interval" is several generations during which one drug is
applied; the policy may switch drugs between intervals based on what it
can observe about the population.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .landscape import CollateralNetwork, Genotype, PDModel


@dataclass
class SimConfig:
    carrying_capacity: int = 5000     # K: max sustainable population
    base_growth: float = 3.0          # offspring per survivor before regulation
    mutation_rate: float = 1.2e-2     # per-cell chance of a resistance mutation
    interval_generations: int = 6     # generations between policy decisions
    horizon_intervals: int = 60       # total treatment length (decisions)
    clearance_threshold: int = 1      # population at/below this counts as cleared
    failure_breadth: int = 2          # dominant load resists >= this many drugs = MDR failure
    initial_population: int = 4000
    standing_variation: float = 6e-3  # pre-existing resistant fraction per drug
    seed: Optional[int] = None


@dataclass
class IntervalObservation:
    """What a policy is allowed to see at a decision point: a coarse,
    realistically-obtainable summary of the population -- mean resistance
    level per drug and total burden. (A real clinic would get this from a
    rapid resistance assay / sequencing, not from omniscient state.)"""

    mean_resistance: Tuple[float, ...]
    total_population: int
    current_drug: int
    cleared: bool


@dataclass
class SimResult:
    cleared: bool
    failed_mdr: bool
    intervals_used: int
    drug_sequence: List[int] = field(default_factory=list)
    population_trace: List[int] = field(default_factory=list)
    max_breadth: int = 0  # most drugs simultaneously resisted by the dominant load


class Population:
    """A treatable pathogen population evolving under a deployment policy."""

    def __init__(self, net: CollateralNetwork, pd: PDModel, cfg: SimConfig):
        self.net = net
        self.pd = pd
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.n_drugs = net.n_drugs
        # Start at the wild-type baseline tolerance, plus realistic standing
        # genetic variation: a large pre-treatment population already contains
        # rare cells carrying a resistance mutation to each drug (mutation-
        # selection balance). This pre-existing variation -- not de novo
        # mutation during therapy -- is the dominant real-world route to
        # treatment failure, so we seed it explicitly.
        wt: Genotype = tuple([pd.baseline_level] * self.n_drugs)
        self.counts: Dict[Genotype, int] = {wt: cfg.initial_population}
        mean_standing = cfg.initial_population * cfg.standing_variation
        for d in range(self.n_drugs):
            n = _poisson(self.rng, mean_standing)
            if n > 0:
                mutant = net.mutate(wt, d, pd.max_level)
                self.counts[mutant] = self.counts.get(mutant, 0) + n

    # ---- observation ----------------------------------------------------------
    def total(self) -> int:
        return sum(self.counts.values())

    def mean_resistance(self) -> Tuple[float, ...]:
        tot = self.total()
        if tot == 0:
            return tuple([0.0] * self.n_drugs)
        sums = [0.0] * self.n_drugs
        for g, c in self.counts.items():
            for d in range(self.n_drugs):
                sums[d] += g[d] * c
        return tuple(s / tot for s in sums)

    def breadth(self) -> int:
        """Number of drugs the *dominant* genotype can actually survive at the
        applied dose (resistance level above the wild-type baseline AND high
        enough to escape the drug). This is the operational measure of how
        multidrug-resistant the prevailing pathogen load is."""
        if not self.counts:
            return 0
        dom = max(self.counts.items(), key=lambda kv: kv[1])[0]
        return sum(1 for d, x in enumerate(dom)
                   if x > self.pd.baseline_level and self.pd.survival(dom, d) > 0.5)

    def observe(self, current_drug: int) -> IntervalObservation:
        return IntervalObservation(
            mean_resistance=self.mean_resistance(),
            total_population=self.total(),
            current_drug=current_drug,
            cleared=self.total() <= self.cfg.clearance_threshold,
        )

    # ---- dynamics --------------------------------------------------------------
    def _step_generation(self, drug: int) -> None:
        cfg = self.cfg
        # 1. expected contribution per genotype after selection
        expected: Dict[Genotype, float] = {}
        for g, c in self.counts.items():
            if c <= 0:
                continue
            w = self.pd.survival(g, drug) * self.pd.fitness_cost(g) * cfg.base_growth
            e = c * w
            if e > 0:
                expected[g] = e

        total_expected = sum(expected.values())
        if total_expected <= 0:
            self.counts = {}
            return

        # 2. density regulation toward carrying capacity
        scale = 1.0
        if total_expected > cfg.carrying_capacity:
            scale = cfg.carrying_capacity / total_expected

        # 3. stochastic resampling (Poisson) + 4. mutation
        new_counts: Dict[Genotype, int] = {}
        for g, e in expected.items():
            mean = e * scale
            n = _poisson(self.rng, mean)
            if n <= 0:
                continue
            # mutation: how many of these acquire a resistance mutation
            mutants = _binomial(self.rng, n, cfg.mutation_rate)
            residents = n - mutants
            if residents > 0:
                new_counts[g] = new_counts.get(g, 0) + residents
            for _ in range(mutants):
                target = self.rng.randrange(self.n_drugs)
                gm = self.net.mutate(g, target, self.pd.max_level)
                new_counts[gm] = new_counts.get(gm, 0) + 1

        self.counts = new_counts

    def run_interval(self, drug: int) -> None:
        for _ in range(self.cfg.interval_generations):
            self._step_generation(drug)
            if self.total() <= self.cfg.clearance_threshold:
                self.counts = {}
                return


def _poisson(rng: random.Random, mean: float) -> int:
    """Knuth's algorithm for small means; normal approximation for large."""
    if mean <= 0:
        return 0
    if mean > 30:
        # normal approximation, clamped at 0
        val = int(round(rng.gauss(mean, mean ** 0.5)))
        return max(0, val)
    import math
    L = math.exp(-mean)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def _binomial(rng: random.Random, n: int, p: float) -> int:
    if n <= 0 or p <= 0:
        return 0
    if p >= 1:
        return n
    # exact for small n*p (mutation is rare), else normal approx
    if n * p < 20:
        return sum(1 for _ in range(n) if rng.random() < p)
    val = int(round(rng.gauss(n * p, (n * p * (1 - p)) ** 0.5)))
    return max(0, min(n, val))
