"""Static compatibility checks against the installed client and dependency."""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from build_asia import ROOT, GAME, parse


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.get('consts', ()):
            yield from walk(child)


def names(model):
    return {name for code in walk(model) for name in code['names']} | {
        code['name'] for code in walk(model)}


def main():
    xml = ET.parse(GAME / 'version.xml').getroot()
    version, build = re.fullmatch(r'\s*v\.(\d+(?:\.\d+)+)\s+#(\d+)\s*', xml.findtext('version')).groups()
    checks = {}
    with zipfile.ZipFile(GAME / 'res/packages/scripts.pkg') as client:
        required = {
            'gui/impl/lobby/hangar/presenters/hangar_vehicle_params_presenter.pyc': (b'HangarVehicleParamsPresenter',),
            'gui/impl/lobby/hangar/presenters/vehicle_statistics_presenter.pyc': (b'VehiclesStatisticsPresenter', b'_onLoading'),
            'skeletons/gui/shared/__init__.pyc': (b'IItemsCache',),
            'gui/battle_control/controllers/feedback_events.pyc': (b'DAMAGE_LOG_SUMMARY', b'getDamage'),
            'frameworks/wulf/view/view_model.pyc': (b'ViewModel', b'transaction', b'_addViewModelProperty'),
        }
        for path, symbols in required.items():
            data = client.read('scripts/client/' + path)
            model = parse(data)[1]
            available = names(model)
            for symbol in symbols:
                checks[path + ':' + symbol.decode()] = symbol in available
    dependencies = sorted((GAME / 'mods' / version).glob('net.openwg.gameface_*.wotmod'))
    if len(dependencies) != 1:
        raise ValueError('Expected exactly one active OpenWG dependency')
    dependency = dependencies[0]
    with zipfile.ZipFile(dependency) as archive:
        meta = ET.fromstring(archive.read('meta.xml'))
        dep_version = meta.findtext('version')
        checks['gameface_version_at_least_1.2.2'] = tuple(map(int, dep_version.split('.'))) >= (1, 2, 2)
        module = parse(archive.read('res/scripts/client/openwg_gameface.pyc'))[1]
        inject = next(code for code in walk(module) if code['name'] == b'gf_mod_inject')
        checks['gf_mod_inject_signature'] = inject['header'][0] == 5 and inject['varnames'][:5] == (
            b'model', b'name', b'styles', b'scripts', b'modules')
        checks['ModelObserver_export'] = b'ModelObserver' in archive.read('res/gui/gameface/mods/libs/model.js')
        entries = set(archive.namelist())
        for path in (ROOT / 'res').rglob('*.js'):
            source = path.read_text(encoding='utf-8')
            for target in re.findall(r'from\s+["\']([^"\']+)["\']', source):
                if target.startswith('.'):
                    resolved = (path.parent / target).resolve()
                    relative = resolved.relative_to(ROOT).as_posix()
                    checks['js_import:' + relative] = resolved.is_file() or relative in entries
            result = subprocess.run(['node', '--input-type=module', '--check'], input=source,
                                    text=True, capture_output=True)
            checks['js_syntax:' + path.name] = result.returncode == 0
            if result.returncode:
                print(result.stderr)
    layouts = json.loads((ROOT / 'res/gui/gen_resources/com.phuochung94.moe_calculator.json').read_text())
    for entry in layouts:
        checks['layout:' + entry['parameters']['entrance']] = (ROOT / 'res' / entry['path'].removeprefix('coui://')).is_file()
    entry_path = ROOT / 'res/scripts/client/gui/mods/mod_moe_calculator.pyc'
    checks['display_name'] = b"phuochung94's MoE Calculator" in parse(entry_path.read_bytes())[1]['consts']
    for relative in ('bridge/mod_settings.pyc', 'bridge/battle_bridge.pyc', 'adapter/variant_overrides.pyc'):
        module = parse((ROOT / 'res/scripts/client/moe_calculator' / relative).read_bytes())[1]
        for code in walk(module):
            if code['name'] in (b'register', b'_seed', b'_apply', b'_on_changed', b'_on_reset',
                                b'set_position', b'set_bar_position', b'_on_drag',
                                b'_on_variant_toggle', b'_maybe_auto_toggle', b'save'):
                checks[relative + ':' + code['name'].decode()] = code['code'] == bytes.fromhex('64000053') + b'\x09' * (len(code['code'])-4)
            if code['name'] in (b'effective', b'toggle'):
                checks[relative + ':' + code['name'].decode()] = code['code'] == bytes.fromhex('7c010053') + b'\x09' * (len(code['code'])-4)
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'game': f'ASIA {version} #{build}', 'client': xml.findtext('meta/client').strip(),
              'dependency': dependency.name, 'dependency_sha256': hashlib.sha256(dependency.read_bytes()).hexdigest(),
              'checks': checks, 'all_passed': all(checks.values()), 'runtime_verified': False,
              'limitations': ['Static checks cannot prove inherited API behavior or in-game garage/battle rendering.']}
    (ROOT / 'dist/client-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    if not report['all_passed']:
        raise SystemExit('Compatibility checks failed; inspect report before packaging.')


if __name__ == '__main__':
    main()
