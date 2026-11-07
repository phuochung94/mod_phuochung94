"""Publish checked runtime with author metadata, excluding development files."""
from pathlib import Path
import hashlib, json, re, shutil, zipfile, xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
OUTPUT=BASE/'.wotmod'
OUTPUT.mkdir(exist_ok=True)
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
def publish(project):
    project=Path(project).resolve()
    if project.parent!=BASE or not (project/'res').is_dir():raise ValueError('Unexpected project')
    info=ET.parse(GAME/'version.xml').getroot()
    version,build=re.search(r'v\.(\S+)\s+#(\d+)',info.findtext('version')).groups()
    label=info.findtext('meta/realm').strip()+' '+version+' #'+build
    ident={'phuochung94.minimap':'phuochung94.minimaps','phuochung94.missingdog':'phuochung94.missingdogs'}.get(project.name,project.name)
    meta=project/'meta.xml'
    root=ET.parse(meta).getroot() if meta.exists() else ET.Element('root')
    for key,value in [('id',root.findtext('id') or ident),('version',root.findtext('version') or version),('name',root.findtext('name') or ident),('author','phuochung94')]:
        node=root.find(key)
        if node is None:node=ET.SubElement(root,key)
        node.text=value
    description=root.find('description')
    if description is None:description=ET.SubElement(root,'description');description.text=ident
    text=description.text or ''
    if 'Maintainer: phuochung94' not in text:text+='\nMaintainer: phuochung94'
    text=re.sub(r'\nTarget game:.*','',text)+'\nTarget game: '+label
    description.text=text
    ET.indent(root);meta.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
    files=[]
    for f in (project/'res').rglob('*'):
        relative=f.relative_to(project)
        if not f.is_file() or f.is_symlink():continue
        if any(x in relative.parts for x in ('development','backups','__pycache__','.git')):continue
        if f.name in ('AGENTS.md','MOD_CUSTOMIZATIONS.md','.DS_Store','.DStore') or f.suffix.lower() in ('.md','.bak','.zip','.wotmod','.py','.pyo'):continue
        files.append(f)
    assert files
    target=OUTPUT/(ident+'-'+label+'.wotmod')
    pending=target.with_suffix('.building')
    with zipfile.ZipFile(pending,'w',zipfile.ZIP_STORED) as z:
        z.write(meta,'meta.xml')
        for f in sorted(files):z.write(f,f.relative_to(project).as_posix())
    with zipfile.ZipFile(pending) as z:
        assert z.testzip() is None
        expected={'meta.xml':meta,**{f.relative_to(project).as_posix():f for f in files}}
        assert set(z.namelist())==set(expected)
        assert all(i.compress_type==zipfile.ZIP_STORED for i in z.infolist())
        for name,f in expected.items():assert z.read(name)==f.read_bytes()
    if target.exists() and target.read_bytes()!=pending.read_bytes():
        previous=BASE/'rollback-backups'/'published';previous.mkdir(parents=True,exist_ok=True)
        oldhash=hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        shutil.copy2(target,previous/(target.stem+'-'+oldhash+'.wotmod'))
    pending.replace(target)
    result=dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),entries=len(files)+1,crc_payload_and_zip_stored_verified=True,in_game_verified=False)
    if ident in ('phuochung94.armorshotanalyzer','phuochung94.moe_calculator','phuochung94.uniquestyles'):
        dependencies=list((GAME/'mods'/version).glob('net.openwg.gameface_*.wotmod'));assert len(dependencies)==1
        dep=dependencies[0];bundle=OUTPUT/('UNZIP-'+target.stem+'.zip')
        with zipfile.ZipFile(bundle,'w',zipfile.ZIP_STORED) as z:z.write(target,target.name);z.write(dep,dep.name)
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None and set(z.namelist())=={target.name,dep.name}
            assert z.read(target.name)==target.read_bytes() and z.read(dep.name)==dep.read_bytes()
        result['bundle']=str(bundle)
        result['bundle_sha256']=hashlib.sha256(bundle.read_bytes()).hexdigest()
    dist=project/'dist';dist.mkdir(exist_ok=True)
    (dist/'published-report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    parser.add_argument('--checks-passed',action='store_true',required=True,help='Confirm compatibility checks have passed before publishing')
    args=parser.parse_args();print(json.dumps(publish(args.project),indent=2))
