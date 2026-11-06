"""Bundle separate mod/dependency files after verifying the client-check report."""
import hashlib
import json
import shutil
import zipfile
from build_asia import ROOT, GAME, OUTPUT_DIR


def main():
    report = json.loads((ROOT / 'dist/compatibility-report.json').read_text())
    checked = report['client_check']
    if not checked['all_passed'] or checked['game'] != report['game']:
        raise ValueError('Dependency/client checks are missing or mismatched')
    mod = OUTPUT_DIR / report['package']
    dependency = GAME / 'mods' / report['game'].split()[1] / checked['dependency']
    for path, expected in ((mod, report['sha256']), (dependency, checked['dependency_sha256'])):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('File changed since checks: ' + path.name)
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError('Corrupt package: ' + path.name)
    output = OUTPUT_DIR / ('UNZIP-' + mod.stem + '.zip')
    if output.exists():
        backup = ROOT / 'dist/backups' / (output.stem + '-' + hashlib.sha256(output.read_bytes()).hexdigest()[:12] + '.zip')
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(output, backup)
    temporary = output.with_suffix('.zip.tmp')
    files = (mod, dependency)
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path in files:
            archive.write(path, arcname=path.name)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None or archive.namelist() != [path.name for path in files]:
            raise ValueError('Invalid bundle')
        for path in files:
            if archive.read(path.name) != path.read_bytes():
                raise ValueError('Bundle content mismatch')
    temporary.replace(output)
    result = {'output': str(output), 'files': [path.name for path in files],
              'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
    (ROOT / 'dist/bundle-report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
