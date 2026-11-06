"""Migrate runtime resource IDs, paths and cache namespace to phuochung94."""
import json
import struct
from build_asia import ROOT, parse

OLD, NEW = b'14th_ua', b'phuochung94'


def transform(value):
    if isinstance(value, bytes):
        return value.replace(OLD, NEW)
    if isinstance(value, dict):
        return {key: transform(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(transform(item) for item in value)
    return value


def save(path, before, after):
    if before == after:
        return
    backup = ROOT / 'dist/backups/rename-namespace' / path.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists() and backup.read_bytes() != before:
        raise ValueError('Backup conflict: ' + str(backup))
    if not backup.exists():
        backup.write_bytes(before)
    path.write_bytes(after)


def main():
    changed = []
    for path in (ROOT / 'res').rglob('*'):
        if not path.is_file():
            continue
        before = path.read_bytes()
        if path.suffix == '.pyc':
            reader, model = parse(before)
            after = before
            for offset, _, value in reversed(reader.strings):
                if OLD in value:
                    renamed = value.replace(OLD, NEW)
                    after = after[:offset+1] + struct.pack('<i', len(renamed)) + renamed + after[offset+5+len(value):]
            if parse(after)[1] != transform(model):
                raise ValueError('Unexpected marshal changes: ' + str(path))
        elif path.suffix in ('.js', '.css', '.html', '.json'):
            after = before.replace(OLD, NEW)
        else:
            continue
        save(path, before, after)
        if before != after:
            changed.append(path.relative_to(ROOT).as_posix())
    meta = ROOT / 'meta.xml'
    before = meta.read_bytes()
    save(meta, before, before.replace(b'com.14th_ua.moe_calculator', b'com.phuochung94.moe_calculator'))
    # Only known namespace paths are moved; targets stay strictly inside res/.
    for old_relative, new_relative in (
        ('res/gui/gen_resources/com.14th_ua.moe_calculator.json', 'res/gui/gen_resources/com.phuochung94.moe_calculator.json'),
        ('res/gui/gameface/mods/14th_ua', 'res/gui/gameface/mods/phuochung94'),
    ):
        old, new = ROOT / old_relative, ROOT / new_relative
        if old.exists():
            if new.exists():
                raise ValueError('Destination already exists: ' + str(new))
            assert old.resolve().is_relative_to((ROOT / 'res').resolve())
            assert new.resolve().is_relative_to((ROOT / 'res').resolve())
            old.rename(new)
    report = {'namespace': 'phuochung94', 'changed_files': changed,
              'original_author_credit_preserved': True, 'runtime_verified': False}
    (ROOT / 'dist/namespace-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
