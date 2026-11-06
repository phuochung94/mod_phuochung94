# Compact overlay update

- Probability text now uses `72.3% - SPACED`; shell name and penetration mm
  are removed from presentation. Existing status and unknown-data handling stay.
- Disable AngleLabelSettings at installation and before invoking the original
  shot result, hide any stale angle, and send angleVisible=False on display.
  Base configuration/color bytecode is preserved.
- Confirmed client getShotResult dispatches HIGH_EXPLOSIVE with MODERN mechanics
  to the modern HE method; the existing overlay already wraps both HE branches.
  HESH is handled using the shell supplied by the game, not invented HEST physics.
  Added mocked HESH tests for body penetration, RNG and shield behavior; no new
  penetration formula was required or introduced.
- 30 source and 30 compiled-bytecode tests passed with client Python 2.7 DLL.
- Rebuilt both maintained extension modules. Previous versions are backed up in
  `backups/before_compact_overlay_2026-11-04/`.
- No in-game test or installation performed. Client remains ASIA 2.4.1.1 #988.
