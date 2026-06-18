"""Experiment runner: play each policy against a pathogen population many
times and report how often it clears the infection versus loses it to
multidrug resistance.

Usage:
    python -m steering.simulate                  # default experiment
    python -m steering.simulate --network cs_cycle --replicates 400 --seed 7
    python -m steering.simulate --all-networks   # sweep all example networks

Pure standard library; no third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
import os
import statistics
from dataclasses import asdict
from typing import Dict, List

from .landscape import NAMED_NETWORKS, PDModel
from .policies import POLICIES
from .population import Population, SimConfig, SimResult


def run_one(policy_name: str, network_name: str, cfg: SimConfig) -> SimResult:
    net = NAMED_NETWORKS[network_name]()
    pd = PDModel()
    pop = Population(net, pd, cfg)
    policy = POLICIES[policy_name]

    history: List[int] = []
    trace: List[int] = []
    max_breadth = 0
    current_drug = 0

    for _ in range(cfg.horizon_intervals):
        obs = pop.observe(current_drug)
        if obs.cleared:
            break
        drug = policy(obs, history, pop.rng)
        history.append(drug)
        current_drug = drug
        pop.run_interval(drug)
        trace.append(pop.total())
        max_breadth = max(max_breadth, pop.breadth())
        if pop.total() <= cfg.clearance_threshold:
            break

    cleared = pop.total() <= cfg.clearance_threshold
    failed_mdr = (not cleared) and max_breadth >= cfg.failure_breadth
    return SimResult(
        cleared=cleared,
        failed_mdr=failed_mdr,
        intervals_used=len(history),
        drug_sequence=history,
        population_trace=trace,
        max_breadth=max_breadth,
    )


def run_experiment(network_name: str, replicates: int, base_seed: int,
                   overrides: dict | None = None) -> Dict[str, dict]:
    overrides = overrides or {}
    summary: Dict[str, dict] = {}
    for policy_name in POLICIES:
        cleared = 0
        mdr = 0
        clear_times: List[int] = []
        breadths: List[int] = []
        for r in range(replicates):
            cfg = SimConfig(seed=base_seed + r, **overrides)
            res = run_one(policy_name, network_name, cfg)
            if res.cleared:
                cleared += 1
                clear_times.append(res.intervals_used)
            if res.failed_mdr:
                mdr += 1
            breadths.append(res.max_breadth)
        summary[policy_name] = {
            "clearance_rate": cleared / replicates,
            "mdr_failure_rate": mdr / replicates,
            "mean_intervals_to_clear": (statistics.mean(clear_times) if clear_times else float("nan")),
            "mean_max_breadth": statistics.mean(breadths),
        }
    return summary


def _print_table(network_name: str, summary: Dict[str, dict]) -> None:
    print(f"\n=== Network: {network_name} ===")
    header = f"{'policy':<17}{'clearance':>11}{'MDR failure':>13}{'~intervals':>12}{'max breadth':>13}"
    print(header)
    print("-" * len(header))
    # order policies by clearance rate descending for readability
    for name in sorted(summary, key=lambda k: -summary[k]["clearance_rate"]):
        s = summary[name]
        clr = f"{s['clearance_rate']*100:5.1f}%"
        mdr = f"{s['mdr_failure_rate']*100:5.1f}%"
        itv = "   n/a" if s["mean_intervals_to_clear"] != s["mean_intervals_to_clear"] else f"{s['mean_intervals_to_clear']:6.1f}"
        brd = f"{s['mean_max_breadth']:6.2f}"
        print(f"{name:<17}{clr:>11}{mdr:>13}{itv:>12}{brd:>13}")


def _write_csv(path: str, all_summaries: Dict[str, Dict[str, dict]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["network", "policy", "clearance_rate", "mdr_failure_rate",
                    "mean_intervals_to_clear", "mean_max_breadth"])
        for net_name, summary in all_summaries.items():
            for pol, s in summary.items():
                w.writerow([net_name, pol, f"{s['clearance_rate']:.4f}",
                            f"{s['mdr_failure_rate']:.4f}",
                            f"{s['mean_intervals_to_clear']:.4f}",
                            f"{s['mean_max_breadth']:.4f}"])


def main(argv: List[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Compare antibiotic deployment policies by the resistance they provoke.")
    p.add_argument("--network", default="cs_cycle", choices=list(NAMED_NETWORKS))
    p.add_argument("--all-networks", action="store_true", help="run every example network")
    p.add_argument("--replicates", type=int, default=400)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--mutation-rate", type=float, default=None, help="override per-cell mutation rate")
    p.add_argument("--standing-variation", type=float, default=None, help="override pre-existing resistant fraction")
    p.add_argument("--horizon", type=int, default=None, help="override number of treatment intervals")
    p.add_argument("--csv", default="results/policy_comparison.csv")
    args = p.parse_args(argv)

    overrides: dict = {}
    if args.mutation_rate is not None:
        overrides["mutation_rate"] = args.mutation_rate
    if args.standing_variation is not None:
        overrides["standing_variation"] = args.standing_variation
    if args.horizon is not None:
        overrides["horizon_intervals"] = args.horizon

    networks = list(NAMED_NETWORKS) if args.all_networks else [args.network]
    all_summaries: Dict[str, Dict[str, dict]] = {}
    for net_name in networks:
        summary = run_experiment(net_name, args.replicates, args.seed, overrides)
        all_summaries[net_name] = summary
        _print_table(net_name, summary)

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = args.csv if os.path.isabs(args.csv) else os.path.join(here, args.csv)
    _write_csv(csv_path, all_summaries)
    print(f"\nWrote {csv_path}")


if __name__ == "__main__":
    main()
