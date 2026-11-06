# Calculation reference supplied by the user

Input: Downloads/pademinune-AP_Calculator-2.2.0.wotmod.
SHA256: 0fcf470511febe755b6b3996210a0430d00af0f5fdc05ec1bc4d389fa99823aa.
Extracted offline math/hooks reference hashes are in reference_2_2_0/SOURCE.json.
The reference module initializers are never executed or installed. Its telemetry,
menu registration and client algorithm overrides are not imported into runtime.

The maintained overlay now follows this reference's effective armor accumulation:

- AP/APCR: accumulated penetration armor from game helpers.
- HEAT: subtract each layer from mean remaining penetration; across the next
  air gap, add max(0, mean_remaining * gap * loss_factor) to effective armor and
  apply that loss to mean remaining penetration. Preserve the reference ordering
  for repeated collide-once materials. This replaces the earlier armor/scale
  initial-penetration threshold calculation.
- Modern HE/HESH: reference shield-penetration factor and reference decision to
  stop overlay analysis at an impassable screen. It does not replace the current
  client's HE absorption or penetration algorithms.
- Gaussian: fixed 75%-125% bounds and exactly the reference's erf expression,
  with z = 6*sqrt(2)*(armor-average)/average. This matches the earlier Gaussian
  for standard 25% RNG but intentionally follows the reference's fixed range
  for nonstandard RNG. Shell RNG is still used for module/layer reachability.

Example: 300mm mean HEAT, 20mm screen, 1m gap at 50%/m loss and 180mm main armor:
reference effective armor is 20 + 140 + 180 = 340mm, whereas the earlier initial
penetration threshold was 380mm. The displayed number is now the reference's
virtual effective armor, not the earlier reverse-solved initial requirement.

Retain safeguards for unknown/invalid data and the approved visual/module/angle
behavior. No percentages or status words are displayed. Native shot functions,
inputs, returned results, exceptions and unload cleanup stay protected.

Validation: isolated reference functions compare armor/flags across nine collision
scenarios and probability across 36 points. Only inspected function code is run
with mocked helpers and no-op debug/GUI callbacks, not reference initialization.
58 source + 58 bytecode tests pass, including current-client result preservation
and lifecycle regressions. No in-game confirmation or submission performed.

Restore backup: backups/before_reference_math_2026-11-06.zip.
