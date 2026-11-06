import os,marshal,types,dis,sys
root=os.path.dirname(__file__)
sys.stdout=open(os.path.join(root,'client_inspection/reference_calculation.txt'),'w')
def walk(code):
    print(code.co_name,code.co_varnames[:code.co_argcount],code.co_names)
    if code.co_name in ('gaussian_probability','my_shot_result_default','my_shot_result_modern_he'):
        dis.dis(code)
    for value in code.co_consts:
        if isinstance(value,types.CodeType):walk(value)
for name in ('ap_math.pyc','ap_hooks.pyc'):
    data=open(os.path.join(root,'reference_2_2_0',name),'rb').read()
    assert data[:4]=='\x03\xf3\x0d\x0a'
    walk(marshal.loads(data[8:]))
