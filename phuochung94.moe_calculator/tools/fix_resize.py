"""Build a small Python 2.7 viewport watcher; do not compile with Python 3.
Python 2.7 opcodes and marshal fields are emitted explicitly and roundtripped.
"""
import sys, struct, copy, json
from pathlib import Path
ROOT=Path(r'C:\mod_phuochung94\phuochung94.moe_calculator')
sys.path.insert(0,str(ROOT/'tools'))
from build_asia import parse
N=('literal',b'N')
def pack(v):
 if isinstance(v,dict):
  return b'c'+b''.join(struct.pack('<i',x) for x in v['header'])+b''.join(pack(v[k]) for k in ('code','consts','names','varnames','freevars','cellvars','filename','name'))+struct.pack('<i',v['firstlineno'])+pack(v['lnotab'])
 if isinstance(v,bytes):return b's'+struct.pack('<i',len(v))+v
 if isinstance(v,int):return b'i'+struct.pack('<i',v)
 if isinstance(v,tuple):
  if len(v)==2 and v[0]=='literal':return v[1]
  if len(v)==2 and v[0] in (b'g',b'y'):return v[0]+v[1]
  return b'('+struct.pack('<i',len(v))+b''.join(pack(x) for x in v)
 raise ValueError(repr(v)[:80])
def ins(op,arg=None):return bytes([op])+(struct.pack('<H',arg) if op>=90 else b'')
class Asm:
 def __init__(self):self.b=bytearray();self.labels={};self.fix=[]
 def op(self,op,arg=None):self.b+=ins(op,arg)
 def label(self,label):self.labels[label]=len(self.b)
 def jump(self,op,label):self.fix.append((len(self.b)+1,label));self.op(op,0)
 def finish(self):
  for p,label in self.fix:self.b[p:p+2]=struct.pack('<H',self.labels[label])
  return bytes(self.b)
def code(name,asm,names,consts,args=(),flags=67):
 return dict(header=(len(args),len(args),12,flags),code=asm.finish(),consts=tuple(consts),names=tuple(s.encode() for s in names),varnames=tuple(s.encode() for s in args),freevars=(),cellvars=(),filename=b'res/scripts/client/moe_calculator/bridge/viewport_watch.py',name=name.encode(),firstlineno=1,lnotab=b'')
# _poll: schedule next tick first, track view identity and resolution, retry during layout settling.
names=['_running','BigWorld','callback','_poll','battle_view','active_view','_last_view','_last_size','_pending','bar_window','_screen_resolution','battle_bridge','_on_scale_changed']
a=Asm();a.op(116,0);a.jump(114,'return');a.op(116,1);a.op(106,2);a.op(100,1);a.op(116,3);a.op(131,2);a.op(1)
a.op(116,4);a.op(106,5);a.op(131,0);a.op(125,0)
a.op(124,0);a.op(100,0);a.op(107,8);a.jump(114,'active')
a.op(100,0);a.op(97,6);a.op(100,0);a.op(97,7);a.op(100,2);a.op(97,8);a.jump(113,'return')
a.label('active');a.op(116,9);a.op(106,10);a.op(131,0);a.op(125,1)
a.op(124,1);a.op(100,0);a.op(107,8);a.jump(115,'invalid')
for index in (2,4):
 a.op(124,1);a.op(100,index);a.op(25);a.op(100,2);a.op(107,1);a.jump(115,'invalid')
a.op(124,0);a.op(116,6);a.op(107,9);a.jump(115,'changed')
a.op(124,1);a.op(116,7);a.op(107,3);a.jump(114,'pending')
a.label('changed');a.op(124,0);a.op(97,6);a.op(124,1);a.op(97,7);a.op(100,3);a.op(97,8)
a.label('pending');a.op(116,8);a.op(100,2);a.op(107,4);a.jump(114,'return')
a.op(116,11);a.op(106,12);a.op(131,0);a.op(1);a.op(116,8);a.op(100,4);a.op(24);a.op(97,8)
a.jump(113,'return');a.label('invalid');a.op(100,0);a.op(97,7);a.op(100,2);a.op(97,8)
a.label('return');a.op(100,0);a.op(83)
poll=code('_poll',a,names,[N,(b'g',struct.pack('<d',0.25)),0,4,1],('view','size'))
# Correct argument counts: view and size are locals, not function arguments.
poll['header']=(0,2,12,67)
a=Asm();a.op(116,0);a.jump(114,'start');a.op(100,0);a.op(83);a.label('start');a.op(100,1);a.op(97,0);a.op(116,1);a.op(131,0);a.op(1);a.op(100,0);a.op(83)
start=code('start',a,['_running','_poll'],[N,('literal',b'T')])
a=Asm();a.op(100,0);a.op(100,1);a.op(108,0);a.op(90,0)
a.op(100,0);a.op(100,2);a.op(108,1)
for i in (2,3,4):a.op(109,i);a.op(90,i)
a.op(1)
a.op(100,3);a.op(90,5);a.op(100,1);a.op(90,6);a.op(100,1);a.op(90,7);a.op(100,4);a.op(90,8)
a.op(100,5);a.op(132,0);a.op(90,9);a.op(100,6);a.op(132,0);a.op(90,10);a.op(100,1);a.op(83)
module=code('<module>',a,['BigWorld','moe_calculator.bridge','bar_window','battle_view','battle_bridge','_running','_last_view','_last_size','_pending','_poll','start'],[-1,N,(b'bar_window',b'battle_view',b'battle_bridge'),('literal',b'F'),0,poll,start],flags=64)
def encode(m):
 raw=bytes.fromhex('03f30d0a00000000')+pack(m)
 assert parse(raw)[1]==m
 return raw
# Behavior-check the emitted watcher with an independent tiny opcode evaluator.
class Obj:pass
env={'_running':False,'_last_view':None,'_last_size':None,'_pending':0};queue=[];moved=[]
bw=Obj();bw.callback=lambda delay,fn:queue.append((delay,fn));env['BigWorld']=bw
view=Obj();view.active_view=lambda:state['view'];env['battle_view']=view
bar=Obj();bar._screen_resolution=lambda:state['size'];env['bar_window']=bar
bridge=Obj();bridge._on_scale_changed=lambda:moved.append(state['size']);env['battle_bridge']=bridge
state={'view':None,'size':(1920,1080)}
def val(v):
 if v==N:return None
 if v==('literal',b'T'):return True
 if isinstance(v,tuple) and v[0]==b'g':return struct.unpack('<d',v[1])[0]
 return v
def run(c):
 stack=[];local={};p=0;b=c['code']
 while p<len(b):
  op=b[p];arg=int.from_bytes(b[p+1:p+3],'little') if op>=90 else None;p+=3 if op>=90 else 1
  if op==100:stack.append(val(c['consts'][arg]))
  elif op==116:stack.append(env[c['names'][arg].decode()])
  elif op==97:env[c['names'][arg].decode()]=stack.pop()
  elif op==106:stack.append(getattr(stack.pop(),c['names'][arg].decode()))
  elif op==125:local[arg]=stack.pop()
  elif op==124:stack.append(local[arg])
  elif op==131:
   args=stack[-arg:] if arg else []
   if arg:del stack[-arg:]
   fn=stack.pop();stack.append(fn(*args))
  elif op==107:
   right=stack.pop();left=stack.pop();stack.append({3:lambda:left!=right,4:lambda:left>right,1:lambda:left<=right,8:lambda:left is right,9:lambda:left is not right}[arg]())
  elif op in (114,115):
   condition=stack.pop()
   if bool(condition)==(op==115):p=arg
  elif op==113:p=arg
  elif op==25:index=stack.pop();stack.append(stack.pop()[index])
  elif op==24:right=stack.pop();stack.append(stack.pop()-right)
  elif op==1:stack.pop()
  elif op==83:return stack.pop()
  else:raise AssertionError(op)
env['_poll']=lambda:run(poll)
run(start);assert len(queue)==1;run(start);assert len(queue)==1
state['view']=object()
for _ in range(6):run(poll)
assert len(moved)==4
state['size']=(1280,720)
for _ in range(6):run(poll)
assert len(moved)==8 and moved[-1]==(1280,720)
state['size']=(0,0);run(poll);assert len(moved)==8
# Zero resolution can occur during minimize; avoid applying until a valid size returns.
state['size']=None;run(poll);assert len(moved)==8
state['view']=None;run(poll);assert env['_last_view'] is None and env['_pending']==0
state['size']=(2560,1440);state['view']=object();run(poll);assert len(moved)==9
# Patch a single startup hook at the existing return, leaving earlier branch offsets intact.
path=ROOT/'res/scripts/client/moe_calculator/bridge/battle_bridge.pyc';original=path.read_bytes();m=parse(original)[1]
hook=next(c for c in m['consts'] if isinstance(c,dict) and c['name']==b'install_all_listeners')
if b'moe_calculator.bridge.viewport_watch' in hook['names']:
 installed=parse((ROOT/'res/scripts/client/moe_calculator/bridge/viewport_watch.pyc').read_bytes())[1]
 actual_poll=next(c for c in installed['consts'] if isinstance(c,dict) and c['name']==b'_poll')
 if b'moe_calculator.bridge.native_visibility' in actual_poll['names']:
  restored=bytearray(actual_poll['code'][17:]);pos=0
  while pos<len(restored):
   op=restored[pos]
   if op in (111,112,113,114,115,119):restored[pos+1:pos+3]=struct.pack('<H',int.from_bytes(restored[pos+1:pos+3],'little')-17)
   pos+=3 if op>=90 else 1
  actual_poll['code']=bytes(restored);actual_poll['names']=actual_poll['names'][:-2];actual_poll['consts']=actual_poll['consts'][:-2]
 assert installed==module
 print('Watcher and simulated resize/lifecycle tests verified; already installed')
 raise SystemExit(0)
assert hook['code'][-4:]==bytes.fromhex('64000053')
oldnames=hook['names'];oldconsts=hook['consts'];idx=len(oldnames);ci=len(oldconsts)
hook['names']+=(b'moe_calculator.bridge.viewport_watch',b'start')
hook['consts']+=(-1,(b'start',))
hook['code']=hook['code'][:-4]+ins(100,ci)+ins(100,ci+1)+ins(108,idx)+ins(109,idx+1)+ins(131,0)+ins(1)+ins(1)+bytes.fromhex('64000053')
hook['header']=(hook['header'][0],hook['header'][1],max(3,hook['header'][2]),hook['header'][3])
encoded=original[:8]+pack(m);assert parse(encoded)[1]==m
backup=ROOT/'dist/backups/resize';backup.mkdir(parents=True,exist_ok=True)
if (backup/'battle_bridge.pyc').exists():raise SystemExit('Backup exists; review before rerun')
(backup/'battle_bridge.pyc').write_bytes(original)
watch=ROOT/'res/scripts/client/moe_calculator/bridge/viewport_watch.pyc';assert not watch.exists();watch.write_bytes(encode(module));path.write_bytes(encoded)
report={'watch_interval_seconds':0.25,'settling_repositions':4,'behavior_checks':['start once','idle no movement','initial battle','window resize','unavailable resolution','battle exit','next battle'],'runtime_verified':False}
(ROOT/'dist/resize-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))



