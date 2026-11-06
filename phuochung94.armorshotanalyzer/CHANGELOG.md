# ArmorShotAnalyzer r993

Target client: World of Tanks ASIA 2.4.1.1 (build 991). Use r993 as the listing version.

- Modern HE estimates check the raw armor of each screen against the remaining penetration roll, then apply the client shield cost. Accumulated explosion absorption reaching the shell's maximum damage stops that path.
- Unexpected overlay failures write a traceback to the local game log. The first shot-overlay error is reported once per session to limit repeated messages.
- The startup log identifies ArmorShotAnalyzer r993. The installation filenames identify the target game client.
