# Loaded-shell penetration extension

The maintained sources are in `source/`. The game receives Python 2.7 `.pyc`
files only. `build_bytecode.py` rebuilds the entry point and shell-info module
with Python 2.7; it leaves the original mod's other bytecode unchanged.

The probability row now shows, for example:

    HEAT 300 mm | 72.3% | SPACED

- AP / APCR / HEAT / HE are identified from the shell supplied by the current
  game's shot-result call, rather than a queued ammunition selection.
- The mm value is the full piercing power supplied to that call, at the current
  aiming distance. The main armor label shows the required initial penetration.
- SPACED identifies a non-hull armor layer along the collision path.
- NO PEN means zero estimated full-penetration chance, not zero HE splash damage.
- NO HULL means the collision path did not reach the main vehicle armor (tracks
  or other external components alone do not imply hull damage).
- RICOCHET uses the game's own helper and the configured red ricochet color.
- Missing/unsupported material information shows `?`; it is not treated as a
  guaranteed failure.

HEAT attenuation uses the game's shell loss coefficient and the gaps between
collision layers. Each layer is mapped back to the initial penetration needed,
so the displayed chance accounts for attenuation of every possible penetration
roll. Chance retains the original mod's bounded normal-distribution estimate,
using the loaded shell's penetration randomization. It is not a server guarantee
or a probability of hitting the same point after gun dispersion.

The extra text reuses the existing probability row and visibility lifecycle,
including its normal hide, postmortem and window-destruction paths. Its status
can wrap inside the 256px overlay. The richer row is enabled by this extension
although the original standalone percentage-label setting remains disabled.
The wrapper preserves the existing game's/mod's shot-result return values.
The original armor/angle/gradient/track settings and disabled JSON persistence
remain intact. The track indicator uses >80% rather than requiring an exact
match with the high-probability gradient endpoint.

Tests: `python2.7 -B development/tests/test_shell_info.py` for source, or
`AP_TEST_BYTECODE=1 python2.7 -B development/tests/test_shell_info.py` for compiled
bytecode. Tests stub game APIs; actual in-game validation is still needed.
Packaging includes only `res/gui` and `res/scripts`, excluding this development
directory and AGENTS.md. The previously generated archive must be rebuilt after
changing runtime assets.
