"""Lock supplied Python 2.7 mod to its original defaults, without executing it."""
import hashlib
import json
from build_asia import ROOT, parse

BASE = ROOT / 'res/scripts/client/moe_calculator'
NOOP = bytes.fromhex('64000053')  # LOAD_CONST None; RETURN_VALUE
RETURN_DEFAULT_VARIANT = bytes.fromhex('7c010053')  # LOAD_FAST 1; RETURN_VALUE
PATCHES = {
    'bridge/mod_settings.pyc': {
        name: NOOP for name in (
            'register', '_seed', '_apply', '_on_changed', '_on_reset',
            'set_position', 'set_bar_position',
        )
    },
    'bridge/battle_bridge.pyc': {
        name: NOOP for name in ('_on_drag', '_on_variant_toggle', '_maybe_auto_toggle')
    },
    'adapter/variant_overrides.pyc': {
        'effective': RETURN_DEFAULT_VARIANT,
        'toggle': RETURN_DEFAULT_VARIANT,
        'save': NOOP,
    },
}


def main():
    report = {'mode': 'fixed_original_defaults', 'patched_functions': {},
              'defaults': {'garage': True, 'battle_overlay': True,
                           'counted_assistance': True, 'battle_progress_bar': False},
              'menu_registration': False, 'saved_settings_loaded': False,
              'position_editing': False, 'variant_switching': False,
              'runtime_verified': False}
    for relative, replacements in PATCHES.items():
        path = BASE / relative
        original = path.read_bytes()
        reader, before = parse(original)
        patched = bytearray(original)
        found = set()
        expected_codes = {}
        for code, offset, size in reader.code_records:
            name = code['name'].decode('ascii')
            if name not in replacements:
                continue
            if name in found:
                raise ValueError('Ambiguous function: ' + name)
            found.add(name)
            replacement = replacements[name]
            if replacement == NOOP and code['consts'][0] != ('literal', b'N'):
                raise ValueError('Expected None at const 0')
            if replacement == RETURN_DEFAULT_VARIANT and code['varnames'][1] != b'default_variant':
                raise ValueError('Expected default_variant at local 1')
            if size < len(replacement) or code['header'][2] < 1:
                raise ValueError('Invalid replacement size/stack')
            payload = replacement + b'\x09' * (size-len(replacement))  # unreachable NOP
            patched[offset:offset+size] = payload
            expected_codes[name] = payload
        if found != set(replacements):
            raise ValueError('Missing functions: %r' % (set(replacements)-found))
        # Verify full marshal structures: only selected function instructions may differ.
        after_reader, after = parse(bytes(patched))
        for code, _, _ in reader.code_records:
            name = code['name'].decode('ascii')
            if name in expected_codes:
                code['code'] = expected_codes[name]
        if before != after:
            raise ValueError('Unexpected marshal field changes')
        for code, _, _ in after_reader.code_records:
            name = code['name'].decode('ascii')
            if name in expected_codes and code['code'] != expected_codes[name]:
                raise ValueError('Replacement verification failed')
        if bytes(patched) != original:
            backup = ROOT / 'dist/backups/fixed-defaults' / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists() and backup.read_bytes() != original:
                raise ValueError('Backup conflict: ' + str(backup))
            if not backup.exists():
                backup.write_bytes(original)
            path.write_bytes(patched)
        report['patched_functions'][relative] = sorted(found)
    js = ROOT / 'res/gui/gameface/mods/phuochung94/MoECalculator/MoECalculator.js'
    source = js.read_bytes()
    marker = b'function installDrag() {'
    guard = b'\n    return; // Fixed-default build: position editing is disabled.'
    if marker + guard not in source:
        if source.count(marker) != 1:
            raise ValueError('Expected one installDrag function')
        backup = ROOT / 'dist/backups/fixed-defaults/MoECalculator.js'
        if backup.exists() and backup.read_bytes() != source:
            raise ValueError('JS backup conflict')
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(source)
        js.write_bytes(source.replace(marker, marker+guard))
    report['js_drag_handler_disabled'] = marker+guard in js.read_bytes()
    # The module initialization (including DEFAULTS and _settings) is untouched.
    report['verification'] = 'Full marshal equality except 13 selected function bodies; module defaults and signatures preserved.'
    (ROOT / 'dist/fixed-settings-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
