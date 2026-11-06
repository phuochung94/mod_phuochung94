# Upstream source reference

## Local original 2.2.0 source on Windows

User-provided path (2026-11-03):
`C:\pademinune-AP_Calculator-2.2.0\Armor-Penetration-Calculator-2.2.0`.
Directory exists; `src/res/scripts/client/ap_calculator/debug.py` declares
`VERSION = "2.2.0"`. No Git commit identity has been verified for this directory.

The user clarified that this source is suitable only for their current game
version and will no longer work after a game version update. Treat it as a
historical baseline, not as a compatible foundation for future clients. The
exact current client version has not yet been recorded here. For a future
update, obtain upstream source suitable for that client, compare the actual
game APIs, then port the approved customizations and validate compatibility.
The pinned 2.2.1 snapshot below is also only a reference; its compatibility with
a future client must not be assumed.

Use this original source as a reference for the 2.2.0 baseline when maintaining
the customized runtime or comparing future upstream changes. Relevant files:

- `src/res/scripts/client/ap_calculator/core/ap_hooks.py` and `ap_math.py`:
  shot-result hooks and penetration math.
- `src/res/scripts/client/ap_calculator/gui/`: configuration and Gameface integration.
- `src/res/gui/AP_Calculator_2/gameface/`: overlay HTML, JS and CSS.
- `src/res/scripts/client/gui/mods/mod_AP_Calculator.py`: original entry point.
- `build/build.py`: original build script, for reference only.

This external directory is not included in the Windows project backup. Preserve
it separately when moving machines. Do not overwrite customized runtime with an
unmodified build; apply `../MOD_CUSTOMIZATIONS.md` and follow
`GAME_UPDATE_COMPATIBILITY.md`. This reference has not changed runtime or packages.

## Pinned upstream 2.2.1 snapshot

Repository: https://github.com/justinnitoi/Armor-Penetration-Calculator.git
Branch: v2
Commit: 97e3b967a3d3465a203c3dab615ee17672ade729
Retrieved: 2026-11-03
Upstream debug.VERSION: 2.2.1
Snapshot: development/upstream/97e3b967a3d3/
License: GPL-3.0 (included in snapshot).

This is a reference snapshot. It has not replaced the customized 2.2.0 runtime
or the packaged wotmod. The upstream mod provides shot-result calculation
hooks, but no firing-input hook. Any zero-penetration fire-blocking feature
still needs an implementation against the matching game client's firing path,
with tests for stale predictions, shell changes, non-vehicle aims and HE.

The user canceled the zero-penetration fire-blocking feature. Do not implement
or restore it during updates unless explicitly requested again.
