# Update rehearsal: local Windows client

Requested by the user on 2026-11-03: perform the workflow as if the game updated.

- Client path: `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`.
- `version.xml`: ASIA v.2.4.1.1 #988, client 2649400, branch v2.4.1.
- `scripts.pkg` SHA256 baseline:
  `a1e931af72edf4a9327b2962ab68a0fd49776e99ee658089b20be872a07d12b3`.
- This is the first recorded client baseline. There is no previous client
  snapshot proving a version change, so no runtime change was invented.
- Inspected `res/packages/scripts.pkg` directly. Relevant game pyc files have
  Python 2.7 magic `03f30d0a` matching the mod.
- Disassembled the client's `_CrosshairShotResults` methods using its own
  `win64/python27.dll` in a separate Python 3 host process. Both shot-result
  methods retain `(cls, gunMarker, collisionsDetails, fullPiercingPower, shell,
  minPP, maxPP, entity)`. Ricochet, penetration and destructible-component
  helpers remain present. This is a partial static check, not a complete
  semantic comparison of all replacement code or Gameface lifecycle APIs.
- TankPartIndexes remains CHASSIS=0, HULL=1, TURRET=2, GUN=3.
- All 24 source tests and all 24 bytecode tests passed using client Python 2.7
  and its standard library extracted into the development-only inspection area.
  Tests use mocked game APIs; they do not demonstrate in-game compatibility.
- `mods/2.4.1.1` and `res_mods/2.4.1.1` contain only readme files at inspection.
  OpenWG Gameface is not present in that mods directory; its compatible version
  is required before an in-game trial.
- Existing python.log is from 2026-08-30; it is not evidence of this build working.
- Packaged existing customized runtime as 2.3.0, preserving prior 2.2.0 package.
  No runtime logic changed. No mod was installed and the game was not launched.

Reproduction with a working Python 3 interpreter:

```
python -B res/development/inspect_client.py
python -B res/development/inspect_client.py --test
python -B res/development/inspect_client.py --test --bytecode
```

`inspect_client.py` is a Windows diagnostic helper for this local trusted client;
it loads the game's Python DLL and reads its bytecode without starting the game.
Do not use with untrusted DLLs/bytecode. Generated inspection files stay under
development and are excluded from runtime packages. A working Python 3 is bundled
at `C:\Users\phuochung94\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
