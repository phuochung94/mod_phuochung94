"""Build and verify a stored-only WoT resource package."""
import hashlib
from pathlib import Path
import zipfile
import struct

ROOT = Path(__file__).resolve().parents[1]
NAME = 'phuochung94.audioww+maps-ASIA 2.4.1.1 #991.wotmod'


def marshal27(value):
    if value is None:
        return b'N'
    if isinstance(value, bytes):
        return b's' + struct.pack('<i', len(value)) + value
    if isinstance(value, tuple):
        return b'(' + struct.pack('<i', len(value)) + b''.join(map(marshal27, value))
    raise TypeError(type(value))


def build_queue_loader():
    source = (ROOT / 'src/mod_compact_queue.py').read_bytes()
    compile(source, 'mod_compact_queue.py', 'exec')
    bytecode = bytes([100, 0, 0, 100, 1, 0, 100, 1, 0, 85, 100, 1, 0, 83])
    fields = (bytecode, (source, None), (), (), (), (), b'mod_compact_queue.py', b'<module>')
    body = b'c' + b''.join(struct.pack('<i', n) for n in (0, 0, 3, 0))
    body += b''.join(map(marshal27, fields)) + struct.pack('<i', 1) + marshal27(b'')
    target = ROOT / 'res/scripts/client/gui/mods/mod_compact_queue.pyc'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'\x03\xf3\r\n' + struct.pack('<i', 0) + body)


def main():
    files = sorted((ROOT / 'res').rglob('*'))
    files = [p for p in files if p.is_file()]
    temp = ROOT / (NAME + '.building')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_STORED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(temp) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == len(files)
        for entry in archive.infolist():
            assert entry.compress_type == zipfile.ZIP_STORED
            assert entry.filename.startswith('res/')
            assert hashlib.sha256(archive.read(entry)).digest() == hashlib.sha256((ROOT / entry.filename).read_bytes()).digest()
    temp.replace(ROOT / NAME)
    print('Verified package:', len(files), 'files;', (ROOT / NAME).stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
