import marshal, types, dis, sys, os
path = os.path.join(os.path.dirname(__file__), 'client_inspection')
code = marshal.loads(open(os.path.join(path, 'gun_marker_ctrl.pyc'), 'rb').read()[8:])
sys.stdout = open(os.path.join(path, 'crit_signal.txt'), 'w')
for value in code.co_consts:
    if isinstance(value, types.CodeType) and value.co_name == '_CrosshairShotResults':
        dis.dis(value)
