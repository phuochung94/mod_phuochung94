"""Validate final delivery bytes and prepare isolated tests of that exact ZIP."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from zipfile import ZipFile, ZIP_STORED

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('project_package', HERE / 'windows_project.py')
project = importlib.util.module_from_spec(spec); spec.loader.exec_module(project)
mod = project.OUTPUT / project.next_package_name()
bundle = project.OUTPUT / ('UNZIP-' + mod.stem + '.zip')
gameface = project.gameface_package()
stage = Path(tempfile.mkdtemp(prefix='release-review-', dir=str(HERE / 'client_inspection')))
expected = {'res/' + p.relative_to(project.RES).as_posix(): p for p in project.runtime_files()}
expected['meta.xml'] = project.PROJECT / 'meta.xml'
with ZipFile(mod) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(set(archive.namelist()))
    assert set(archive.namelist()) == set(expected)
    for info in archive.infolist():
        name = PurePosixPath(info.filename)
        assert not name.is_absolute() and '..' not in name.parts and (name.parts[0] == 'res' or str(name) == 'meta.xml')
        assert info.compress_type == ZIP_STORED
        data = archive.read(info.filename)
        assert data == expected[info.filename].read_bytes(), info.filename
        if name.suffix == '.pyc': assert data[:4] == bytes.fromhex('03f30d0a')
        target = stage.joinpath(*name.parts); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
with ZipFile(bundle) as archive:
    assert archive.testzip() is None
    assert all(i.compress_type == ZIP_STORED for i in archive.infolist())
    assert len(archive.namelist()) == 2
    assert set(archive.namelist()) == {mod.name, gameface.name}
    assert archive.read(mod.name) == mod.read_bytes()
    assert archive.read(gameface.name) == gameface.read_bytes()
    for name in archive.namelist():
        with ZipFile(io.BytesIO(archive.read(name))) as nested: assert nested.testzip() is None
with ZipFile(gameface) as archive:
    for name in archive.namelist():
        if name.endswith('.pyc'):
            target = stage / 'dependency' / PurePosixPath(name)
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(archive.read(name))

development = stage / 'res/development'; development.mkdir(parents=True)
for folder in ('source', 'tests', 'reference_2_2_0'):
    shutil.copytree(HERE / folder, development / folder)
for name in ('audit_privacy.py','audit_no_menus.py'):
    shutil.copy2(HERE / name, development / name)
report = dict(client=list(project.client_identity()), stage=str(stage),
              mod=dict(path=str(mod), sha256=hashlib.sha256(mod.read_bytes()).hexdigest()),
              bundle=dict(path=str(bundle), sha256=hashlib.sha256(bundle.read_bytes()).hexdigest()),
              gameface=dict(path=str(gameface), sha256=hashlib.sha256(gameface.read_bytes()).hexdigest()),
              exact_runtime_file_count=len(expected), package_crc_structure_and_content='PASS',
              artifact_tests='PENDING', in_game_validation=False, submitted_to_reviewer=False)
(HERE / 'client_inspection/final_release_review.json').write_text(json.dumps(report, indent=2))
print('Exact release extracted for isolated runtime audit:', stage)
