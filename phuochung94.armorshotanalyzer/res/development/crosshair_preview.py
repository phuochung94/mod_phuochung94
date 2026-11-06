"""Add a static overlay sample to the native settings preview; stdlib only.

Rebuild from the installed client SWF on every package, retaining original
ActionScript and display tags. No battle SWF is modified.
"""
import hashlib
import json
from pathlib import Path
import struct
import zlib
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')

class Bits:
    def __init__(self, data=b''):
        self.bits = ''.join(format(b, '08b') for b in data)
        self.pos = 0

    def get(self, count, signed=False):
        value = int(self.bits[self.pos:self.pos + count] or '0', 2)
        self.pos += count
        return value - (1 << count) if signed and value & (1 << (count - 1)) else value

    def put(self, value, count):
        self.bits += format(value & ((1 << count) - 1), '0{}b'.format(count))

    def bytes(self):
        padded = self.bits + '0' * (-len(self.bits) % 8)
        return bytes(int(padded[n:n+8], 2) for n in range(0, len(padded), 8))

def tags(data, offset=0):
    while offset < len(data):
        begin = offset
        header = struct.unpack_from('<H', data, offset)[0]; offset += 2
        size = header & 63
        if size == 63:
            size = struct.unpack_from('<I', data, offset)[0]; offset += 4
        if offset + size > len(data):
            raise RuntimeError('Truncated SWF tag')
        yield header >> 6, data[offset:offset+size], data[begin:offset+size]
        offset += size

def tag(kind, body):
    return struct.pack('<HI', (kind << 6) | 63, len(body)) + body

def rect(width, height):
    bits = Bits(); size = max(width, height).bit_length() + 1
    bits.put(size, 5)
    for value in (0, width, 0, height): bits.put(value, size)
    return bits.bytes()

def matrix(x=0, y=0, scale=None):
    bits = Bits(); bits.put(scale is not None, 1)
    if scale is not None:
        value = int(scale * 65536); size = value.bit_length() + 1
        bits.put(size, 5); bits.put(value, size); bits.put(value, size)
    bits.put(0, 1)
    size = max(abs(x), abs(y)).bit_length() + 1
    bits.put(size, 5); bits.put(x, size); bits.put(y, size)
    return bits.bytes()

def placement(body):
    flags, flags2 = body[0], body[1]
    pos = 4
    if flags2 & 8:
        pos = body.index(b'\0', pos) + 1
    if flags & 2: pos += 2
    if not flags & 4: raise RuntimeError('Crosshair placement has no matrix')
    bits = Bits(body[pos:])
    if bits.get(1):
        size = bits.get(5); bits.get(size); bits.get(size)
    if bits.get(1):
        size = bits.get(5); bits.get(size); bits.get(size)
    size = bits.get(5)
    return bits.get(size, True), bits.get(size, True)

def shape(shape_id, bitmap_id):
    body = struct.pack('<H', shape_id) + rect(5120, 5120)
    body += b'\x01\x41' + struct.pack('<H', bitmap_id) + matrix(scale=20)
    body += b'\x00'  # no line styles
    bits = Bits(); bits.put(1, 4); bits.put(0, 4)
    bits.put(5, 6); bits.put(1, 5); bits.put(0, 1); bits.put(0, 1); bits.put(1, 1)
    for dx, dy in ((5120, 0), (0, 5120), (-5120, 0), (0, -5120)):
        size = 14
        bits.put(1, 1); bits.put(1, 1); bits.put(size - 2, 4)
        bits.put(0, 1); bits.put(bool(dy), 1); bits.put(dx or dy, size)
    bits.put(0, 6)
    return tag(32, body + bits.bytes())

def build():
    originals = []
    for package in sorted((GAME / 'res/packages').glob('gui*.pkg')):
        with ZipFile(package) as archive:
            if 'gui/flash/settingsWindow.swf' in archive.namelist():
                originals.append(archive.read('gui/flash/settingsWindow.swf'))
    if len(originals) != 1: raise RuntimeError('Expected one native settings SWF')
    original = originals[0]
    if original[:3] not in (b'CWS', b'FWS'): raise RuntimeError('Unsupported SWF compression')
    data = original[:8] + zlib.decompress(original[8:]) if original[:3] == b'CWS' else original
    if len(data) != struct.unpack_from('<I', original, 4)[0]: raise RuntimeError('SWF size mismatch')
    offset = 8 + (5 + 4 * (data[8] >> 3) + 7) // 8 + 4
    entries = list(tags(data, offset)); symbols = {}; used = set()
    definitions = {2,6,7,10,11,14,20,21,22,32,33,34,35,36,37,39,46,48,60,61,62,73,75,83,84,87,90,91}
    for kind, body, _ in entries:
        if kind in definitions: used.add(struct.unpack_from('<H', body)[0])
        if kind in (57, 71):
            pos = body.index(b'\0') + 1 + (2 if kind == 71 else 0)
            count = struct.unpack_from('<H', body, pos)[0]; pos += 2
            for _ in range(count):
                used.add(struct.unpack_from('<H', body, pos)[0]); pos += 2
                pos = body.index(b'\0', pos) + 1
        if kind == 76:
            pos = 2
            for _ in range(struct.unpack_from('<H', body)[0]):
                sid = struct.unpack_from('<H', body, pos)[0]; pos += 2
                end = body.index(b'\0', pos); symbols[sid] = body[pos:end].decode(); pos = end+1
                used.add(sid)
    targets = [sid for sid, name in symbols.items() if name == 'AimSettings']
    if len(targets) != 1: raise RuntimeError('Native AimSettings structure changed')
    bitmap_id, shape_id = max(used) + 1, max(used) + 2
    if shape_id > 65535: raise RuntimeError('SWF character IDs exhausted')
    pixels = (HERE / 'resources/crosshair_preview.argb.zlib').read_bytes()
    if len(zlib.decompress(pixels)) != 256 * 256 * 4: raise RuntimeError('Invalid preview pixels')
    additions = tag(36, struct.pack('<HBHH', bitmap_id, 5, 256, 256) + pixels) + shape(shape_id, bitmap_id)
    rebuilt = []; anchor = None; changes = 0
    for kind, body, raw in entries:
        if kind == 39 and struct.unpack_from('<H', body)[0] == targets[0]:
            children = list(tags(body, 4))
            positions = [placement(b) for k, b, _ in children
                         if k == 70 and (b'arcadeCrosshair\0' in b or b'sniperCrosshair\0' in b)]
            if len(positions) != 2 or positions[0] != positions[1]:
                raise RuntimeError('Native preview anchors changed')
            anchor = positions[0]
            depth = max(struct.unpack_from('<H', b, 2 if k == 70 else 1)[0]
                        for k, b, _ in children if k in (26, 70)) + 1
            if depth > 65535: raise RuntimeError('SWF depth exhausted')
            place = tag(26, b'\x26' + struct.pack('<HH', depth, shape_id)
                        + matrix(anchor[0]-2560, anchor[1]-2560) + b'armorShotAnalyzerPreview\0')
            inserted = False; new_children = []
            for k, b, child_raw in children:
                if k == 1 and not inserted: new_children.append(place); inserted = True
                new_children.append(child_raw)
            if not inserted: raise RuntimeError('No preview frame')
            if [raw for raw in new_children if raw != place] != [raw for _,_,raw in children]:
                raise RuntimeError('Existing preview display tags changed')
            rebuilt.append(additions + tag(39, body[:4] + b''.join(new_children))); changes += 1
        else: rebuilt.append(raw)
    if changes != 1: raise RuntimeError('Preview sprite not found')
    result = data[:offset] + b''.join(rebuilt)
    result = b'FWS' + result[3:4] + struct.pack('<I', len(result)) + result[8:]
    # All original top-level tags except the one preview sprite remain byte-identical.
    expected = [raw for k,b,raw in entries if not (k == 39 and struct.unpack_from('<H', b)[0] == targets[0])]
    actual = [raw for k,b,raw in tags(result, offset)
              if not (k in (36,32) and struct.unpack_from('<H', b)[0] in (bitmap_id,shape_id))
              and not (k == 39 and struct.unpack_from('<H', b)[0] == targets[0])]
    if actual != expected: raise RuntimeError('Unrelated SWF tags changed')
    target = HERE.parent / 'gui/flash/settingsWindow.swf'; target.parent.mkdir(exist_ok=True)
    target.write_bytes(b'CWS' + result[3:8] + zlib.compress(result[8:]))
    report = dict(native_sha256=hashlib.sha256(original).hexdigest(), anchor_twips=anchor,
                  preview_sprite=targets[0], original_actionscript_unchanged=True,
                  limitations='Static sample in native AimSettings, not a live penetration calculation')
    report_dir = HERE / 'client_inspection'; report_dir.mkdir(exist_ok=True)
    (report_dir / 'crosshair_preview_build.json').write_text(json.dumps(report, indent=2))
    print('Built native crosshair-settings sample; anchor:', tuple(v / 20.0 for v in anchor))
    return target

if __name__ == '__main__': build()
