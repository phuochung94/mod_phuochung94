"""Static symbol audit only; execute through inspect_client.py's Python 2 host."""
import json
import marshal
import os
import types
import zipfile

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia'
output = os.path.join(os.path.dirname(__file__), 'client_inspection', 'api_audit.json')

def symbols(code):
    found = set(code.co_names) | set(code.co_varnames) | set([code.co_name])
    for item in code.co_consts:
        if isinstance(item, types.CodeType):
            found.update(symbols(item))
        elif isinstance(item, basestring):
            found.add(item)
    return found

required = {
    'scripts/client/PlayerEvents.pyc': ['onAvatarReady', 'onAvatarBecomeNonPlayer'],
    'scripts/client/AvatarInputHandler/__init__.pyc': ['activatePostmortem'],
    'scripts/client/aih_constants.pyc': ['SHOT_RESULT', 'UNDEFINED', 'NOT_PIERCED',
                                      'LITTLE_PIERCED', 'GREAT_PIERCED'],
    'scripts/client/frameworks/wulf/__init__.pyc': ['PositionAnchor', 'ViewFlags',
        'ViewModel', 'ViewSettings', 'WindowFlags', 'WindowLayer'],
    'scripts/client/gui/impl/pub/__init__.pyc': ['ViewImpl', 'WindowImpl'],
    'scripts/client/gui/impl/pub/view_impl.pyc': ['_onLoading'],
    'scripts/client/frameworks/wulf/view/view.pyc': ['getViewModel'],
    'scripts/client/frameworks/wulf/view/view_model.pyc': ['transaction',
        '_addStringProperty', '_addBoolProperty', '_setString', '_setBool'],
    'scripts/client/gui/impl/pub/window_impl.pyc': ['destroy', 'center', 'move'],
    'scripts/client/frameworks/wulf/windows_system/window.pyc': ['load', 'show',
        'onSizeChanged'],
}
report = {}
with zipfile.ZipFile(os.path.join(GAME, 'res/packages/scripts.pkg')) as archive:
    for name, expected in sorted(required.items()):
        data = archive.read(name)
        if data[:4] != '\x03\xf3\x0d\x0a':
            raise RuntimeError('Unexpected bytecode: ' + name)
        found = symbols(marshal.loads(data[8:]))
        missing = sorted(set(expected) - found)
        report[name] = dict(required=expected, missing=missing)
with zipfile.ZipFile(os.path.join(GAME,
        'mods/2.4.1.1/net.openwg.gameface_1.2.2.wotmod')) as archive:
    model = archive.read('res/gui/gameface/mods/libs/model.js')
    expected = ['ModelObserver', 'onUpdate', 'subscribe']
    report['OpenWG/model.js'] = dict(required=expected,
        missing=[name for name in expected if name not in model])
with open(output, 'w') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
for name, result in sorted(report.items()):
    print(name + ': ' + ('MISSING ' + repr(result['missing']) if result['missing'] else 'OK'))
if any(value['missing'] for value in report.values()):
    raise RuntimeError('Static API audit incomplete; inspect missing symbols')
