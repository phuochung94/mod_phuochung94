# MoE Calculator ASIA

Mod: 14th_ua's MoE Calculator 8.0.0.
Display name: phuochung94's MoE Calculator (user-requested branding).
Runtime IDs/resource paths now use phuochung94, as requested on 2026-11-06:
com.phuochung94.moe_calculator, com_phuochung94_moe_calculator,
res/gui/gameface/mods/phuochung94 and the matching gen_resources JSON filename.
The API user-agent and local cache namespace are renamed consistently too.
The old cache directory is not read, copied or deleted; the new namespace gets
fresh data. Do not install old and renamed packages together (same Python entry
module). Metadata credits the original author and links to the original repository.
`tools/rename_namespace.py` verifies all marshal fields against the expected
string-only transformation without recompiling Python 2.7. Workspace directory
and historical backups retain their original names.
Game directory: `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`.
OpenWG releases: https://gitlab.com/openwg/wot.gameface/-/releases
Author source: https://github.com/drizzer14/moe-calculator

## User command: cập nhật mod

When the user clicks or sends “cập nhật mod”, perform the complete workflow:
read the installed game's actual version/build, check client interfaces,
ASIA API, resources and OpenWG dependency, make necessary mod code fixes,
recheck and build the stored `.wotmod` in the agreed output directory.
Preserve phuochung94 branding and fixed defaults without a settings menu.
Back up overwritten artifacts and report actual checks and runtime limits.
Do not merely rename an archive or reuse historical checks. This command
does not create a recurring schedule or imply installation into the game.

## Current change

The supplied Python 2.7 module `adapter/moe_wgapi.pyc` assigns `REGION = "eu"`.
The ASIA build changes that constant to `"asia"`, so requests and region-tagged
cache validation use ASIA. No Python opcodes, API key, calculations, or unrelated
marshal fields are changed. The original module and previous archive are backed
up under `dist/backups/`. Upstream main was inspected (9.0.0), not substituted
for the supplied 8.0.0.

The read-only API smoke check returned HTTP 200 and API status `ok`, with
`distribution` and `updated_at` fields. This validates connectivity and acceptance
of the bundled application id; it does not prove every vehicle has data.

## Build and checks

Also create `UNZIP-phuochung94.moe_calculator-ASIA <version> #<build>.zip`
in the same output directory, with two separate root entries: the MoE wotmod
and the verified OpenWG Gameface wotmod. Do not embed Gameface into the mod.
Gameface is maintained as a separate dependency: select/check a compatible
official version for each game update, not permanently 1.2.2. Bundle using
`tools/bundle_zip.py`, which verifies both files against the build/client hashes.
Preparing the bundle does not imply permission to change the installed dependency.

The user requested fixed original defaults without a settings menu or editing.
`tools/fix_defaults.py` disables menu registration/settings loading and mutation,
position setters/dragging, and per-vehicle/manual/automatic variant overrides.
Garage, battle overlay and counted assistance keep their original enabled
defaults; the separate battle progress bar remains disabled by default.
Previously saved settings are ignored, not deleted. Alt display behavior remains
available according to the original defaults; it is not a settings change.

The patch modifies 13 selected Python 2.7 function bodies with immediate returns
and unreachable NOP padding, preserving instruction lengths, argument signatures,
module initialization, defaults and all other marshal fields. One JS guard
disables installation of garage drag handlers. Backups are in
`dist/backups/fixed-defaults/`. Full marshal comparisons and JS syntax checks
pass; the fixed-default mode has not been tested inside the game.

Run `tools/build_asia.py` with Python 3. It reads the actual game version,
validates the Python 2.7 marshal payloads, checks four client module/symbol pairs,
and packages only `res/` plus `meta.xml` using ZIP_STORED. It then verifies CRCs
and every packaged file against its source. It preserves an existing output
before replacing it. Output:

`C:\pademinune-AP_Calculator-2.2.0\phuochung94.moe_calculator-ASIA <version> #<build>.wotmod`

This output directory was explicitly requested by the user. It is outside the
current writable workspace; request filesystem escalation when needed. Reports
and backups remain in the workspace's `dist/` directory.

`tools/check_asia_api.py` performs one read-only network request. It keeps the
bundled application id out of logs. Build again after this check to include its
result in `dist/compatibility-report.json`.

## Limits and future updates

On 2026-11-05 the installed game was rechecked: ASIA 2.4.1.1 #991,
client 2653317, overrides 2653575 (previous baseline: #988).
OpenWG Gameface 1.2.2 is now installed in mods/2.4.1.1; its metadata,
Python 2.7 gf_mod_inject signature and ModelObserver resource were checked.
The official releases API also listed v1.2.2 as latest when checked.
The ASIA API smoke check again returned HTTP 200/status ok.
`tools/verify_client.py` passed 36 static checks covering client symbols,
dependency interface, JS syntax/imports, layouts, branding and the 13 locked
settings functions. No additional mod-code changes were indicated by these checks.
The report is in `dist/client-check.json`; rerun it for subsequent client builds.
No installation, game launch, garage check, or battle check was performed.
Static symbol matches do not prove compatible signatures or runtime behavior.

When the user requests support for a newer game version, inspect changes in
client APIs and dependency behavior and make necessary code changes before
building. Merely rerunning the packager is not a compatibility port. Confirm
garage mounting, per-vehicle thresholds, battle assistance/projections, and
absence of mod tracebacks in a fresh game log before declaring runtime support.
Back up installed mods/settings and obtain filesystem approval before writing
to the game directory. There is no scheduled background updater.

2026-11-07: Added bridge/viewport_watch.pyc and one startup hook in battle_bridge.install_all_listeners. The watcher tracks the active battle view and GUI.screenResolution via the existing safe bar_window helper every 0.25 seconds. On view/size change it reuses the existing placement/scale callback for four ticks to allow Wulf layout settling. Invalid/zero dimensions and leaving battle reset the cached placement; repeated starts do not create additional timer chains. Windows stay content-sized and input-transparent. Existing fixed defaults/menu removal are preserved. tools/fix_resize.py includes Python 2.7 bytecode generation and independent simulated opcode tests (start once, idle, resize, zero/unavailable resolution, battle exit and next battle); this is not an in-game test. Original bridge backed up in dist/backups/resize.

User confirmed screenshot anchor: beside the left vehicle-status/personal-efficiency HUD. Preserve the original battle anchor constants and relative spacing when resizing; do not relocate to a different screen corner. Resize watcher reapplies the existing placement function.

2026-11-07: Added bridge/native_visibility.pyc. It reads the active battle page through IAppLoader.getDefBattleApp().containerManager.getView(WindowLayer.VIEW), then SharedPage.isGuiVisible() and as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL). It synchronizes a dedicated native_damage_hud gate in battle_bridge._open_overlays without clearing other gates; the original snapshot spectator/own-vehicle rules are preserved. GameEvent.GUI_VISIBILITY updates immediately; the existing viewport watcher polls every 0.25s for native component transitions, including kill-camera hiding/restoring. Native page lookup failure hides the overlay until the next successful check. No game method is replaced and no game HUD state is modified. Tools/fix_visibility.py contains explicit Python 2.7 assembly plus simulated native API/state tests. Recovery: dist/backups/native-visibility. Runtime behavior still needs an in-game check, especially kill-camera and spectator transitions.
