"""Package the native garage header override. Includes a UI-only native server statistics bridge."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cleanheader import RESOURCE, transform, parse_online_sprites
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
INFO = ET.parse(GAME / 'version.xml').getroot()
VERSION = re.search(r'v\.(\S+)\s+#(\d+)', INFO.findtext('version'))
PACKAGE_NAME = 'phuochung94.cleanheader-%s %s #%s.wotmod' % (
    INFO.findtext('meta/realm').strip(), VERSION[1], VERSION[2])
MOD_VERSION = '0.6.5'
ONLINE_RESOURCE = 'scripts/client/gui/mods/mod_cleanheader.pyc'


def _marshal(value):
    if value is None: return b'N'
    if isinstance(value, bytes): return b's' + struct.pack('<i', len(value)) + value
    if isinstance(value, tuple): return b'(' + struct.pack('<i', len(value)) + b''.join(map(_marshal, value))
    raise TypeError(type(value))


def loader(source):
    code = bytes([100,0,0,100,1,0,100,1,0,85,100,1,0,83])
    fields = (code, (source, None), (), (), (), (), b'mod_cleanheader.py', b'<module>')
    body = b'c' + b''.join(struct.pack('<i', value) for value in (0,0,3,0))
    body += b''.join(_marshal(value) for value in fields) + struct.pack('<i', 1) + _marshal(b'')
    return b'\x03\xf3\r\n' + struct.pack('<i', 0) + body


def main():
    with zipfile.ZipFile(GAME / 'res/packages/gui-part1.pkg') as archive:
        original = archive.read(RESOURCE)
    with zipfile.ZipFile(GAME / 'res/packages/gui-part3.pkg') as archive:
        sprites = parse_online_sprites(archive.read('gui/gameface/_dist/production/mono/hangar/footer/bundle.js').decode('utf-8'))
    for sprite in sprites.values():
        asset = 'gui/maps/icons/' + sprite['path'].replace('.', '/') + '.png'
        found = False
        for path in sorted((GAME / 'res/packages').glob('gui*.pkg')):
            with zipfile.ZipFile(path) as archive:
                if asset in archive.namelist():
                    png = archive.read(asset)
                    width, height = struct.unpack('>II', png[16:24])
                    if dict(w=width, h=height) != sprite['config']['meta']['size']:
                        raise ValueError('Native sprite atlas size mismatch: ' + asset)
                    found = True
                    break
        if not found:
            raise ValueError('Native Contacts icon atlas not found: ' + asset)
    patched = transform(original.decode('utf-8'), sprites).encode('utf-8')
    output = ROOT / 'res' / RESOURCE
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(patched)
    bridge = ROOT / 'res' / ONLINE_RESOURCE
    bridge.parent.mkdir(parents=True, exist_ok=True)
    bridge.write_bytes(loader((ROOT / 'src/mod_cleanheader.py').read_bytes()))
    active_files = {p.relative_to(ROOT / 'res').as_posix() for p in (ROOT / 'res').rglob('*') if p.is_file()}
    if active_files != {RESOURCE, ONLINE_RESOURCE}:
        raise ValueError('Unexpected resources in res; refusing to include stale show-tank code')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    metadata = ('<root><id>phuochung94.cleanheader</id><version>%s</version>'
                '<name>Clean Garage Header</name><description>Hide WoT Plus and Premium Shop; '
                'show native premium time and current-server online count beside the player name</description></root>') % MOD_VERSION
    with zipfile.ZipFile(dist / PACKAGE_NAME, 'w', zipfile.ZIP_STORED) as archive:
        archive.write(output, 'res/' + RESOURCE)
        archive.write(bridge, 'res/' + ONLINE_RESOURCE)
        archive.writestr('meta.xml', metadata)
    (dist / 'cleanheader.json').write_text(json.dumps({
        'package': PACKAGE_NAME, 'mod_version': MOD_VERSION, 'resource': RESOURCE,
        'source_sha256': hashlib.sha256(original).hexdigest(),
        'patched_sha256': hashlib.sha256(patched).hexdigest(),
        'show_tank_enabled': False, 'native_css_modified': False, 'online_counter': True, 'online_icon': sprites}, indent=2)+'\n', encoding='utf-8')
    print('Built:', dist / PACKAGE_NAME)


if __name__ == '__main__': main()
