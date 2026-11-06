Release r993. See CHANGELOG.md. Native reticle SWF structure and rendered sample checked offline. Ten simulated battle/garage cycles passed. See client_inspection/r993_archive_tests.txt.

# Final review of delivered archives

Client: ASIA 2.4.1.1 #991. Audited the actual exported files, not only workspace
source or the previously rejected version.

Latest revision also implements the post-approval accuracy recommendation:
shell-specific piercingPowerRandomization, normalized bounded-normal estimates,
and affine propagation of all initial rolls through armor and HEAT gaps. See
ROLL_AWARE_ESTIMATE.md for formulas, independent 4096-roll simulations and limits.
The fixed-spread helper is removed. These remain overlay estimates, not server
RNG certification. The privacy/native-result/unload fixes remain intact.

## Artifact identity

- Mod: phuochung94.armorshotanalyzer-ASIA 2.4.1.1 #991.wotmod
  SHA256: 067543dae046610c3b320eec2681506fa8b9edf384672d13683f3f7c23603c30
- Bundle: UNZIP-phuochung94.armorshotanalyzer-ASIA 2.4.1.1 #991.zip
  SHA256: 77f419d38f3fe5bde3cd50facc8b8596e6845be263e7c626a4717221e3476e65

## Reviewer requirements

1. Telemetry removed entirely. No logger module, garage telemetry callback, HTTP
   request, player/server reporting, opt-in feature or five-second network stall
   remains in mod runtime. Privacy audit also covers the loader and nested
   constant containers. The included installed OpenWG bytecode passes the same
   static forbidden-marker audit. Upstream/reference/backups are not shipped.
2. No copied client penetration implementations are installed. Thin wrappers call
   the active client functions with identical input objects, return their actual
   results and propagate their original exceptions. Additional math remains an
   independent overlay estimate. Real-client default and modern-HE function-code
   regressions compare both return values and debug traces, exercising exhausted
   penetration and nonzero HE screen absorption in controlled test globals.
3. init/fini install and remove hooks/subscriptions. Teardown preserves later
   hooks owned by other mods, restores inherited descriptors correctly, disables
   retained callbacks/wrappers using per-install sessions, retries transient
   unsubscribe failures, and attempts window close independently of label errors.

## Executed validation

- 73 source tests pass.
- 73 workspace bytecode tests pass.
- 73 additional isolated tests pass using runtime bytecode extracted directly
  from the final exported .wotmod. Test source is only a harness; the loaded mod
  and lifecycle code under test come from the delivery archive.
- All six maintained source modules match compiled delivery bytecode exactly.
- Runtime/no-menu/privacy audits pass on the extracted mod; the OpenWG bytecode
  is inspected statically without being initialized.
- The 18 archive entries match workspace runtime bytes, are all ZIP_STORED,
  and contain no development/reference/backups or logger. CRCs are valid.
- The outer ZIP contains exactly the corrected mod and the installed OpenWG
  1.2.2 package, byte-identical to their sources; both nested CRCs pass.

Machine-readable evidence: client_inspection/final_release_review.json.
Test output: client_inspection/roll_delivered_tests.txt and
client_inspection/roll_delivered_audit.txt.
Reproduce after packaging with prepare_release_audit.py, then
inspect_client.py --run res/development/run_release_audit.py.

No actual game session or reviewer resubmission was performed. Differential
tests use real function code with mocked game dependencies and do not replace
an in-battle test. Close/restart the client when replacing the rejected version,
as its old in-memory hooks/telemetry cannot be removed by replacing files alone.
Restore point 2028 remains untouched.
