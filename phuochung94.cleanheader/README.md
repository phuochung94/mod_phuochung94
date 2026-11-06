# Clean Garage Header — 0.6.5

World of Tanks ASIA 2.4.1.1 #991. Hide the WoT Plus/Activate button and Premium Shop in the garage header. The order is player name, premium time, then the player icon, current server name and online count. The counter uses the same native text class as premium time and the native header separators/spacing, including UI scaling.

The complete show-tank feature has been removed from active source, resources and packaging: no tank replacement, vehicle rotation, test-vehicle list, custom tank click handler, or rotation/config files are loaded. The promotional vehicle uses the original game behavior.

## Installation

Close the game. Copy `dist/phuochung94.cleanheader-ASIA 2.4.1.1 #991.wotmod` into `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia\mods\2.4.1.1` without extracting it. Replace the previous file with the same name. Remove other older packages of this project from the active mods folder to avoid loading the removed show-tank feature.

Alternatively run `Install.ps1`. It installs the current package and moves recognized older packages to `mods/disabled/cleanheader`. No configuration is required.

The package uses the compact filename `phuochung94.cleanheader`. The build-time processing file is `src/cleanheader.py`. Its contents implement only the header changes. Historical backups are retained separately and are not packaged.

## Layout

The WoT Plus node, its internal separator, and the Premium Shop node are removed. An online counter is added after premium time. The original player-name and premium-account nodes remain in their original order. The native separator between the name and premium time remains. No CSS, fixed offsets, font sizes, icon dimensions, or UI scale values are changed. The online text uses the existing Premiums text class and native profile divider layout.

Online counts come from the game's existing server statistics controller. Only the current cluster count is displayed, not the region total. Updates follow native server-statistics events; no external API or additional polling is used. Until data is available, the counter shows the server name followed by `—`. Disconnecting clears the previous count. The UI-only Python module extends the header view model with one string property; it does not control vehicles.

The premium-account button continues to show the original premium status and expiry time, including the native inactive state. This mod does not change premium ownership or subscription data.

## Verification and limits

Automated checks validate node removal, preservation of native VIP markup, JavaScript syntax, and absence of vehicle-control or show-tank code in the package. Live in-game visual verification is still required, including long player names and different UI scales. Other mods replacing the same header bundle can conflict. Rebuild/review this resource override after game updates; the build refuses unrecognized component markers.

To uninstall, close the game and remove the WOTMOD file. For direct verification, open the normal garage: the left header should show player name, the standard separator, premium time, and `[player icon] ASIA1  12,345`. Plus and Premium Shop should be absent. The advertising tank should retain original behavior.

## Build

Run `python tools/build.py`, then `python tools/check.py`. Build packages the header `bundle.js`, the UI bridge `res/scripts/client/gui/mods/mod_cleanheader.pyc`, and `meta.xml`, without ZIP compression. Run `python tools/check_online.py` as well to check the online counter bridge.

The online counter now includes the native Contacts/player icon from the game footer atlases (`header_footer.footer_small`, `footer_large`, `footer_upscale`). The build reads the exact Contacts frames from the native footer bundle and validates the source PNG dimensions. Rendering uses the original sprite component and responsive/upscale hooks; no custom icon files or CSS size overrides are bundled.

The displayed format is `[player icon] ASIA1  12,345`, with two spaces between the server name and player count, no separator symbol, and no ping. The server name comes from the native connection manager, is shown in uppercase, and refreshes with the native population updates. If the server name is unavailable, a dash is shown instead of an invented server name.
