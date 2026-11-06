# Shell-specific, roll-aware overlay estimate

This implements the accuracy recommendation following approval of the privacy,
client-result preservation and unload fixes. It supersedes the fixed +/-25%
Gaussian and mean-shot HEAT losses in REFERENCE_CALCULATION.md.

## Penetration range and weights

Read r = shell.piercingPowerRandomization for the shell in this shot calculation.
The range is [P*(1-r), P*(1+r)], where P is the current fullPiercingPower. Zero
randomization is a point mass (deterministic). Missing/invalid RNG is unknown;
there is no silent fallback to 25%.

For r > 0, keep an estimated normal shape with sigma = P*r/3, explicitly
normalized within the shell's range. Integrate the surviving mass above the
initial penetration requirement. At both bounds probability is continuous,
and equals 0%/100% outside them. This is a modeling choice; the shell's spread
alone does not prove the server's RNG density. The listing must continue to
describe estimates, not exact server damage or guaranteed outcomes.

## Every roll passes through its own layers and losses

Represent remaining penetration for any initial roll p as:

```
remaining(p) = scale*p - spent
initially: scale=1, spent=0
armor layer a: require p >= (spent+a)/scale; spent += a
air gap: f=max(0,1-gap*shell_loss_factor); scale *= f; spent *= f
```

Take the largest initial requirement over the traversed layers. This is a
closed-form propagation of all rolls through the continuous linear loss model,
not a simulation of only the mean and not random sampling at runtime. If the
jet dissipates completely, no roll can reach the hull. Armor and ricochet still
come from the client's helpers. Modern HE/HESH uses the shield-penetration
property and client shield factor, without HEAT air-gap loss.

The observed client's ordering applies jet loss before ignoring a repeated
collide-once material. Match that ordering while never subtracting duplicate
armor twice. Tests cover this case explicitly. Module reachability is based on
whether any positive modeled probability survives to that module, using the
same roll budget, not a separate mean-shot calculation.

Example: P=300, 20mm screen, 1m gap at 50%/m loss, 180mm hull. Each roll leaves
0.5*(p-20) for the hull, requiring p>=380. At +/-25% the maximum is 375, so the
estimated penetration chance is zero; with +/-40% some rolls survive. The older
mean-shot virtual armor value of 340mm is no longer used. The armor label now
shows the required INITIAL penetration again, or '-' for an exhausted jet.

## Validation and boundaries

70 source and 70 bytecode tests cover narrow/wide/zero RNG, probability bounds,
symmetry/continuity, exhausted/zero-loss jets, repeated layers, modules, AP/APCR,
HEAT and HE/HESH. A separate forward simulator subtracts armor and applies losses
to 4096 individual roll samples per case, weighting samples by an independent
normal PDF calculation, and agrees with the analytic probability within 0.08
percentage points. There is no stochastic sampling in the shipped overlay.

Client shot-result methods, original arguments/results/exceptions and cleanup
remain protected by the existing regressions. Telemetry remains removed. All
previous font/color/angle/hidden status/preview settings are preserved. The old,
unused fixed-spread armorshotanalyzer_math.pyc was removed after checking there
were no runtime references; the probability implementation has one active source.

Limits: continuous penetration, fixed collision geometry and a chosen RNG density
are estimates; this does not reproduce every server rounding rule, destructible
geometry change or nonpenetrating HE splash calculation. No in-game trial was
performed for this revision. Backup: before_shell_roll_accuracy_2026-11-06.zip.
