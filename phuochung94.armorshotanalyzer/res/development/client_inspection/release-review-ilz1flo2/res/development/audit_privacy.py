"""Python 2.7 runtime audit: no telemetry/network code or copied shot algorithms."""
import os, marshal, types
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
package = os.path.join(root, 'scripts/client/armorshotanalyzer')
forbidden = ('wot-telemetry', 'onrender.com', 'urllib', 'urlopen', 'httplib', 'socket',
             'requests', 'onaccountshowgui', 'armorshotanalyzer_logger',
             'serverusername', 'accountdbid', 'getplayerdatabaseid')
def walk(code):
    values = list(code.co_names) + list(code.co_consts) if isinstance(code,types.CodeType) else list(code)
    for value in values:
        if isinstance(value, types.CodeType):
            walk(value)
        elif isinstance(value,(tuple,list,set,frozenset)):
            walk(value)
        elif isinstance(value, basestring):
            assert not any(key in value.lower() for key in forbidden), value
for directory, _, files in os.walk(os.path.join(root,'scripts/client')):
    for name in files:
        if name.endswith('.pyc'):
            walk(marshal.loads(open(os.path.join(directory,name),'rb').read()[8:]))
assert not os.path.exists(os.path.join(package,'armorshotanalyzer_logger.pyc'))
code=marshal.loads(open(os.path.join(package,'core/armorshotanalyzer_hooks.pyc'),'rb').read()[8:])
names=[c.co_name for c in code.co_consts if isinstance(c,types.CodeType)]
assert not any(name.startswith('my_shot_result') for name in names)
for source,target in (
    ('debug.py','debug.pyc'),
    ('armorshotanalyzer_shell_info.py','core/armorshotanalyzer_shell_info.pyc'),
    ('armorshotanalyzer_hooks.py','core/armorshotanalyzer_hooks.pyc'),
    ('core_init.py','core/__init__.pyc'),('package_init.py','__init__.pyc'),
    ('mod_armorshotanalyzer.py','../gui/mods/mod_armorshotanalyzer.pyc')):
    path=os.path.join(package,target)
    dfile=os.path.relpath(path,root).replace('\\','/')[:-1]
    expected=compile(open(os.path.join(root,'development/source',source),'rb').read(),dfile,'exec')
    actual=marshal.loads(open(path,'rb').read()[8:])
    assert marshal.dumps(actual)==marshal.dumps(expected),target
print('Runtime telemetry/network audit and maintained source/bytecode matches: OK')
