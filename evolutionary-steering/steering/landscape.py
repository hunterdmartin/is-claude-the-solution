"""Resistance genotypes, the pharmacodynamic kill model, and the
collateral-sensitivity network that couples drugs together.

Genotype representation
-----------------------
A genotype is a tuple of integer *resistance levels*, one per drug:

    g = (l_0, l_1, ..., l_{D-1}),   l_d in [0, L_max]

Level 0 means fully susceptible to that drug; higher means more
resistant (think of it as a coarse-grained log2-MIC). Carrying
resistance is costly, so high-level multidrug genotypes pay a growth
penalty.

Collateral network
-------------------
``C[i][j]`` is the change in resistance level to drug ``j`` caused by a
single resistance-acquiring mutation that targets drug ``i``:

    C[i][i] > 0   the mutation's primary effect (raises resistance to i)
    C[i][j] < 0   collateral SENSITIVITY (resistance to i lowers MIC to j)
    C[i][j] > 0   cross-RESISTANCE (resistance to i also raises MIC to j)
    C[i][j] = 0   independent

These pleiotropic couplings are what make evolution *steerable*: if every
escape route up one drug's resistance ladder pushes the population down
another's, a policy that always attacks the freshly-exposed weakness can
keep the population cornered.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

Genotype = Tuple[int, ...]


@dataclass(frozen=True)
class PDModel:
    """A minimal pharmacodynamic model: how well does a genotype survive a
    given drug applied at a given concentration?

    Survival is a logistic (Hill-like) function of how far the genotype's
    resistance level exceeds the applied concentration. A susceptible cell
    facing an effective drug survives a generation with low probability; a
    resistant cell survives with high probability.
    """

    concentration: float = 4.0   # applied dose, in resistance-level units
    steepness: float = 1.5       # Hill slope of the kill curve
    cost_per_level: float = 0.05  # growth penalty per unit of carried resistance
    max_level: int = 6
    baseline_level: int = 2      # intrinsic tolerance of the wild type

    def survival(self, genotype: Genotype, drug: int) -> float:
        """Probability a cell of ``genotype`` survives one generation of
        exposure to ``drug`` at the model concentration."""
        margin = genotype[drug] - self.concentration
        return 1.0 / (1.0 + math.exp(-self.steepness * margin))

    def fitness_cost(self, genotype: Genotype) -> float:
        """Multiplicative growth factor (<=1) from carrying resistance.

        Costs are sub-additive: the marginal cost of each extra resistance
        level shrinks, reflecting compensatory adaptation. Even so, broad
        multidrug genotypes grow appreciably slower than the wild type.
        """
        total = sum(genotype)
        # sub-additive: sqrt-like saturation so the model never goes negative
        return 1.0 / (1.0 + self.cost_per_level * total)


class CollateralNetwork:
    """Square matrix of pleiotropic couplings between drugs."""

    def __init__(self, matrix: Sequence[Sequence[float]], drug_names: Sequence[str] | None = None):
        n = len(matrix)
        for row in matrix:
            if len(row) != n:
                raise ValueError("collateral matrix must be square")
        self.matrix: List[List[float]] = [[float(x) for x in row] for row in matrix]
        self.n_drugs = n
        self.drug_names = list(drug_names) if drug_names else [f"drug_{i}" for i in range(n)]

    # ---- construction helpers -------------------------------------------------
    @classmethod
    def from_json(cls, path: str) -> "CollateralNetwork":
        with open(path, "r", encoding="utf-8") as fh:
            blob = json.load(fh)
        return cls(blob["matrix"], blob.get("drug_names"))

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"drug_names": self.drug_names, "matrix": self.matrix}, fh, indent=2)

    # ---- dynamics -------------------------------------------------------------
    def mutate(self, genotype: Genotype, target_drug: int, max_level: int) -> Genotype:
        """Apply one resistance-acquiring mutation aimed at ``target_drug``.

        The primary effect raises resistance to the target; collateral
        effects shift resistance to every other drug per the matrix. Levels
        are clamped to ``[0, max_level]``.
        """
        levels = list(genotype)
        for j in range(self.n_drugs):
            delta = self.matrix[target_drug][j]
            # round toward the effect's sign so small couplings still bite
            step = int(delta) if abs(delta) >= 1 else (1 if delta > 0 else (-1 if delta < 0 else 0))
            # only the primary mutation is guaranteed; collateral steps apply
            # the integer part of the coupling
            if j == target_drug:
                levels[j] += max(1, int(round(delta)))
            else:
                levels[j] += int(round(delta))
            levels[j] = max(0, min(max_level, levels[j]))
        return tuple(levels)


# ---------------------------------------------------------------------------
# Example networks. These are ILLUSTRATIVE structures, not measured values.
# The shapes are inspired by the literature on collateral-sensitivity
# networks (e.g. Imamovic & Sommer 2013; Nichol et al. 2015; Barbosa et al.
# 2017): reciprocal collateral-sensitivity cycles do occur and are the most
# exploitable structure. Replace these with empirical matrices to get
# clinically meaningful output.
# ---------------------------------------------------------------------------

def cs_cycle_network() -> CollateralNetwork:
    """A 4-drug *collateral-sensitivity cycle*: gaining resistance to each
    drug sensitises the next one around the ring (A->B->C->D->A). This is
    the ideal steerable structure."""
    nm = ["A", "B", "C", "D"]
    m = [
        # primary +3 on diagonal; -2 collateral sensitivity to the next drug
        [3, -2, 0, 0],
        [0, 3, -2, 0],
        [0, 0, 3, -2],
        [-2, 0, 0, 3],
    ]
    return CollateralNetwork(m, nm)


def cs_cycle_scrambled_network() -> CollateralNetwork:
    """The same collateral-sensitivity cycle, but the sensitised drug is NOT
    the next one in index order: A sensitises C, C sensitises B, B sensitises
    D, D sensitises A. Blind 'rotate to the next drug' policies misfire here;
    an observation-driven steering policy still finds the weak drug."""
    nm = ["A", "B", "C", "D"]
    #          A   B   C   D
    m = [
        [3, 0, -2, 0],   # A sensitises C
        [0, 3, 0, -2],   # B sensitises D
        [0, -2, 3, 0],   # C sensitises B
        [-2, 0, 0, 3],   # D sensitises A
    ]
    return CollateralNetwork(m, nm)


def cross_resistance_network() -> CollateralNetwork:
    """A pessimistic control: resistance to any drug confers partial
    cross-resistance to the others (positive off-diagonals). Steering should
    help much less here -- there is no weakness to exploit."""
    nm = ["A", "B", "C", "D"]
    m = [
        [3, 1, 1, 0],
        [1, 3, 0, 1],
        [1, 0, 3, 1],
        [0, 1, 1, 3],
    ]
    return CollateralNetwork(m, nm)


def independent_network() -> CollateralNetwork:
    """Neutral control: drugs are pharmacologically independent."""
    nm = ["A", "B", "C", "D"]
    m = [[3 if i == j else 0 for j in range(4)] for i in range(4)]
    return CollateralNetwork(m, nm)


NAMED_NETWORKS = {
    "cs_cycle": cs_cycle_network,
    "cs_cycle_scrambled": cs_cycle_scrambled_network,
    "cross_resistance": cross_resistance_network,
    "independent": independent_network,
}
