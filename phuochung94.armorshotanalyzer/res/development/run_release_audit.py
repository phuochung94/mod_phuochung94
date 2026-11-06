"""Run in the client Python 2.7 host against extracted delivery bytecode."""
import json, os, sys, types, unittest, marshal
here = os.path.dirname(__file__)
report_path = os.path.join(here,'client_inspection/final_release_review.json')
report = json.load(open(report_path))
stage = report['stage']; development = os.path.join(stage,'res/development')
sys.argv = ['release_tests']
os.environ['AP_TEST_BYTECODE'] = '1'
module = types.ModuleType('release_bytecode_tests')
module.__file__ = os.path.join(development,'tests/test_shell_info.py')
sys.modules[module.__name__] = module
execfile(module.__file__, module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
assert suite.countTestCases() >= 73
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise RuntimeError('Packaged-bytecode tests failed')
namespace = dict(__name__='__main__',__file__=os.path.join(development,'audit_privacy.py'))
execfile(namespace['__file__'], namespace)
# OpenWG is audited statically, never imported into the test process.
for directory, _, files in os.walk(os.path.join(stage,'dependency')):
    for name in files:
        if name.endswith('.pyc'):
            namespace['walk'](marshal.loads(open(os.path.join(directory,name),'rb').read()[8:]))
namespace = dict(__name__='__main__',__file__=os.path.join(development,'audit_no_menus.py'))
execfile(namespace['__file__'], namespace)
report['artifact_tests'] = 'PASS'
report['packaged_bytecode_test_count'] = suite.countTestCases()
report['mod_and_openwg_privacy_static_audit'] = 'PASS'
with open(report_path,'w') as stream: json.dump(report,stream,indent=2)
print('DELIVERED ARCHIVE AUDIT PASS: '+str(suite.countTestCases())+' bytecode tests')
