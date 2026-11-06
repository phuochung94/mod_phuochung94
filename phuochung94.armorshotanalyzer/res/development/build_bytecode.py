# Run with Python 2.7. Build the five maintained overlay/lifecycle sources.
import os
import py_compile
import sys
if sys.version_info[:2] != (2, 7):
    raise SystemExit('Use Python 2.7 to build WoT bytecode.')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for source, target in (
    ('debug.py', 'scripts/client/armorshotanalyzer/debug.pyc'),
    ('armorshotanalyzer_shell_info.py', 'scripts/client/armorshotanalyzer/core/armorshotanalyzer_shell_info.pyc'),
    ('mod_armorshotanalyzer.py', 'scripts/client/gui/mods/mod_armorshotanalyzer.pyc'),
    ('package_init.py', 'scripts/client/armorshotanalyzer/__init__.pyc'),
    ('core_init.py', 'scripts/client/armorshotanalyzer/core/__init__.pyc'),
    ('armorshotanalyzer_hooks.py', 'scripts/client/armorshotanalyzer/core/armorshotanalyzer_hooks.pyc')):
    path = os.path.join(root, target)
    py_compile.compile(os.path.join(root, 'development/source', source),
                       cfile=path, dfile=target[:-1], doraise=True)
    print('Built ' + target)
