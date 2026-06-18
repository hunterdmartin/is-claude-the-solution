"""Antibiotic deployment policies.

A policy decides which single drug to apply during the next treatment
interval, given only what is realistically observable: a coarse readout of
how resistant the current population is to each drug (the kind of thing a
rapid resistance assay or bedside sequencing could provide) plus the
history of drugs already used.

The comparison of interest is whether a policy that *uses the
collateral-sensitivity structure* (``steering``) outperforms policies that
ignore it (monotherapy, blind cycling, reactive switching).
"""

from __future__ import annotations

import random
from typing import Callable, List

from .population import IntervalObservation

# A policy maps (observation, history-of-drugs, rng) -> next drug index.
Policy = Callable[[IntervalObservation, List[int], random.Random], int]


def monotherapy(obs: IntervalObservation, history: List[int], rng: random.Random) -> int:
    """Use one drug for the entire course (standard, naive)."""
    return 0


def fixed_cycle(obs: IntervalObservation, history: List[int], rng: random.Random) -> int:
    """Rotate through drugs in a fixed order every interval, regardless of
    what the population is doing. 'Cycling' as often deployed in hospitals."""
    n = len(obs.mean_resistance)
    return len(history) % n


def random_cycle(obs: IntervalObservation, history: List[int], rng: random.Random) -> int:
    """Pick a drug at random each interval (mixing-like baseline)."""
    n = len(obs.mean_resistance)
    return rng.randrange(n)


def reactive_switch(obs: IntervalObservation, history: List[int], rng: random.Random) -> int:
    """Stay on the current drug while it seems to be working; when the
    population rebounds (a sign of resistance), switch to the *next* drug in
    a fixed rotation. This is clinically intuitive but ignores collateral
    structure -- it switches to a drug that may share cross-resistance."""
    n = len(obs.mean_resistance)
    if not history:
        return 0
    current = history[-1]
    # "working" heuristic: a small/shrinking population means the current drug
    # is still controlling the infection -- stay on it. A rebound means
    # resistance has emerged -- rotate to the next drug in order.
    if obs.total_population < 200:
        return current
    return (current + 1) % n


def steering(obs: IntervalObservation, history: List[int], rng: random.Random) -> int:
    """Collateral-sensitivity steering.

    Attack the population where it is weakest: choose the drug to which the
    population currently has the lowest mean resistance. On a collateral-
    sensitivity network, adapting to whichever drug we apply lowers
    resistance to another drug, which then becomes the new weakest point --
    so this policy keeps the population cornered and rarely lets it climb to
    broad multidrug resistance. Ties are broken toward the least-recently
    used drug to keep the rotation moving.
    """
    n = len(obs.mean_resistance)
    last_used = {d: -1 for d in range(n)}
    for t, d in enumerate(history):
        last_used[d] = t

    def key(d: int):
        # primary: lowest resistance; secondary: least recently used
        return (round(obs.mean_resistance[d], 6), last_used[d])

    return min(range(n), key=key)


POLICIES: dict[str, Policy] = {
    "monotherapy": monotherapy,
    "fixed_cycle": fixed_cycle,
    "random_cycle": random_cycle,
    "reactive_switch": reactive_switch,
    "steering": steering,
}
