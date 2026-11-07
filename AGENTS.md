## Gameface remains separate — latest user requirement

The personal combined mods_<REALM version #build>.wotmod must contain ONLY the user mod payloads. NEVER merge OpenWG Gameface runtime into it. Keep net.openwg.gameface_<compatible version>.wotmod as a separate file alongside it in C:\mod_phuochung94\.wotmod. Install the combined package plus exactly one separate Gameface package; do not also install the constituent individual mods. This supersedes every older instruction to embed Gameface in the combined archive. Standalone WGmods releases and distribution ZIPs keep their existing separate-dependency behavior.

## Current output directory — user confirmed

All projects export standalone .wotmod files, the combined mods_<REALM version #build>.wotmod, separate Gameface downloads and distribution ZIPs to `C:\mod_phuochung94\.wotmod`. This is a DIRECTORY, not a filename. Project sources/tools remain in C:\mod_phuochung94; backups and reports stay in their existing locations. This instruction supersedes every older output path below. Shared helpers remain in the parent directory; use publish_mod.py after compatibility checks and build_all_mods.py for the combined package.

When `cập nhật mod` is invoked, FIRST check official OpenWG Gameface releases and the available dependency version; then detect the game version and check compatibility before making needed fixes, verifying and packaging all mod projects. Do not permanently pin Gameface 1.2.2.

# Shared World of Tanks mod workflow

The user commands `cập nhật mod` to run compatibility checks, make needed fixes, verify and package ALL World of Tanks mod projects on this machine. Otherwise wait for `làm việc` before executing pending work; explicit memory-save requests authorize the save itself.

Game: `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`. Read version.xml each session. Check official OpenWG releases at https://gitlab.com/openwg/wot.gameface/-/releases and the required interfaces; never pin dependency versions permanently. Preserve each project's approved customizations and backups.

After current checks pass, run `publish_mod.py <project path> --checks-passed` using Python 3. Outputs go directly to `C:\mod_phuochung94`, as `phuochung94.<user-specified mod name>-<REALM version #build>.wotmod`, with root meta.xml (author phuochung94) alongside res/. Keep metadata original credits. Do not publish development/backup files. Do not confuse fixture/static checks with in-game verification. Do not install/launch game unless requested.

After updating and publishing all individual mods, also run build_all_mods.py to create mods_<REALM version #build>.wotmod in C:\mod_phuochung94. This user-requested combined archive merges all current mod runtime files plus exactly one checked Gameface runtime, with root meta.xml author phuochung94. This combined-package requirement supersedes separate-only dependency rules for this artifact; keep standalone releases available. Refuse conflicting resource bytes, verify source hashes, CRC and ZIP_STORED. Tell the user to install the combined package instead of constituent standalone mods and Gameface, avoiding duplicate loaders. Never claim in-game interoperability without testing.

## Release purposes confirmed by the user

Every full mod update must produce BOTH outputs in C:\mod_phuochung94:
- Individual phuochung94.<user-specified mod name>-<REALM version #build>.wotmod packages, for the user to update each mod on WGmods. Keep each mod independent; Gameface stays a separate dependency for these individual releases.
- One mods_<REALM version #build>.wotmod combined package, for the user's personal local gameplay installation, merging all current mod runtime payloads and exactly one checked Gameface runtime.

Use the actual installed game version and build. Preserve these distinct purposes in future projects and updates. Preparing the packages does not authorize uploading to WGmods or installing into the game.
