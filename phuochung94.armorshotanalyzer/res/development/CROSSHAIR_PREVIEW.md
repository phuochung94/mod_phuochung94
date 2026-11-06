# Native crosshair-settings preview

Latest HUD revision: Warhelios Bold from the installed game, brighter integrated
palette, regenerated sample. `render_crosshair_sample.py` regenerates preview
pixels directly from the CSS's first font and source DISPLAY_PALETTE. The older
PF DIN description below records the first implementation.

Diagnosis of the reported missing preview: on 2026-11-05 the installed package
had 18 files and SHA256 e1b7961ccf2a55683100011e14920f23c7e9cf59b1cb41f28dd22e58c1aac520,
without the native settings SWF. The exported 19-file preview build was not the
installed build. Installing the new output and restarting the client is needed
to validate the preview. This does not prove that the new SWF renders correctly.

Adds a static ArmorShotAnalyzer sample (armor 215, probability 72.3% - SPACED)
to the client's existing AimSettings display container in settingsWindow.swf.
The sample uses the current PF DIN Max Compressed Bold font, the 72.3% gradient
color, existing 22px/15px type sizes and offsets relative to the reticle center.
It is a demonstration; it does not calculate penetration on the settings screen.

The installed client's Arcade/Sniper preview placements share local coordinates
(509, 278). The bitmap sample is centered at that anchor and is a non-interactive
shape in the existing settings container. Thus native tab/window lifecycle and
UI scaling apply; there is no independent settings window or mod-list entry.
It belongs to the AimSettings screen, rather than separate Arcade/Sniper subtab
controllers; other aiming subtabs may also show the static sample.

`crosshair_preview.py` reads the original settingsWindow.swf directly from the
installed client's gui packages whenever windows_project.py packages/builds.
It adds a bitmap, shape and one placement; all ActionScript and existing tags
remain byte-identical. It validates target symbols and matching reticle anchors,
and stops if those assumptions no longer hold. Only the derivative settings SWF
is shipped at `res/gui/flash/settingsWindow.swf`; battle crosshair SWFs are untouched.
The normal battle overlay still uses the OpenWG already installed in the game.

The pre-rendered premultiplied ARGB sample is stored at
`resources/crosshair_preview.argb.zlib`. PNGs beside it are visual references,
excluded from runtime. Re-render the sample if font/layout is changed later.
The builder uses only the standard library; Pillow was used only to author the
sample from the existing bundled font.

Validation: original native tag preservation, original sprite-child preservation,
matching Arcade/Sniper anchors, bitmap dimensions, archive integrity, and 38
source + 38 bytecode regression tests. The raster sample was visually inspected.
No in-game validation has been performed; final native SWF rendering, subtab
layout, UI scaling and interaction still need a game trial. Another mod replacing
the same settingsWindow.swf can conflict with this resource override.

Backup: `backups/before_crosshair_preview_2026-11-05.zip`.
Build evidence: `client_inspection/crosshair_preview_build.json`.
