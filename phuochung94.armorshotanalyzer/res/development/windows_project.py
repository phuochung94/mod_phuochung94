#!/usr/bin/env python3
"""Portable project checks, extension build and ZIP_STORED packaging."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZIP_STORED, ZipFile

RES = Path(__file__).resolve().parent.parent
PROJECT = RES.parent
OUTPUT = Path(r'C:\mod_phuochung94\.wotmod')
def client_identity():
    game = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
    root = ET.parse(str(game / 'version.xml')).getroot()
    realm = (root.findtext('meta/realm') or '').strip()
    version = (root.findtext('version') or '').strip()
    match = re.fullmatch(r'v\.?\s*(\d+(?:\.\d+)+)\s+#(\d+)', version)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', realm) or not match:
        raise RuntimeError('Invalid client realm/version; refusing to guess package name')
    return realm, match.group(1), match.group(2)


def next_package_name():
    return 'phuochung94.armorshotanalyzer-{} {} #{}.wotmod'.format(*client_identity())


def gameface_package():
    game = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
    version = client_identity()[1]
    candidates = sorted((game / 'mods' / version).glob('net.openwg.gameface_*.wotmod'))
    if len(candidates) != 1 or candidates[0].is_symlink():
        raise RuntimeError('Expected exactly one installed OpenWG Gameface package for ' + version)
    path = candidates[0]
    with ZipFile(str(path)) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Gameface archive CRC failure')
        meta = ET.fromstring(archive.read('meta.xml'))
        if (meta.findtext('id') or '').strip() != 'net.openwg.gameface':
            raise RuntimeError('Unexpected Gameface package identity')
        archive.getinfo('res/gui/gameface/mods/libs/model.js')
    return path

MAGIC = bytes.fromhex('03f30d0a')


def cleanup():
    for directory, dirs, files in os.walk(str(RES), followlinks=False):
        dirs[:] = [d for d in dirs if not Path(directory, d).is_symlink()]
        for name in files:
            path = Path(directory, name)
            if name in ('.DS_Store', '.DStore') and not path.is_symlink():
                path.unlink()


def runtime_files():
    result = []
    for folder in ('gui', 'scripts'):
        for directory, dirs, files in os.walk(str(RES / folder), followlinks=False):
            dirs[:] = [d for d in dirs if not Path(directory, d).is_symlink()
                       and d not in ('__pycache__', '.git')]
            for name in files:
                path = Path(directory, name)
                if path.is_symlink() or name in ('AGENTS.md', '.DS_Store', '.DStore'):
                    continue
                if path.suffix.lower() in ('.bak', '.zip', '.wotmod', '.py', '.pyo'):
                    continue
                result.append(path)
    return sorted(result)


def check():
    cleanup()
    for obsolete in ('scripts/client/ap_calculator', 'gui/AP_Calculator_2',
                     'gui/gen_resources/ap_calculator_2.json',
                     'scripts/client/armorshotanalyzer/settings_gui',
                     'scripts/client/armorshotanalyzer/armorshotanalyzer_logger.pyc',
                     'scripts/client/armorshotanalyzer/core/armorshotanalyzer_math.pyc',
                     'gui/ArmorShotAnalyzer/tooltips', 'gui/ArmorShotAnalyzer/translations'):
        if (RES / obsolete).exists():
            raise RuntimeError('Obsolete namespace remains: ' + obsolete)
    if (RES / 'scripts/client/gui/mods/mod_AP_Calculator.pyc').exists():
        raise RuntimeError('Remove the obsolete mod_AP_Calculator.pyc entry point before packaging')
    required = [RES / p for p in (
        'AGENTS.md', 'MOD_CUSTOMIZATIONS.md',
        'development/source/armorshotanalyzer_shell_info.py',
        'development/source/mod_armorshotanalyzer.py',
        'development/source/package_init.py',
        'development/source/core_init.py',
        'development/source/armorshotanalyzer_hooks.py',
        'development/tests/test_shell_info.py',
        'scripts/client/gui/mods/mod_armorshotanalyzer.pyc',
        'scripts/client/armorshotanalyzer/core/armorshotanalyzer_shell_info.pyc',
        'scripts/client/armorshotanalyzer/core/armorshotanalyzer_hooks.pyc',
        'scripts/client/armorshotanalyzer/core/__init__.pyc',
        'scripts/client/armorshotanalyzer/__init__.pyc',
        'gui/gen_resources/armorshotanalyzer.json')]
    for path in required:
        if not path.is_file():
            raise RuntimeError('Missing project file: ' + str(path))
    files = runtime_files()
    if not files:
        raise RuntimeError('No runtime files found')
    for path in files:
        if path.suffix == '.pyc' and path.read_bytes()[:4] != MAGIC:
            raise RuntimeError('Not Python 2.7 bytecode: ' + str(path))
    print('Project: ' + str(PROJECT))
    print('Runtime files: ' + str(len(files)))
    print('Required files and Python 2.7 bytecode headers: OK')
    print('Game compatibility still needs testing in the target WoT client.')


def python27(explicit):
    candidates = [explicit] if explicit else []
    if not explicit:
        candidates += [shutil.which(n) for n in ('python2.7', 'python27', 'python2')]
        candidates += [r'C:\Python27\python.exe', r'C:\Program Files\Python27\python.exe',
                       r'C:\Program Files (x86)\Python27\python.exe']
        if shutil.which('py'):
            result = subprocess.run(['py', '-2.7', '-c',
                                     'import sys; print(sys.executable)'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode == 0:
                candidates.append(result.stdout.strip())
    for candidate in candidates:
        if not candidate:
            continue
        try:
            result = subprocess.run([str(candidate), '-c',
                'import sys; sys.exit(0 if sys.version_info[:2] == (2,7) else 1)'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return str(candidate)
        except OSError:
            pass
    raise RuntimeError('Python 2.7 not found. Pass --python27 "C:\\Python27\\python.exe". '
                       'Packaging an existing build only needs Python 3.')


def test(interpreter):
    path = str(RES / 'development/tests/test_shell_info.py')
    for bytecode in (False, True):
        env = os.environ.copy()
        env.pop('AP_TEST_BYTECODE', None)
        if bytecode:
            env['AP_TEST_BYTECODE'] = '1'
        print('Testing ' + ('compiled bytecode' if bytecode else 'source'), flush=True)
        subprocess.check_call([interpreter, '-B', path], env=env, cwd=str(RES))


def runtime_digest(entries):
    digest = hashlib.sha256()
    for name, data in sorted(entries):
        if name.endswith('.pyc'):
            data = data[:4] + data[8:]  # Python 2 source mtime
        digest.update(name.encode('utf-8') + b'\0' + hashlib.sha256(data).digest())
    return digest.hexdigest()


def release_record(files):
    record_path = RES / 'development' / 'release_record.json'
    previous = json.loads(record_path.read_text())
    digest = runtime_digest(('res/' + p.relative_to(RES).as_posix(), p.read_bytes()) for p in files)
    number = previous['number'] + int(digest != previous['digest'])
    release = 'r' + str(number)
    heading = (PROJECT / 'CHANGELOG.md').read_text(encoding='utf-8').splitlines()[0]
    debug = RES / 'development/source/debug.py'
    if (heading != '# ArmorShotAnalyzer ' + release
            or ('VERSION = "' + release + '"') not in debug.read_text().splitlines()
            or release.encode() not in (RES / 'scripts/client/armorshotanalyzer/debug.pyc').read_bytes()):
        raise RuntimeError('Expected ' + release + ' in changelog and compiled startup logger. Update and rebuild before packaging.')
    return record_path, dict(number=number, digest=digest)


def package():
    from crosshair_preview import build as build_crosshair_preview
    build_crosshair_preview()
    check()
    gameface = gameface_package()
    gameface_data = gameface.read_bytes()
    files = runtime_files()
    record_path, record = release_record(files)
    destination = OUTPUT / next_package_name()
    fd, temporary = tempfile.mkstemp(prefix='ap-package-', suffix='.tmp', dir=str(OUTPUT))
    os.close(fd)
    bundle_temporary = None
    bundle_destination = OUTPUT / ('UNZIP-' + destination.stem + '.zip')
    try:
        with ZipFile(temporary, 'w', compression=ZIP_STORED) as archive:
            for path in files:
                archive.write(str(path), 'res/' + path.relative_to(RES).as_posix())
        with ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise RuntimeError('Archive CRC failure')
            if len(archive.infolist()) != len(files) or not all(
                    entry.compress_type == ZIP_STORED and entry.filename.startswith('res/')
                    for entry in archive.infolist()):
                raise RuntimeError('Invalid archive structure/compression')
            for path in files:
                if archive.read('res/' + path.relative_to(RES).as_posix()) != path.read_bytes():
                    raise RuntimeError('Archive content mismatch: ' + str(path))
        fd, bundle_temporary = tempfile.mkstemp(prefix='armorshotanalyzer-bundle-',
                                               suffix='.tmp', dir=str(OUTPUT))
        os.close(fd)
        with ZipFile(bundle_temporary, 'w', compression=ZIP_STORED) as bundle:
            bundle.write(temporary, destination.name)
            bundle.writestr(gameface.name, gameface_data)
        with ZipFile(bundle_temporary) as bundle:
            if (bundle.testzip() is not None or len(bundle.infolist()) != 2
                    or any(i.compress_type != ZIP_STORED for i in bundle.infolist())
                    or set(bundle.namelist()) != {destination.name, gameface.name}
                    or bundle.read(destination.name) != Path(temporary).read_bytes()
                    or bundle.read(gameface.name) != gameface_data):
                raise RuntimeError('Bundle structure, CRC or content mismatch')
        # Keep an identical existing package; Windows may have it open in an
        # archive viewer, and replacing it is unnecessary when bytes match.
        if not destination.exists() or destination.read_bytes() != Path(temporary).read_bytes():
            os.replace(temporary, str(destination))
        os.replace(bundle_temporary, str(bundle_destination))
        if record != json.loads(record_path.read_text()):
            pending = record_path.with_suffix(".tmp")
            pending.write_text(json.dumps(record, indent=2))
            os.replace(pending, record_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
        if bundle_temporary and os.path.exists(bundle_temporary):
            os.unlink(bundle_temporary)
    print('Created ZIP_STORED: ' + str(destination))
    print('SHA256: ' + hashlib.sha256(destination.read_bytes()).hexdigest())
    print('Created mod + Gameface bundle: ' + str(bundle_destination))
    print('Gameface source: ' + str(gameface))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'test', 'build', 'package'))
    parser.add_argument('--python27', help='Path to the Python 2.7 executable')
    args = parser.parse_args()
    if args.action == 'check':
        check()
    elif args.action == 'package':
        package()
    elif args.action == 'test':
        check()
        test(python27(args.python27))
    else:
        check()
        interpreter = python27(args.python27)
        targets = [RES / p for p in (
            'scripts/client/armorshotanalyzer/debug.pyc',
            'scripts/client/armorshotanalyzer/core/armorshotanalyzer_shell_info.pyc',
            'scripts/client/gui/mods/mod_armorshotanalyzer.pyc',
            'scripts/client/armorshotanalyzer/__init__.pyc',
            'scripts/client/armorshotanalyzer/core/__init__.pyc',
            'scripts/client/armorshotanalyzer/core/armorshotanalyzer_hooks.pyc')]
        originals = {path: path.read_bytes() for path in targets}
        try:
            subprocess.check_call([interpreter, '-B',
                str(RES / 'development/build_bytecode.py')], cwd=str(RES))
            test(interpreter)
        except Exception:
            for path, content in originals.items():
                path.write_bytes(content)
            raise
        package()
        print('Built the six maintained modules; client shot algorithms are not replaced.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        sys.exit(1)
