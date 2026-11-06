"""Read local client bytecode using its own Python DLL; never starts the game."""
import ctypes
import pathlib
import sys
import zipfile

PROJECT = pathlib.Path(__file__).resolve().parents[2]
GAME = pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
WORK = PROJECT / 'res/development/client_inspection'
WORK.mkdir(exist_ok=True)
with zipfile.ZipFile(GAME / 'res/packages/scripts.pkg') as archive:
    for name in archive.namelist():
        if name.startswith('scripts/common/Lib/') and not name.endswith('/'):
            relative = pathlib.PurePosixPath(name).relative_to('scripts/common/Lib')
            if '..' in relative.parts:
                raise RuntimeError('Unsafe archive path')
            target = WORK / 'Lib' / str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
    targets = ['scripts/client/AvatarInputHandler/gun_marker_ctrl.pyc',
               'scripts/client/vehicle_systems/tankStructure.pyc',
               'scripts/common/items/components/component_constants.pyc']
    for name in targets:
        (WORK / pathlib.PurePosixPath(name).name).write_bytes(archive.read(name))

dll = ctypes.PyDLL(str(GAME / 'win64/python27.dll'))
ctypes.c_int.in_dll(dll, 'Py_NoSiteFlag').value = 1
ctypes.c_int.in_dll(dll, 'Py_IgnoreEnvironmentFlag').value = 1
dll.Py_SetPythonHome.argtypes = [ctypes.c_char_p]
python_home = str(WORK).encode('utf-8')
dll.Py_SetPythonHome(python_home)
dll.Py_Initialize()
dll.PyRun_SimpleString.argtypes = [ctypes.c_char_p]
dll.PyRun_SimpleString.restype = ctypes.c_int
code = """
import sys
sys.path.insert(0, {lib!r})
import marshal, types, dis
out = open({output!r}, 'w')
sys.stdout = out
def walk(code, prefix=''):
    name = prefix + code.co_name
    if code.co_name in ('getShotResult', '__shotResultDefault', '__shotResultModernHE',
                         '_shouldRicochet', '_computePenetrationArmor',
                         '__isDestructibleComponent', 'TankPartIndexes'):
        print(name, code.co_varnames[:code.co_argcount], code.co_names)
        dis.dis(code)
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            walk(value, name + '.')
for filename in {targets!r}:
    print('FILE', filename)
    walk(marshal.loads(open(filename, 'rb').read()[8:]))
out.close()
""".format(lib=str(WORK / 'Lib'), output=str(WORK / 'disassembly.txt'),
           targets=[str(WORK / pathlib.PurePosixPath(n).name) for n in targets])
if '--test' in sys.argv:
    code = """
import sys, os
sys.argv = ['test_shell_info.py']
sys.path.insert(0, {lib!r})
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
os.environ.pop('AP_TEST_BYTECODE', None)
if {bytecode!r}:
    os.environ['AP_TEST_BYTECODE'] = '1'
import types, unittest
module = types.ModuleType('client_overlay_tests')
module.__file__ = {test!r}
sys.modules[module.__name__] = module
execfile({test!r}, module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
if suite.countTestCases() < 24:
    raise RuntimeError('Expected at least 24 tests')
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise RuntimeError('Tests failed')
""".format(lib=str(WORK / 'Lib'), bytecode='--bytecode' in sys.argv,
           test=str(PROJECT / 'res/development/tests/test_shell_info.py'))
if '--run' in sys.argv:
    script = pathlib.Path(sys.argv[sys.argv.index('--run') + 1]).resolve()
    script.relative_to(PROJECT)
    code = """
import sys
sys.path.insert(0, {lib!r})
sys.argv = [{script!r}]
execfile({script!r}, {{'__name__': '__main__', '__file__': {script!r}}})
""".format(lib=str(WORK / 'Lib'), script=str(script))
status = dll.PyRun_SimpleString(code.encode('utf-8'))
if status:
    raise SystemExit('Client Python execution failed: ' + str(status))
