## Gameface remains separate — latest user requirement

The personal combined mods_<REALM version #build>.wotmod must contain ONLY the user mod payloads. NEVER merge OpenWG Gameface runtime into it. Keep net.openwg.gameface_<compatible version>.wotmod as a separate file alongside it in C:\mod_phuochung94\.wotmod. Install the combined package plus exactly one separate Gameface package; do not also install the constituent individual mods. This supersedes every older instruction to embed Gameface in the combined archive. Standalone WGmods releases and distribution ZIPs keep their existing separate-dependency behavior.

## Current output directory — user confirmed

All projects export standalone .wotmod files, the combined mods_<REALM version #build>.wotmod, separate Gameface downloads and distribution ZIPs to `C:\mod_phuochung94\.wotmod`. This is a DIRECTORY, not a filename. Project sources/tools remain in C:\mod_phuochung94; backups and reports stay in their existing locations. This instruction supersedes every older output path below. Shared helpers remain in the parent directory; use publish_mod.py after compatibility checks and build_all_mods.py for the combined package.

When `cập nhật mod` is invoked, FIRST check official OpenWG Gameface releases and the available dependency version; then detect the game version and check compatibility before making needed fixes, verifying and packaging all mod projects. Do not permanently pin Gameface 1.2.2.

## Current shared packaging rule (2026-11-07)

User instructions supersede older output paths: after compatibility checks pass, publish to `C:\mod_phuochung94` using `publish_mod.py` in that directory with this project path and `--checks-passed`. It includes author phuochung94 in root meta.xml alongside res/, ZIP_STORED, game-version filename, CRC/payload verification and required separate Gameface bundles. Preserve original authorship. All earlier output directory references are historical. Do not install or launch the game without explicit instruction.

