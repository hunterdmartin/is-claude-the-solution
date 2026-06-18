"""Evolutionary steering of antimicrobial resistance.

A small, dependency-free simulation engine for comparing antibiotic
deployment *policies* by the resistance they provoke, not just the
pathogen they kill in the short term.

The central idea: resistance to one drug frequently changes
susceptibility to another (collateral sensitivity or cross-resistance).
A policy that *exploits* the known collateral-sensitivity network can
trap a pathogen population in evolutionary dead-ends, clearing it more
reliably and with less multidrug resistance than naive monotherapy or
blind cycling.

This package is an extensible, illustrative engine. It is meant to be
re-parameterised with empirical collateral-sensitivity data, not used as
a clinical tool as-is. See README.md.
"""

from .landscape import CollateralNetwork, PDModel
from .population import Population, SimConfig
from .policies import POLICIES, Policy

__all__ = [
    "CollateralNetwork",
    "PDModel",
    "Population",
    "SimConfig",
    "POLICIES",
    "Policy",
]
