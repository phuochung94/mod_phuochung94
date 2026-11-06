"""Python 2.7: check migrated imports, resources and unchanged base instructions."""
import dis
import json
import marshal
import os
import re
import types
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(ROOT, 'res/scripts/client')
mapping = [('ap_calculator_2', 'armorshotanalyzer'),
           ('AP_Calculator_2', 'ArmorShotAnalyzer'),
           ('ap_calculator', 'armorshotanalyzer'), ('APBattle', 'ArmorShotAnalyzerBattle')]
mapping += [('ap_' + s, 'armorshotanalyzer_' + s) for s in
            ('shell_info', 'gameface_api', 'constants', 'config', 'logger', 'hooks', 'math', 'gui')]
def renamed(text):
    for old, new in mapping:
        text = text.replace(old, new)
    return text

def compare(old, new):
    if isinstance(old, types.CodeType):
        assert old.co_code == new.co_code, old.co_name
        assert (old.co_argcount, old.co_flags, old.co_stacksize, old.co_nlocals) == (
            new.co_argcount, new.co_flags, new.co_stacksize, new.co_nlocals)
        assert tuple(renamed(s) for s in old.co_names) == new.co_names
        compare(old.co_consts, new.co_consts)
    elif isinstance(old, tuple):
        assert len(old) == len(new)
        for a, b in zip(old, new):
            compare(a, b)
    elif isinstance(old, basestring):
        assert renamed(old) == new
    else:
        assert old == new

def module_exists(name):
    path = os.path.join(CLIENT, *name.split('.'))
    return os.path.isfile(path + '.pyc') or os.path.isfile(os.path.join(path, '__init__.pyc'))

def check_imports(code):
    # IMPORT_NAME references the co_names table; no executing game imports.
    index = 0
    while index < len(code.co_code):
        op = ord(code.co_code[index]); index += 1
        if op >= dis.HAVE_ARGUMENT:
            arg = ord(code.co_code[index]) | ord(code.co_code[index + 1]) << 8
            index += 2
            if op == dis.opmap['IMPORT_NAME']:
                name = code.co_names[arg]
                if name.startswith('armorshotanalyzer'):
                    assert module_exists(name), name
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            check_imports(value)

count = 0
with zipfile.ZipFile(os.path.join(ROOT,
        'res/development/backups/before_namespace_rename_2026-11-05.zip')) as archive:
    for name in archive.namelist():
        if name.startswith('res/scripts/') and name.endswith('.pyc'):
            if '/settings_gui/' in name or name.endswith(('ap_logger.pyc','ap_math.pyc')):
                assert not os.path.exists(os.path.join(ROOT, renamed(name)))
                continue
            path = os.path.join(ROOT, renamed(name))
            old = marshal.loads(archive.read(name)[8:])
            new = marshal.loads(open(path, 'rb').read()[8:])
            check_imports(new)
            if not name.endswith(('ap_shell_info.pyc', 'mod_armorshotanalyzer.pyc',
                                  'ap_calculator/__init__.pyc', 'core/__init__.pyc',
                                  'core/ap_hooks.pyc', '/debug.pyc')):
                compare(old, new)
                count += 1
gui = os.path.join(ROOT, 'res/gui')
resource = json.load(open(os.path.join(gui, 'gen_resources/armorshotanalyzer.json')))[0]
assert resource['id'] == 'R.mods.armorshotanalyzer.views.ArmorShotAnalyzerBattleView'
html = os.path.join(ROOT, 'res', resource['path'].replace('coui://', ''))
assert os.path.isfile(html)
for local in re.findall(r'(?:href|src)="([^"]+)"', open(html).read()):
    assert os.path.isfile(os.path.join(os.path.dirname(html), local)), local
assert not os.path.exists(os.path.join(CLIENT, 'ap_calculator'))
assert not os.path.exists(os.path.join(gui, 'AP_Calculator_2'))
print('Base modules preserve instructions and non-name data: ' + str(count))
print('Renamed package imports and resource/HTML links: OK')
