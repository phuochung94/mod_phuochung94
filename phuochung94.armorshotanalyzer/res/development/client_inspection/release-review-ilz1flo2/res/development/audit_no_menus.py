"""Python 2.7: verify initialization and all runtime imports without menu APIs."""
import __builtin__
import marshal
import os
import types
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
package = os.path.join(root, 'scripts/client/armorshotanalyzer')
forbidden = ('settings_gui', 'aslain', 'modssettingsapi', 'modslistapi',
             '/tooltips/', '/translations/')
def audit(code):
    for text in list(code.co_names) + list(code.co_consts):
        if isinstance(text, types.CodeType):
            audit(text)
        elif isinstance(text, basestring):
            assert not any(key in text.lower() for key in forbidden), repr(text)
count = 0
for directory, _, files in os.walk(package):
    for name in files:
        if name.endswith('.pyc'):
            audit(marshal.loads(open(os.path.join(directory, name), 'rb').read()[8:]))
            count += 1
requests = []
native_import = __builtin__.__import__
def importer(name, globals=None, locals=None, fromlist=(), level=-1):
    requests.extend(fromlist)
    assert not any('settings' in value.lower() or 'menu' in value.lower() for value in fromlist)
    if 'core' in fromlist:
        return type('Dependencies', (), dict(core=object()))
    return native_import(name, globals, locals, fromlist, level)
builtins = dict(__builtin__.__dict__)
builtins['__import__'] = importer
code = marshal.loads(open(os.path.join(package, '__init__.pyc'), 'rb').read()[8:])
exec code in dict(__name__='armorshotanalyzer', __package__='armorshotanalyzer',
                  __builtins__=builtins)
assert requests == ['core'], requests
print('Package imports inert core only; no telemetry, menu or modlist registration')
print('All ' + str(count) + ' package modules free of removed menu/resource references')
