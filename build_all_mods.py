"""Merge current verified releases into one stored WoT archive. Never installs it."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re, shutil, zipfile, xml.etree.ElementTree as ET

BASE=Path(r'C:\mod_phuochung94')
OUTPUT=BASE/'.wotmod'
OUTPUT.mkdir(exist_ok=True)
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')

def sha(data):return hashlib.sha256(data).hexdigest()

def build():
    info=ET.parse(GAME/'version.xml').getroot()
    version,number=re.fullmatch(r'\s*v\.(\S+)\s+#(\d+)\s*',info.findtext('version')).groups()
    label=info.findtext('meta/realm').strip()+' '+version+' #'+number
    projects=sorted(p for p in BASE.glob('phuochung94.*') if p.is_dir() and (p/'res').is_dir())
    inputs=[]
    for p in projects:
        record=json.loads((p/'dist/published-report.json').read_text(encoding='utf-8'))
        source=Path(record['path'])
        assert source.parent==OUTPUT and source.name.endswith('-'+label+'.wotmod'), 'Publish project for current game first: '+p.name
        assert sha(source.read_bytes())==record['sha256'], 'Published hash changed: '+p.name
        inputs.append(source)
    assert inputs, 'No published projects'
    installed=list((GAME/'mods'/version).glob('net.openwg.gameface_*.wotmod'))
    assert len(installed)==1, 'Expected one installed and checked Gameface dependency'
    dependency=OUTPUT/installed[0].name
    assert dependency.read_bytes()==installed[0].read_bytes(), 'Dependency differs from checked installed copy'
    payload={}; owners={}; aliases={}; credits=[]; sources=[];duplicates=[]
    for source in inputs:
        with zipfile.ZipFile(source) as z:
            assert z.testzip() is None, 'CRC failure: '+source.name
            assert len(z.namelist())==len(set(z.namelist())), 'Duplicate entries: '+source.name
            metadata=ET.fromstring(z.read('meta.xml'))
            credits.append(source.stem+'\n'+(metadata.findtext('description') or metadata.findtext('name') or '')+'\nAuthor: '+(metadata.findtext('author') or 'see original project credits'))
            for entry in z.infolist():
                if entry.is_dir() or entry.filename=='meta.xml':continue
                path=PurePosixPath(entry.filename)
                assert not path.is_absolute() and '..' not in path.parts and path.parts[0]=='res' and '\\' not in entry.filename, 'Unsafe/non-runtime entry: '+entry.filename
                name=entry.filename; key=name.casefold(); data=z.read(entry)
                if key in aliases:
                    previous=aliases[key]
                    if payload[previous]!=data:raise RuntimeError('Conflicting runtime file: '+name+' from '+owners[previous]+' and '+source.name)
                    duplicates.append(dict(path=name,from_package=source.name,shared_with=owners[previous]));continue
                aliases[key]=name;payload[name]=data;owners[name]=source.name
        sources.append(dict(file=source.name,sha256=sha(source.read_bytes())))
    root=ET.Element('root')
    for key,value in [('id','phuochung94.mod_all'),('version',version+'.'+number),('name','phuochung94 — all mods'),('author','phuochung94'),('description','Combined personal mod collection for '+label+'.\nRequires the separate OpenWG Gameface .wotmod; it is not embedded.\n\n'+'\n\n'.join(credits))]:ET.SubElement(root,key).text=value
    ET.indent(root);meta=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    target=OUTPUT/('mods_'+label+'.wotmod');temporary=target.with_suffix('.building')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_STORED) as z:
        z.writestr('meta.xml',meta)
        for name,data in sorted(payload.items()):z.writestr(name,data)
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert len(z.infolist())==len(payload)+1
        assert all(i.compress_type==zipfile.ZIP_STORED for i in z.infolist())
        assert z.read('meta.xml')==meta
        for name,data in payload.items():assert z.read(name)==data
        with zipfile.ZipFile(dependency) as dep_archive:
            dependency_paths={n.casefold() for n in dep_archive.namelist() if n.startswith('res/') and not n.endswith('/')}
        assert not (dependency_paths & {n.casefold() for n in z.namelist()}), 'Shared Gameface runtime must remain external'
        assert not any(n.endswith('.wotmod') for n in z.namelist())
    if target.exists():
        old=BASE/'rollback-backups'/'combined';old.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,old/(target.stem+'-'+sha(target.read_bytes())[:16]+'.wotmod'))
    temporary.replace(target)
    report=dict(game=label,path=str(target),sha256=sha(target.read_bytes()),bytes=target.stat().st_size,mod_projects=len(projects),dependency=dependency.name,dependency_embedded=False,dependency_sha256=sha(dependency.read_bytes()),sources=sources,runtime_entries=len(payload),identical_duplicates=duplicates,conflicting_files=0,crc_and_source_payload_verified=True,compression='ZIP_STORED',in_game_verified=False,limitations='File collision and integrity checks do not prove runtime hook interoperability. Install this combined package plus exactly one separate Gameface package; omit constituent standalone mods to avoid duplicate initialization.')
    (BASE/'combined-build-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report

if __name__=='__main__':build()
