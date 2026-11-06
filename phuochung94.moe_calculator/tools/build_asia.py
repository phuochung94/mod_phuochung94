"""Patch the existing Python 2.7 region constant and build a stored wotmod.

Run with Python 3. Never execute or recompile the game's Python 2.7 bytecode.
"""
import hashlib
import io
import json
import re
import shutil
import struct
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
OUTPUT_DIR = Path(r'C:\pademinune-AP_Calculator-2.2.0')
TARGET = ROOT / 'res/scripts/client/moe_calculator/adapter/moe_wgapi.pyc'


class Reader:
    """Read Python 2.7 marshal data, preserving string offsets and interned refs."""
    def __init__(self, data):
        self.data, self.pos, self.refs, self.strings = data, 8, [], []
        self.code_records = []

    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise ValueError('Invalid marshal length')
        out = self.data[self.pos:self.pos+n]
        self.pos += n
        return out

    def integer(self):
        return struct.unpack('<i', self.take(4))[0]

    def read(self):
        start = self.pos
        tag = self.take(1)
        if tag in (b'N', b'F', b'T', b'S', b'.', b'0'):
            return ('literal', tag)
        if tag == b'i':
            return self.integer()
        if tag == b'I':
            return ('int64', self.take(8))
        if tag == b'l':
            n = self.integer()
            return ('long', n, self.take(abs(n)*2))
        if tag in (b'g', b'y'):
            return (tag, self.take(8 if tag == b'g' else 16))
        if tag in (b'f', b'x'):
            return (tag, tuple(self.take(self.take(1)[0]) for _ in range(1 if tag == b'f' else 2)))
        if tag in (b's', b't', b'u'):
            value = self.take(self.integer())
            self.strings.append((start, tag, value))
            if tag == b't':
                self.refs.append(value)
            return value
        if tag == b'R':
            return self.refs[self.integer()]
        if tag in (b'(', b'[', b'<', b'>'):
            return tuple(self.read() for _ in range(self.integer()))
        if tag == b'{':
            result = []
            while True:
                key = self.read()
                if key == ('literal', b'0'):
                    return ('dict', tuple(result))
                result.append((key, self.read()))
        if tag == b'c':
            result = {'header': tuple(self.integer() for _ in range(4))}
            for field in ('code', 'consts', 'names', 'varnames', 'freevars', 'cellvars', 'filename', 'name'):
                position = self.pos
                result[field] = self.read()
                if field == 'code':
                    code_offset = position + 5
            result['firstlineno'] = self.integer()
            result['lnotab'] = self.read()
            self.code_records.append((result, code_offset, len(result['code'])))
            return result
        raise ValueError('Unsupported marshal tag %r at %d' % (tag, start))


def parse(data):
    if data[:4] != bytes.fromhex('03f30d0a'):
        raise ValueError('Expected Python 2.7 bytecode')
    reader = Reader(data)
    code = reader.read()
    if reader.pos != len(data):
        raise ValueError('Unparsed trailing bytes')
    return reader, code


def region_constant(code):
    raw, pos, previous = code['code'], 0, None
    while pos < len(raw):
        op = raw[pos]
        arg = struct.unpack('<H', raw[pos+1:pos+3])[0] if op >= 90 else None
        if op == 90 and code['names'][arg] == b'REGION':
            if previous is None or previous[0] != 100:
                raise ValueError('REGION is not a direct LOAD_CONST assignment')
            return previous[1]
        previous = (op, arg)
        pos += 3 if op >= 90 else 1
    raise ValueError('REGION assignment not found')


def main():
    version_xml = ET.parse(GAME / 'version.xml').getroot()
    version, build = re.fullmatch(r'\s*v\.(\d+(?:\.\d+)+)\s+#(\d+)\s*', version_xml.findtext('version')).groups()
    realm = version_xml.findtext('meta/realm').strip()
    if realm != 'ASIA':
        raise ValueError('This build targets ASIA only')
    client_report_path = ROOT / 'dist/client-check.json'
    client_report = json.loads(client_report_path.read_text(encoding='utf-8')) if client_report_path.exists() else None
    if client_report is not None and (not client_report['all_passed'] or client_report['game'] != '%s %s #%s' % (realm, version, build)):
        raise ValueError('Client checks failed or target version changed; run tools/verify_client.py')
    original = TARGET.read_bytes()
    reader, code = parse(original)
    index = region_constant(code)
    current = code['consts'][index]
    backup = ROOT / 'dist/backups/moe_wgapi.original.pyc'
    backup.parent.mkdir(parents=True, exist_ok=True)
    if current == b'eu':
        candidates = [(offset, tag) for offset, tag, val in reader.strings if val == b'eu']
        if len(candidates) != 1:
            raise ValueError('Region string is ambiguous')
        offset, tag = candidates[0]
        patched = original[:offset+1] + struct.pack('<i', 4) + b'asia' + original[offset+7:]
        _, after = parse(patched)
        expected = dict(code)
        constants = list(code['consts'])
        constants[index] = b'asia'
        expected['consts'] = tuple(constants)
        if after != expected or region_constant(after) != index:
            raise ValueError('Patch changed data other than REGION')
        if backup.exists() and backup.read_bytes() != original:
            raise ValueError('Backup conflict')
        if not backup.exists():
            backup.write_bytes(original)
        TARGET.write_bytes(patched)
    elif current != b'asia':
        raise ValueError('Unexpected region')
    # Check client modules/symbols without importing or executing client code.
    checks = {}
    with zipfile.ZipFile(GAME / 'res/packages/scripts.pkg') as client:
        for path, symbol in (
            ('gui/impl/lobby/hangar/presenters/hangar_vehicle_params_presenter.pyc', b'HangarVehicleParamsPresenter'),
            ('gui/impl/lobby/hangar/presenters/vehicle_statistics_presenter.pyc', b'VehiclesStatisticsPresenter'),
            ('gui/shared/items_cache.pyc', b'IItemsCache'),
            ('gui/battle_control/controllers/feedback_events.pyc', b'DAMAGE_LOG_SUMMARY'),
        ):
            name = 'scripts/client/' + path
            checks[name] = symbol in client.read(name)
    if not all(checks.values()):
        raise ValueError('Client symbol check failed: %r' % checks)
    # Every shipped module must remain readable Python 2.7 marshal data.
    pyc_count = 0
    for path in (ROOT / 'res').rglob('*.pyc'):
        parse(path.read_bytes())
        pyc_count += 1
    output = OUTPUT_DIR / ('phuochung94.moe_calculator-ASIA %s #%s.wotmod' % (version, build))
    if output.exists():
        old = output.read_bytes()
        old_hash = hashlib.sha256(old).hexdigest()[:12]
        old_path = backup.parent / (output.stem + '-' + old_hash + '.wotmod')
        if not old_path.exists():
            shutil.copy2(output, old_path)
    files = sorted(p for p in (ROOT / 'res').rglob('*') if p.is_file()) + [ROOT / 'meta.xml']
    temporary = output.with_suffix('.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as package:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            package.writestr(info, path.read_bytes())
    with zipfile.ZipFile(temporary) as package:
        assert package.testzip() is None
        assert len(package.infolist()) == len(files)
        for info in package.infolist():
            assert info.compress_type == zipfile.ZIP_STORED
            assert package.read(info) == (ROOT / info.filename).read_bytes()
    temporary.replace(output)
    report = {
        'built_at_utc': datetime.now(timezone.utc).isoformat(),
        'game': '%s %s #%s' % (realm, version, build),
        'change': 'REGION constant eu -> asia in existing Python 2.7 bytecode; instructions and all other marshal fields unchanged',
        'endpoint': 'https://api.worldoftanks.asia/wot/tanks/mastery/',
        'client_symbol_checks': checks,
        'parsed_python27_modules': pyc_count,
        'package': output.name, 'output_path': str(output), 'entries': len(files),
        'compression': 'ZIP_STORED',
        'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'runtime_verified': False,
        'namespace': 'phuochung94',
        'client_check': client_report,
        'fixed_settings': json.loads((ROOT / 'dist/fixed-settings-report.json').read_text(encoding='utf-8')) if (ROOT / 'dist/fixed-settings-report.json').exists() else None,
        'api_check': json.loads((ROOT / 'dist/api-check.json').read_text(encoding='utf-8')) if (ROOT / 'dist/api-check.json').exists() else None,
        'limitations': ['No in-game garage/battle verification yet.',
                        'Matching client symbols does not prove API signatures or runtime compatibility.',
                        'Upstream main is 9.0.0; it was inspected only and not substituted for the supplied 8.0.0.'],
    }
    (ROOT / 'dist/compatibility-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
