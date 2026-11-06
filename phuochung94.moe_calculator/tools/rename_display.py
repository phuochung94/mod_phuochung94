"""Rename display branding while preserving resource IDs, paths and attribution."""
import struct
from build_asia import ROOT, parse

OLD = b"14th_ua's MoE Calculator"
NEW = b"phuochung94's MoE Calculator"


def transform(value):
    if isinstance(value, bytes):
        return value.replace(OLD, NEW)
    if isinstance(value, dict):
        return {key: transform(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(transform(item) for item in value)
    return value


def write_with_backup(path, before, after):
    if before == after:
        return
    backup = ROOT / 'dist/backups/rename-display' / path.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists() and backup.read_bytes() != before:
        raise ValueError('Backup conflict: ' + str(backup))
    if not backup.exists():
        backup.write_bytes(before)
    path.write_bytes(after)
    print(path.relative_to(ROOT))


def main():
    for path in (ROOT / 'res').rglob('*.pyc'):
        before = path.read_bytes()
        reader, model = parse(before)
        patches = [(offset, value) for offset, _, value in reader.strings if OLD in value]
        after = before
        for offset, value in reversed(patches):
            renamed = value.replace(OLD, NEW)
            after = (after[:offset+1] + struct.pack('<i', len(renamed)) + renamed
                     + after[offset+5+len(value):])
        if parse(after)[1] != transform(model):
            raise ValueError('Unexpected bytecode change: ' + str(path))
        write_with_backup(path, before, after)
    for path in (ROOT / 'res').rglob('*'):
        if path.is_file() and path.suffix in ('.js', '.css', '.html'):
            before = path.read_bytes()
            write_with_backup(path, before, before.replace(OLD, NEW))
    path = ROOT / 'meta.xml'
    before = path.read_bytes()
    after = before.replace(OLD, NEW).replace(
        b'Author: 14th_ua</description>',
        b'Maintainer: phuochung94\nOriginal author: 14th_ua\nSource: https://github.com/drizzer14/moe-calculator</description>')
    write_with_backup(path, before, after)


if __name__ == '__main__':
    main()
