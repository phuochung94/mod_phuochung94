"""Build Python 2.7 native-HUD visibility adapter using verified client interfaces."""
import ast,sys,struct,json,copy
from pathlib import Path
ROOT=Path(r'C:\mod_phuochung94\phuochung94.moe_calculator');sys.path.insert(0,str(ROOT/'tools'))
from build_asia import parse
# Reuse assembler definitions only; never execute the resize installer on import.
tree=ast.parse((ROOT/'tools/fix_resize.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('pack','ins','Asm','code')],type_ignores=[]),'<assembler>','exec'))
N=('literal',b'N');F=('literal',b'F');T=('literal',b'T')
# native_visible: read the native battle page and native damage-log component.
names=['dependency','instance','IAppLoader','getDefBattleApp','containerManager','getView','WindowLayer','VIEW','isGuiVisible','as_isComponentVisibleS','ALIASES','BATTLE_DAMAGE_LOG_PANEL','Exception']
a=Asm();setup=len(a.b);a.op(121,0)
a.op(116,0);a.op(106,1);a.op(116,2);a.op(131,1);a.op(106,3);a.op(131,0);a.op(125,0)
a.op(124,0);a.op(100,0);a.op(107,8);a.jump(115,'hidden')
a.op(124,0);a.op(106,4);a.op(106,5);a.op(116,6);a.op(106,7);a.op(131,1);a.op(125,1)
a.op(124,1);a.op(100,0);a.op(107,8);a.jump(115,'hidden')
a.op(124,1);a.op(106,8);a.op(131,0);a.jump(114,'hidden')
a.op(124,1);a.op(106,9);a.op(116,10);a.op(106,11);a.op(131,1);a.op(83)
a.label('hidden');a.op(100,1);a.op(83)
a.label('except');a.op(4);a.op(116,12);a.op(107,10);a.jump(114,'unhandled');a.op(1);a.op(1);a.op(1);a.op(100,1);a.op(83)
a.label('unhandled');a.op(88)
a.b[setup+1:setup+3]=struct.pack('<H',a.labels['except']-(setup+3))
native=code('native_visible',a,names,[N,F],('app','page'));native['header']=(0,2,12,67)
# sync uses the existing visibility gate: don't bypass scoreboard/spectator/battle conditions.
a=Asm();a.op(116,0);a.op(131,0);a.op(125,0);a.op(124,0);a.op(100,1);a.op(116,2);a.op(106,3);a.op(107,6);a.op(12);a.op(107,2);a.jump(115,'return')
a.op(124,0);a.op(97,1);a.op(124,0);a.jump(114,'hide')
a.op(116,2);a.op(106,3);a.op(106,4);a.op(100,1);a.op(131,1);a.op(1);a.jump(113,'refresh')
a.label('hide');a.op(116,2);a.op(106,3);a.op(106,5);a.op(100,1);a.op(131,1);a.op(1)
a.label('refresh');a.op(116,2);a.op(106,6);a.op(131,0);a.op(1)
a.label('return');a.op(100,0);a.op(83)
sync=code('sync',a,['native_visible','_last_visible','battle_bridge','_open_overlays','discard','add','_schedule_refresh'],[N,b'native_damage_hud'],('visible',));sync['header']=(0,1,12,67)
a=Asm();a.op(116,0);a.op(131,0);a.op(1);a.op(100,0);a.op(83)
event=code('_on_gui_visibility',a,['sync'],[N],('event',))
# start: event-driven GUI visibility plus polling for killcam/native components.
a=Asm();a.op(116,0);a.jump(115,'return');a.op(116,1);a.op(106,2);a.op(116,3);a.op(106,4);a.op(116,5);a.op(116,6);a.op(106,7);a.op(131,3);a.op(1);a.op(100,1);a.op(97,0)
a.label('return');a.op(100,0);a.op(83)
start=code('start',a,['_armed','g_eventBus','addListener','GameEvent','GUI_VISIBILITY','_on_gui_visibility','EVENT_BUS_SCOPE','BATTLE'],[N,T])
# Build module imports and function exports.
a=Asm();mn=[];mc=[]
def ni(n):
 b=n.encode()
 if b not in mn:mn.append(b)
 return mn.index(b)
def ci(v):
 for i,c in enumerate(mc):
  if c==v:return i
 mc.append(v);return len(mc)-1
def imp(module,items):
 a.op(100,ci(-1));a.op(100,ci(tuple(x[0].encode() for x in items)));a.op(108,ni(module))
 for original,alias in items:a.op(109,ni(original));a.op(90,ni(alias))
 a.op(1)
imp('helpers',[('dependency','dependency')]);imp('skeletons.gui.app_loader',[('IAppLoader','IAppLoader')]);imp('frameworks.wulf',[('WindowLayer','WindowLayer')])
imp('gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES',[('BATTLE_VIEW_ALIASES','ALIASES')]);imp('gui.shared',[('g_eventBus','g_eventBus'),('EVENT_BUS_SCOPE','EVENT_BUS_SCOPE')]);imp('gui.shared.events',[('GameEvent','GameEvent')]);imp('moe_calculator.bridge',[('battle_bridge','battle_bridge')])
a.op(100,ci(N));a.op(90,ni('_last_visible'));a.op(100,ci(F));a.op(90,ni('_armed'))
for c in (native,sync,event,start):a.op(100,ci(c));a.op(132,0);a.op(90,ni(c['name'].decode()))
a.op(101,ni('start'));a.op(131,0);a.op(1);a.op(100,ci(N));a.op(83)
module=code('<module>',a,[n.decode() for n in mn],mc,flags=64)
for c in (native,sync,event,start,module):c['filename']=b'res/scripts/client/moe_calculator/bridge/native_visibility.py'
def encode(m):
 raw=bytes.fromhex('03f30d0a00000000')+pack(m);assert parse(raw)[1]==m;return raw
# Simulate native function against fake battle page; exercise normal/hidden/failure cases.
class Obj:pass
state={'gui':True,'damage':True,'page':True,'app':True,'fail':False};env={}
page=Obj();page.isGuiVisible=lambda:state['gui'];page.as_isComponentVisibleS=lambda alias:state['damage']
manager=Obj();manager.getView=lambda layer:page if state['page'] else None
app=Obj();app.containerManager=manager
loader=Obj()
def appget():
 if state['fail']:raise RuntimeError('unavailable client')
 return app if state['app'] else None
loader.getDefBattleApp=appget;dep=Obj();dep.instance=lambda cls:loader
env.update(dependency=dep,IAppLoader=object(),WindowLayer=Obj(),ALIASES=Obj(),Exception=Exception)
env['WindowLayer'].VIEW=1;env['ALIASES'].BATTLE_DAMAGE_LOG_PANEL='battleDamageLogPanel'
def val(v):
 if v==N:return None
 if v==F:return False
 if v==T:return True
 return v.decode() if isinstance(v,bytes) else v
def run(c):
 st=[];loc={};p=0;handler=None;b=c['code']
 while p<len(b):
  op=b[p];arg=int.from_bytes(b[p+1:p+3],'little') if op>=90 else None;p+=3 if op>=90 else 1
  try:
   if op==121:handler=p+arg
   elif op==100:st.append(val(c['consts'][arg]))
   elif op==116:st.append(env[c['names'][arg].decode()])
   elif op==97:env[c['names'][arg].decode()]=st.pop()
   elif op==106:st.append(getattr(st.pop(),c['names'][arg].decode()))
   elif op==125:loc[arg]=st.pop()
   elif op==124:st.append(loc[arg])
   elif op==131:
    args=st[-arg:] if arg else []
    if arg:del st[-arg:]
    fn=st.pop();st.append(fn(*args))
   elif op==107:
    r=st.pop();l=st.pop();st.append({2:lambda:l==r,8:lambda:l is r,6:lambda:l in r,10:lambda:issubclass(l,r)}[arg]())
   elif op in (114,115):
    if bool(st.pop())==(op==115):p=arg
   elif op==113:p=arg
   elif op==12:st.append(not st.pop())
   elif op==4:st.append(st[-1])
   elif op==1:st.pop()
   elif op==83:return st.pop()
   else:raise AssertionError(op)
  except RuntimeError as exc:
   assert handler is not None;st=[None,exc,type(exc)];p=handler;handler=None
assert run(native) is True
for key in ('gui','damage','page','app'):
 state[key]=False;assert run(native) is False;state[key]=True
state['fail']=True;assert run(native) is False;state['fail']=False
bridge=Obj();bridge._open_overlays={'scoreboard'};refresh=[];bridge._schedule_refresh=lambda:refresh.append(1)
env.update(native_visible=lambda:run(native),_last_visible=None,battle_bridge=bridge)
run(sync);assert bridge._open_overlays=={'scoreboard'} and len(refresh)==0
state['gui']=False;run(sync);assert bridge._open_overlays=={'scoreboard','native_damage_hud'}
run(sync);assert len(refresh)==1
state['gui']=True;run(sync);assert bridge._open_overlays=={'scoreboard'} and len(refresh)==2
state['gui']=False;run(sync);bridge._open_overlays.clear();run(sync);assert 'native_damage_hud' in bridge._open_overlays
# Modify viewport poll to sync native visibility each tick. Remap absolute branch targets.
path=ROOT/'res/scripts/client/moe_calculator/bridge/viewport_watch.pyc';original=path.read_bytes();m=parse(original)[1];poll=next(c for c in m['consts'] if isinstance(c,dict) and c['name']==b'_poll')
if b'moe_calculator.bridge.native_visibility' in poll['names']:
 assert parse((ROOT/'res/scripts/client/moe_calculator/bridge/native_visibility.pyc').read_bytes())[1]==module
 print('Native visibility adapter matches; simulated visibility transitions passed')
 raise SystemExit(0)
idx=len(poll['names']);ci0=len(poll['consts']);poll['names']+=(b'moe_calculator.bridge.native_visibility',b'sync');poll['consts']+=(-1,(b'sync',))
prefix=ins(100,ci0)+ins(100,ci0+1)+ins(108,idx)+ins(109,idx+1)+ins(131,0)+ins(1)+ins(1)
raw=bytearray(poll['code']);p=0
while p<len(raw):
 op=raw[p]
 if op in (111,112,113,114,115,119):raw[p+1:p+3]=struct.pack('<H',int.from_bytes(raw[p+1:p+3],'little')+len(prefix))
 p+=3 if op>=90 else 1
poll['code']=prefix+raw
encoded=original[:8]+pack(m);assert parse(encoded)[1]==m
backup=ROOT/'dist/backups/native-visibility';backup.mkdir(parents=True,exist_ok=True);assert not (backup/'viewport_watch.pyc').exists();(backup/'viewport_watch.pyc').write_bytes(original)
newpath=ROOT/'res/scripts/client/moe_calculator/bridge/native_visibility.pyc';assert not newpath.exists();newpath.write_bytes(encode(module));path.write_bytes(encoded)
report={'native_hud':'SharedPage.isGuiVisible','native_component':'BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL','event':'GameEvent.GUI_VISIBILITY','poll_fallback_seconds':0.25,'spectator_gate':'existing snapshot.is_spectating preserved','simulation_checks':['visible','HUD hidden','native damage component hidden/killcam','no page','no battle app','client exception','restore without clearing scoreboard gate','no repeated refresh for same visibility'],'runtime_verified':False}
(ROOT/'dist/native-visibility-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


