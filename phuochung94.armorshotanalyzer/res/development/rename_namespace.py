"""One-time Python 2.7 namespace migration, preserving bytecode instructions."""
import os
import marshal
import types
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPLACEMENTS = [
    ('ap_calculator_2', 'armorshotanalyzer'),
    ('AP_Calculator_2', 'ArmorShotAnalyzer'),
    ('ap_calculator', 'armorshotanalyzer'),
    ('APBattle', 'ArmorShotAnalyzerBattle'),
] + [('ap_' + suffix, 'armorshotanalyzer_' + suffix) for suffix in
     ('shell_info', 'gameface_api', 'constants', 'config', 'logger', 'hooks', 'math', 'gui')]

def rename(value):
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value

def transform(value):
    if isinstance(value, types.CodeType):
        # Only symbolic names, string constants and diagnostic filenames change.
        # Preserve instruction bytes, numeric constants, line tables and layout.
        result = types.CodeType(value.co_argcount, value.co_nlocals,
            value.co_stacksize, value.co_flags, value.co_code,
            tuple(transform(v) for v in value.co_consts),
            tuple(rename(v) for v in value.co_names),
            tuple(rename(v) for v in value.co_varnames), rename(value.co_filename),
            rename(value.co_name), value.co_firstlineno, value.co_lnotab,
            tuple(rename(v) for v in value.co_freevars),
            tuple(rename(v) for v in value.co_cellvars))
        assert result.co_code == value.co_code
        return result
    if isinstance(value, basestring):
        return rename(value)
    if isinstance(value, tuple):
        return tuple(transform(v) for v in value)
    return value

backup = os.path.join(ROOT, 'res/development/backups/before_namespace_rename_2026-11-05.zip')
if os.path.exists(backup):
    raise RuntimeError('Migration backup exists; refusing to repeat')
paths = []
for folder in ('res/scripts', 'res/gui', 'res/development/source', 'res/development/tests'):
    for directory, dirs, names in os.walk(os.path.join(ROOT, folder), followlinks=False):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(directory, d))]
        paths.extend(os.path.join(directory, n) for n in names
                     if not os.path.islink(os.path.join(directory, n)))
tools = [os.path.join(ROOT, 'res/development', n) for n in
         ('build_bytecode.py', 'windows_project.py')]
paths.extend(tools)
with zipfile.ZipFile(backup, 'w', zipfile.ZIP_STORED) as archive:
    for path in paths:
        archive.write(path, os.path.relpath(path, ROOT).replace('\\', '/'))
with zipfile.ZipFile(backup) as archive:
    assert archive.testzip() is None

for path in paths:
    data = open(path, 'rb').read()
    if path.endswith('.pyc'):
        assert data[:4] == '\x03\xf3\x0d\x0a'
        data = data[:8] + marshal.dumps(transform(marshal.loads(data[8:])))
    elif path.endswith(('.py', '.js', '.html', '.css', '.json')):
        if path in tools:
            # Preserve fixed external project/output paths and old-loader guard.
            for old, new in REPLACEMENTS:
                if old not in ('AP_Calculator_2', 'APBattle'):
                    data = data.replace(old, new)
        else:
            data = rename(data)
    open(path, 'wb').write(data)

# Rename children before their parents; never traverse historical snapshots.
for folder in ('res/scripts', 'res/gui', 'res/development/source'):
    for directory, dirs, files in os.walk(os.path.join(ROOT, folder), topdown=False,
                                         followlinks=False):
        for name in files + dirs:
            new = rename(name)
            if new != name:
                oldpath = os.path.join(directory, name)
                if os.path.islink(oldpath):
                    raise RuntimeError('Unexpected symlink')
                os.rename(oldpath, os.path.join(directory, new))
print('Namespace migrated; backup: ' + backup)
