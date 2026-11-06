# Client compatibility check — 2026-11-05

Client: ASIA v.2.4.1.1 #991, client revision 2653317, overrides 2653575,
branch v2.4.1, read from the configured Steam asia/version.xml.

## Evidence

- scripts.pkg SHA256:
  `2e4ce9af5821c35a793fe9ab69610ee6c56472835361957630ef07c0f49d0751`.
- Compared complete bytecode files against the original files preserved in
  backup 2026: gun_marker_ctrl.pyc, tankStructure.pyc and
  items/components/component_constants.pyc all match byte-for-byte. No new
  shot-result, vehicle-component or HE coefficient changes were found in these
  files since build #988. They retain Python 2.7 magic 03f30d0a.
- Static audit found the required battle events, postmortem entry point,
  SHOT_RESULT names, Wulf exports, inherited view/window methods and ViewModel
  transaction/property methods. See client_inspection/api_audit.json and
  audit_client_api.py. Symbol presence is not a full behavior/signature proof.
- Installed dependency: mods/2.4.1.1/net.openwg.gameface_1.2.2.wotmod;
  CRC valid, meta.xml version 1.2.2. Its libs/model.js contains ModelObserver,
  onUpdate and subscribe used by the overlay. No claim of upstream release
  certification for #991 is made.
- res_mods/2.4.1.1 contains only readme.txt. At inspection the mods directory
  contains Gameface, without an installed AP Calculator package.
- Required project/runtime files and Python 2.7 headers pass the project check.
- 38 source tests and 38 compiled-bytecode tests pass using the current client's
  Python 2.7 DLL and extracted standard library. Full outputs are in
  client_inspection/source_tests_991.txt and bytecode_tests_991.txt.

## Result and limits

No incompatibility was found within the static checks and mocked tests above;
runtime changes or recompilation were not required. Keep compact probability
text, module orange/futile-shot red estimates, gradient, hidden angle and the
original PF DIN Max Compressed Bold font. Backup 2026 is unchanged.

Repackage as `AP_Calculator-ASIA 2.4.1.1 #991.wotmod` in the configured parent
output directory, with ZIP_STORED runtime files under res/. Packaging checks CRC,
entry compression and every file's contents. Preserve the #988 output.

The game was not launched or modified. Existing python.log is dated 2026-08-30
and is not evidence for this package. An in-battle test of overlay lifecycle,
HEAT/HE/HESH and module colors is still needed for full compatibility confirmation.
