import struct, zlib
from pathlib import Path
from zipfile import ZipFile
with ZipFile(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia\res\packages\gui-part4.pkg') as z:
    data = z.read('gui/flash/settingsWindow.swf')
data = data[:8] + zlib.decompress(data[8:]) if data[:3] == b'CWS' else data
start = 8 + (5 + 4 * (data[8] >> 3) + 7) // 8 + 4
def tags(buf, start=0):
    while start < len(buf):
        h = struct.unpack_from('<H', buf, start)[0]; start += 2
        size = h & 63; kind = h >> 6
        if size == 63: size = struct.unpack_from('<I', buf, start)[0]; start += 4
        yield kind, buf[start:start+size]
        start += size
symbols = {}
for kind, body in tags(data, start):
    if kind == 76:
        p = 2
        for _ in range(struct.unpack_from('<H', body)[0]):
            sid = struct.unpack_from('<H', body, p)[0]; p += 2
            end = body.index(b'\0', p); symbols[sid] = body[p:end].decode(); p = end+1
for kind, body in tags(data, start):
    if kind == 39:
        sid = struct.unpack_from('<H', body)[0]
        name = symbols.get(sid, '')
        if any(k in name.lower() for k in ('arcade','sniper','aim','settingwindow')):
            print('SPRITE', sid, name)
            for k, b in tags(body, 4):
                if k in (26,70):
                    print('PLACE', k, b.hex())
print('SYMBOLS', [(k,v) for k,v in symbols.items() if any(t in v.lower() for t in ('arcade','sniper','aim','settingwindow'))])
