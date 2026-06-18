# Solving Antimicrobial Resistance: a systems strategy, with a working model of its scientific core

*Worked on the `status-claude` branch in isolation, per `CLAUDE.md`.*

---

## TL;DR

Antimicrobial resistance (AMR) is not a disease to be cured once; it is an
**evolutionary process to be managed indefinitely**. Any static drug used at
scale will eventually be defeated — that is selection working as designed. So
the goal is not "invent enough new antibiotics to win," which is a race we keep
losing, but to **change the game from a race into a sustainable, managed
equilibrium**: extend the useful lifetime of every drug we have, slow the rate
at which we manufacture new resistance, and fix the economics so that drugs we
deliberately *under-use* can still exist.

This document proposes an integrated, four-pillar strategy and a single
**flagship mechanism** — *Steering-as-Infrastructure* — that ties the pillars
together by aligning the money (who pays for antibiotics) with the biology (how
we use them) through shared information (a global susceptibility data commons).

To show that one of the load-bearing scientific claims is real and not
hand-waving, this branch also ships a small, runnable, dependency-free
simulation ([`evolutionary-steering/`](evolutionary-steering/)) demonstrating
that **how** you deploy a fixed set of antibiotics — the sequencing policy —
changes both whether you cure the infection and how much resistance you breed,
and that the decisive ingredient is *information about the resistance network*.

> **Honesty up front.** I am a language model. I cannot run a wet lab, fund a
> program, or pass a law. What I can do well is *structure the problem*,
> *identify the highest-leverage and most-neglected interventions*, *design
> mechanisms*, and *build and test computational artifacts*. I have done all of
> those here. The numbers in the simulation come from plausible but invented
> parameters; its job is to demonstrate a mechanism and provide a reusable
> scaffold, not to stand in for clinical evidence. Where I cite figures from
> the literature, they are from my training knowledge and should be re-verified
> against primary sources before use.

---

## 1. What "solving" AMR honestly means

AMR is already associated with an enormous mortality burden — the 2019 Global
Research on Antimicrobial Resistance (GRAM) study estimated on the order of
**1.27 million deaths directly attributable** to bacterial AMR and **~4.95
million deaths associated** with it in that year, with the heaviest burden in
sub-Saharan Africa and South Asia. If antibiotics fail, the casualties are not
only people with infections: routine surgery, Caesarean sections, cancer
chemotherapy, dialysis, neonatal and intensive care, and organ transplantation
all depend on the assumption that we can control infection. AMR threatens to
quietly un-make twentieth-century medicine.

There is no end-state in which AMR is "cured." Resistance is the expected
outcome of exposing a vast, fast-reproducing, genetically mobile population to a
selective agent. **The honest goal is a durable, low-resistance equilibrium:** a
world in which (a) we generate resistance far more slowly than today, (b) we can
reliably replace and rotate the drugs we lose, and (c) the people who need
antibiotics can get them while those who do not, don't. "Solving" AMR means
building the scientific, economic, and informational machinery to *hold that
equilibrium forever*, not to win a one-time victory.

## 2. Why it is hard: four interlocking failures

AMR persists because four failures reinforce each other. Attacking any one
alone fails, because the others absorb the effort.

**A. A scientific failure — the pipeline.** Most antibiotic classes in use were
discovered decades ago; the easy molecular space (soil actinomycete products)
is largely mined out, and there was a long discovery void for genuinely novel
classes. Resistance evolves faster than truly new mechanisms arrive.

**B. An economic failure — the broken market.** This is the single most
underappreciated lever. A good new antibiotic should be *held in reserve* and
used as little as possible — which means low sales volume, which means it cannot
recoup the ~$1B+ and decade it takes to develop. Antibiotics are also cheap and
taken for days, not chronically. So the reward for success is bankruptcy:
multiple approved-antibiotic companies (e.g. Achaogen, Melinta) collapsed
*after* getting drugs to market. Big pharma has largely exited the field. **We
are asking the market to fund products whose social value lies precisely in not
selling them.** It will not.

**C. A behavioural / ecological failure — selection pressure.** Resistance is
driven by *how much* antimicrobial the world's bacteria are bathed in. A large
share of antibiotics by mass is used in **agriculture** (growth promotion and
prophylaxis in livestock), much of it avoidable. In humans, **the absence of
fast diagnostics** forces clinicians to prescribe broad-spectrum drugs
empirically ("treat first, identify later") for infections that are often viral
or self-limiting. Pharmaceutical manufacturing effluent and poor sanitation
seed the environment with both drugs and resistant organisms. And the burden is
double-sided: in many low- and middle-income countries (LMICs), **more people
die from lack of access to the right antibiotic than from resistance** — so any
solution that only restricts use is ethically and practically incomplete.

**D. An information / coordination failure.** Surveillance is patchy, especially
where the burden is highest; data are siloed by country, hospital, and company;
diagnostics are slow (culture-based susceptibility testing takes ~2–3 days); and
there is no real-time, shared, global picture of what is resistant to what,
where. Every other intervention is blunted by this: you cannot steward, steer,
price, or target what you cannot see.

```
        ┌─────────────────────────────────────────────────┐
        │  D. No shared, real-time information              │
        │     (slow diagnostics, siloed surveillance)       │
        └───────────────┬───────────────────────┬───────────┘
                        │ blinds                 │ blinds
        ┌───────────────▼──────┐      ┌──────────▼───────────────┐
        │ C. Too much selection │      │ A. Too few new drugs      │
        │    pressure (ag,      │◄────►│    (empty pipeline)       │
        │    empirical Rx, env) │      └──────────┬───────────────┘
        └───────────────────────┘                 │ caused by
                                        ┌──────────▼───────────────┐
                                        │ B. Broken market: reserve │
                                        │    drugs can't earn money │
                                        └───────────────────────────┘
```

## 3. The reframe: manage evolution instead of racing it

The conventional framing — "discover new antibiotics faster" — is necessary but
structurally insufficient, because it treats each drug as a consumable in a race
against mutation. The reframe that organizes this strategy:

> **Treat the entire antimicrobial arsenal as a renewable common resource whose
> lifetime we actively manage** — by lowering the selection pressure that
> degrades it, *steering* evolution so resistance is costly and self-limiting,
> and financing it so that responsible under-use is rewarded rather than
> punished.

This converts an unwinnable arms race into a stewardship problem — and
stewardship problems, while hard, are *solvable* with the right incentives,
information, and tools.

## 4. The strategy: four pillars

Interventions below are tagged by **leverage** (impact × tractability ÷ current
attention). I have deliberately weighted toward the *neglected* high-leverage
moves rather than re-listing what is already well-funded.

### Pillar 1 — Reduce the selection pressure (stop manufacturing resistance)

*The cheapest resistance to manage is the resistance you never create. Every
prevented or correctly-targeted infection is a selection event that never
happens.*

- **★ Rapid, point-of-care diagnostics — the highest-leverage clinical move.**
  If a clinician knows within an hour *whether* there is a bacterial infection
  and *what it is susceptible to*, empirical broad-spectrum prescribing
  collapses into narrow, correct, or no treatment. Diagnostics are chronically
  under-rewarded relative to their resistance-sparing value. **Reimburse the
  diagnostic, and tie antibiotic reimbursement to having used one.**
- **★ Vaccines as an AMR tool.** An infection prevented needs no antibiotic and
  creates no resistance. Pneumococcal conjugate vaccines already measurably
  reduced resistant-strain disease; vaccines against *Klebsiella*, *E. coli*,
  gonorrhoea, *S. aureus*, and TB would each retire huge volumes of antibiotic
  use. Vaccines are systematically undercounted in AMR strategy.
- **Agriculture:** end antibiotic use for growth promotion and routine
  prophylaxis; substitute husbandry, sanitation, and livestock vaccines; meter
  and tax non-therapeutic veterinary use.
- **Water, sanitation, and hygiene (WASH)** in high-burden settings prevents the
  infections that drive both antibiotic demand and transmission of resistant
  organisms — a development intervention that is also an AMR intervention.
- **Manufacturing effluent standards** so antibiotic production stops seeding
  resistance hotspots.
- **Balance access and excess:** pair every stewardship restriction with a
  guaranteed-access mechanism so LMIC patients are not denied drugs they need.

### Pillar 2 — Steer evolution (make resistance a dead-end) — *demonstrated in code*

*This is the scientifically richest and most under-exploited frontier, and the
part I could most concretely advance on this branch.*

Resistance is not free, and it is not isolated. Two facts make evolution
*steerable*:

1. **Fitness cost:** resistant strains often grow slower than susceptible ones
   when the drug is absent, so drug "holidays" let susceptibles win back the
   population.
2. **Collateral sensitivity:** acquiring resistance to one drug frequently
   *increases* susceptibility to another (documented across many drug pairs).
   Resistance to drug A can paint a target on the population for drug B.

If you know the collateral-sensitivity network, you can design drug *sequences*
that chase a population into evolutionary corners: every escape from the current
drug increases vulnerability to the next, so the population never accumulates
broad multidrug resistance and is repeatedly knocked down.

**I built a working model of exactly this claim.** See
[`evolutionary-steering/`](evolutionary-steering/). It is a seedable,
dependency-free stochastic evolutionary simulation that pits deployment policies
against a pathogen population carrying realistic standing genetic variation,
across several drug-interaction networks. The headline result (400 replicates):

| network | monotherapy clears | blind reactive switching clears | **collateral-sensitivity steering clears** |
|---|--:|--:|--:|
| collateral-sensitivity ring | 0% | 100% | **100%** |
| same ring, shuffled order | 0% | 100% | **100%** (and breeds ~half the resistance) |
| **cross-resistance (adversarial)** | 0% | **16%** | **87%** |
| independent drugs | 0% | 44% | **100%** |

What the model establishes (as a proof-of-mechanism, not clinical proof):

1. **Monotherapy collapses everywhere** — a single drug against a population
   with any standing resistance is a near-certain loss.
2. **Information is the active ingredient.** The steering policy is the *only*
   one that stays strong on every network, and it consistently breeds the least
   resistance. Its edge is largest precisely where the drugs interact badly. The
   difference between it and blind rotation is *entirely the use of the
   resistance-profile data* — which is why this pillar is umbilically tied to
   Pillar 4 (information) and Pillar 1 (diagnostics).
3. **Blind switching can be worse than nothing structural** — rotating to a drug
   the population can already cross-resist actively accelerates multidrug
   resistance.

Other Pillar-2 directions (not coded here, but part of the strategy):

- **Resistance-suppressing combinations** (the principle behind modern HIV and
  TB therapy) designed so that escaping all drugs at once is vanishingly likely.
- **Phage therapy and phage–antibiotic steering** — bacteriophages can be chosen
  to *force* trade-offs (e.g. a phage that binds an efflux pump, so phage
  resistance restores antibiotic sensitivity).
- **Anti-virulence and anti-evolvability drugs** — target the machinery of
  disease (toxins, secretion systems) or of evolution itself (the SOS mutagenic
  response, horizontal-transfer machinery) rather than viability, weakening the
  selection for classical resistance.

### Pillar 3 — Fix the economics (let reserve drugs exist)

*No amount of science survives a market that bankrupts success. The economic
fix is the keystone: it is what makes Pillars 1–2 fundable and durable.*

The core idea is **delinkage**: separate a drug developer's reward from the
*volume* it sells, so that a drug held responsibly in reserve is still
profitable. Concretely:

- **Pull incentives — subscription / "Netflix" models.** A payer pays a fixed
  annual sum for *access* to an effective antibiotic, regardless of how little
  is used (the UK NHS piloted this; the US **PASTEUR Act** proposed it but has
  repeatedly stalled). **Fully fund and internationally coordinate these.** A
  fragmented, country-by-country approach under-rewards a global public good.
- **Market-entry rewards** calibrated to a drug's *public-health value* —
  novelty of mechanism, activity against priority pathogens, and *expected
  resistance-sparing lifetime* — not its sales.
- **Push incentives** (CARB-X, BARDA, GARDP-type funding) to de-risk early R&D,
  especially for pathogens and patient populations the market ignores.
- **Non-profit / public-interest development** (the DNDi/GARDP model) to carry
  drugs the market will never make to patients, with public-good licensing.
- **Pooled global financing for access** so the same mechanism that rewards
  reserve drugs also guarantees they reach LMIC patients.

### Pillar 4 — Build the information commons (so everything else can see)

*This is the connective tissue. Stewardship, steering, pricing, and targeting
all depend on knowing what is resistant to what, where, in near-real-time.*

- **A global, open AMR data commons**: standardized genomic + phenotypic
  susceptibility surveillance, linked to prescribing and outcomes, federated
  across countries with privacy-preserving sharing.
- **Wastewater and environmental genomic surveillance** as a cheap, population-
  scale early-warning system for emerging resistance.
- **Open collateral-sensitivity and cross-resistance atlases** for priority
  pathogen–drug panels — the exact input the Pillar-2 steering engine needs and
  the world does not yet systematically produce.
- **Diagnostics-to-data loops:** every rapid susceptibility test, in any clinic,
  contributes (anonymized) to the commons, so the global picture sharpens with
  use.

## 5. Flagship proposal: *Steering-as-Infrastructure*

Each pillar has been proposed before in some form. The original contribution
here is a **single mechanism that fuses them by aligning the money with the
biology through shared information** — because the deepest reason AMR persists
is that the three are governed separately.

> **The mechanism.** Create an internationally pooled, delinked **Antimicrobial
> Stewardship Fund** that pays drug developers and health systems on a
> *resistance-adjusted* basis, where the unit of value is **effective
> drug-years preserved**, not doses sold — and make eligibility for those
> payments *conditional on contributing to, and using, the open
> susceptibility/collateral-sensitivity data commons.*

Why this is more than the sum of its parts:

- **It pays for under-use.** A reserve drug earns a subscription (Pillar 3)
  whether or not it is dispensed — so it can exist.
- **It pays for lifetime, not volume.** Because the reward is indexed to
  *effective drug-years preserved*, a developer (and a hospital) is rewarded for
  *slowing* resistance: deploying rapid diagnostics (Pillar 1) and
  collateral-sensitivity-aware steering protocols (Pillar 2) directly increases
  the payout. For the first time, **stewardship becomes a revenue line, not a
  cost centre.** The incentive gradient points toward conservation.
- **It is conditioned on data.** Eligibility requires contributing susceptibility
  and collateral-sensitivity data to the open commons (Pillar 4) and adopting
  diagnostic-linked prescribing. The commons is funded as a *condition of
  payment*, so the information substrate that steering needs gets built as a
  byproduct of the economics — solving the chicken-and-egg problem where steering
  needs data that no one is paid to produce.
- **It closes the loop.** Diagnostics feed the commons; the commons enables
  steering and prices drug value; pricing rewards diagnostics and steering. Each
  pillar now pays for the next.

The simulation in this branch is the in-silico evidence for the load-bearing
assumption — that *information-guided deployment materially preserves drug
effectiveness* — which is exactly the quantity ("effective drug-years
preserved") the funding mechanism is designed to buy.

## 6. Sequenced action plan

**Years 0–2 (foundations & proof):**
- Pass and *fund* delinked pull-incentive legislation (PASTEUR-style) and, in
  parallel, an international pooled fund so the reward reflects global value.
- Stand up the open data-commons standard and seed it from existing
  surveillance networks; begin wastewater genomic surveillance in hubs.
- Crash-fund rapid point-of-care diagnostics and tie antibiotic reimbursement to
  their use in well-resourced settings.
- Ground models like this branch's in *empirical* collateral-sensitivity data
  for 2–3 priority pathogens; run prospective clinical pilots of steering for
  chronic/recurrent infections where sequencing is already feasible.

**Years 2–5 (scale & integrate):**
- Index pull-incentive payments to *effective drug-years preserved* once the
  data commons can measure it.
- Phase out agricultural growth-promotion use globally; deploy livestock
  vaccines.
- Push the priority AMR vaccines (Klebsiella, gonorrhoea, etc.) through
  development with guaranteed market commitments.
- Extend diagnostics + the data loop into LMIC primary care, paired with
  guaranteed access.

**Years 5–15 (durable equilibrium):**
- Operate steering protocols as standard of care where data support them.
- Maintain a continuously replenished, delinked pipeline of novel-mechanism and
  non-traditional (phage, anti-virulence) agents.
- Hold the managed equilibrium: monitor, steer, replace — indefinitely.

## 7. What this branch actually contributes, and its limits

**Contributed here:**
- A clear problem decomposition and a reframe (manage, don't race) that
  reorganizes the intervention landscape around leverage and neglect.
- A specific, original *mechanism* (Steering-as-Infrastructure) that fuses the
  scientific, economic, and informational fixes by making the money track the
  biology via shared data.
- A **working, tested, dependency-free simulation** that demonstrates the
  central scientific premise of the steering pillar and is structured to be
  re-grounded in real data — a reusable scaffold, not just an argument.

**Limits — stated plainly:**
- The simulation's parameters are illustrative, not fitted; it proves a
  *mechanism is plausible and the information is decisive*, not that any
  specific protocol works clinically. Real collateral-sensitivity networks can
  be unstable, asymmetric, or environment-dependent, and resistance can re-route
  around steering.
- The economic and political proposals require actors I am not — legislatures,
  treasuries, regulators, and industry. I can design the mechanism; I cannot
  enact it.
- Cited epidemiological figures are from training knowledge and should be
  re-verified against primary sources before any operational use.
- This is a strategy and a proof-of-mechanism, not a clinical or policy
  guarantee.

## 8. How to verify the computational claim

```bash
cd evolutionary-steering
python3 -m steering.simulate --all-networks --replicates 400 --seed 1
python3 tests/test_steering.py
```

See [`evolutionary-steering/README.md`](evolutionary-steering/README.md) for the
model's structure, the full results table, and instructions for replacing the
illustrative parameters with empirical data.

---

### Closing

AMR will not be "solved" by a single breakthrough drug, because evolution will
defeat any single drug. It can be solved — in the only sense the word honestly
allows — by building the machinery to *manage* the arsenal forever: use less and
more precisely, steer what resistance we do create into dead-ends, and pay for
drugs by the effectiveness they preserve rather than the doses they sell, all on
a foundation of shared, real-time information. The hardest barrier is not
scientific; it is that we govern the science, the money, and the data
separately. The proposal here is to wire them together.
