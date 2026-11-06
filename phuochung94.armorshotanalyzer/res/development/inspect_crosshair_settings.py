import os, zipfile, marshal, types, dis, sys
output = os.path.join(os.path.dirname(__file__), 'client_inspection/crosshair_settings.txt')
sys.stdout = open(output, 'w')
def walk(code, parent=''):
    print(parent + code.co_name, code.co_varnames[:code.co_argcount], code.co_names)
    print('STRINGS', [s for s in code.co_consts if isinstance(s, basestring)])
    if any(s in code.co_name.lower() for s in ('crosshair','tab','populate','dispose','size','preview')):
        dis.dis(code)
    for child in code.co_consts:
        if isinstance(child, types.CodeType): walk(child, parent + code.co_name + '.')
with zipfile.ZipFile(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia\res\packages\scripts.pkg') as archive:
    for name in ('scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsWindow.pyc',
                 'scripts/client/gui/Scaleform/daapi/view/meta/SettingsWindowMeta.pyc'):
        print('FILE', name)
        walk(marshal.loads(archive.read(name)[8:]))
