"""Tests for the evolutionary-steering engine.

These assert the *qualitative* invariants the model is meant to demonstrate
(steering beats monotherapy; results are reproducible; the genotype space
behaves) rather than exact rates, so they are robust to small refactors.

Run from the project root:

    python -m pytest tests/            # if pytest is available
    python tests/test_steering.py      # plain stdlib runner (no deps)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steering.landscape import NAMED_NETWORKS, PDModel, CollateralNetwork
from steering.population import Population, SimConfig
from steering.simulate import run_one, run_experiment


def _clearance(policy, network, replicates=120, base_seed=1):
    cleared = sum(run_one(policy, network, SimConfig(seed=base_seed + r)).cleared
                  for r in range(replicates))
    return cleared / replicates


def test_reproducible():
    """Same seed must give identical outcomes."""
    a = run_one("steering", "cs_cycle", SimConfig(seed=42))
    b = run_one("steering", "cs_cycle", SimConfig(seed=42))
    assert a.drug_sequence == b.drug_sequence
    assert a.cleared == b.cleared
    assert a.population_trace == b.population_trace


def test_monotherapy_collapses():
    """A single drug used alone should almost never clear in this regime."""
    assert _clearance("monotherapy", "cs_cycle") < 0.2


def test_steering_beats_monotherapy_everywhere():
    """Steering must clear far more often than monotherapy on every network."""
    for net in NAMED_NETWORKS:
        mono = _clearance("monotherapy", net)
        steer = _clearance("steering", net)
        assert steer > mono + 0.4, f"steering did not dominate monotherapy on {net}"


def test_steering_robust_on_cross_resistance():
    """On a cross-resistance network, blind reactive switching breeds
    multidrug resistance; steering should clear substantially more often."""
    steer = _clearance("steering", "cross_resistance")
    reactive = _clearance("reactive_switch", "cross_resistance")
    assert steer > reactive + 0.3


def test_steering_limits_resistance_breadth():
    """Averaged over replicates, steering should generate a narrower
    multidrug-resistance burden than blind rotation on the scrambled cycle."""
    summary = run_experiment("cs_cycle_scrambled", replicates=120, base_seed=1)
    assert summary["steering"]["mean_max_breadth"] < summary["fixed_cycle"]["mean_max_breadth"]


def test_mutation_clamps_levels():
    net = NAMED_NETWORKS["cs_cycle"]()
    g = tuple([2, 2, 2, 2])
    for _ in range(50):
        g = net.mutate(g, 0, max_level=6)
        assert all(0 <= x <= 6 for x in g)


def test_network_json_roundtrip(tmp_path=None):
    import tempfile
    net = NAMED_NETWORKS["cs_cycle"]()
    d = tempfile.mkdtemp()
    path = os.path.join(d, "net.json")
    net.to_json(path)
    loaded = CollateralNetwork.from_json(path)
    assert loaded.matrix == net.matrix
    assert loaded.drug_names == net.drug_names


def test_pd_model_monotonic():
    """Higher resistance level must never lower survival under a drug."""
    pd = PDModel()
    last = -1.0
    for level in range(0, 7):
        g = (level, 2, 2, 2)
        s = pd.survival(g, 0)
        assert s >= last - 1e-12
        last = s


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failures}/{len(fns)} passed")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
