"""Test the native-model bridge without loading game modules."""
import contextlib
import io
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch
import zipfile
from build import ROOT, GAME

SOURCE = (ROOT / 'src/mod_cleanheader.py').read_bytes()


class Event:
    def __init__(self): self.handlers = []
    def fire(self, *args):
        for handler in tuple(self.handlers): handler(*args)


class Online(unittest.TestCase):
    def setUp(self):
        self.log = io.StringIO()
        capture = contextlib.ExitStack()
        capture.enter_context(contextlib.redirect_stdout(self.log))
        capture.enter_context(contextlib.redirect_stderr(self.log))
        self.addCleanup(capture.close)
        self.stats = ('12,345', '98,765', 'regionCCU/clusterCCU')
        self.fail = False
        def get_stats():
            if self.fail: raise RuntimeError('unavailable')
            return self.stats
        self.connection = types.SimpleNamespace(serverUserNameShort='ASIA1')
        stats_interface, connection_interface = object(), object()
        self.controller = types.SimpleNamespace(getStats=get_stats, onStatsReceived=Event())
        self.events = types.SimpleNamespace(onDisconnected=Event(), onAccountBecomeNonPlayer=Event())
        class Model:
            def __init__(self, properties=2, commands=1):
                self.properties=properties; self.commands=commands; self.fields=[]; self.values={}
                self._initialize()
            def _initialize(self): self.fields.extend(['userInfo', 'subscriptions'])
            def _addStringProperty(self, name, value):
                self.values[len(self.fields)] = value; self.fields.append(name)
            def _setString(self, index, value):
                assert index < len(self.fields)
                self.values[index] = value
            def transaction(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
        original_event = Event()
        class Presenter:
            def __init__(self): self.viewModel = Model(); self.loaded = False
            def _getEvents(self): return ((original_event, lambda: None),)
            def _onLoading(self, *args, **kwargs): self.loaded = True; return 'native-loading'
        self.Model = Model; self.Presenter = Presenter
        self.scope = {}
        modules = {
            'helpers': types.SimpleNamespace(dependency=types.SimpleNamespace(instance=lambda interface:self.connection if interface is connection_interface else self.controller)),
            'PlayerEvents': types.SimpleNamespace(g_playerEvents=self.events),
            'skeletons.gui.game_control': types.SimpleNamespace(IServerStatsController=stats_interface),
            'skeletons.connection_mgr': types.SimpleNamespace(IConnectionManager=connection_interface),
            'gui.game_control.ServerStats': types.SimpleNamespace(STATS_TYPE=types.SimpleNamespace(UNAVAILABLE='unavailable')),
            'gui.impl.gen.view_models.views.lobby.page.header.user_account_model': types.SimpleNamespace(UserAccountModel=Model),
            'gui.impl.lobby.page.user_account_presenter': types.SimpleNamespace(UserAccountPresenter=Presenter)}
        with patch.dict(sys.modules, modules): exec(compile(SOURCE,'mod_cleanheader.py','exec'),self.scope)
        self.presenter=Presenter()
        for event,handler in self.presenter._getEvents(): event.handlers.append(handler)
    def test_model_adds_one_string_without_changing_native_properties_or_commands(self):
        model=self.presenter.viewModel
        self.assertEqual(model.properties,3); self.assertEqual(model.commands,1)
        self.assertEqual(model.fields,['userInfo','subscriptions','cleanheaderOnline'])
    def test_loading_preserves_native_behavior_and_uses_current_cluster_not_region(self):
        self.assertEqual(self.presenter._onLoading(),'native-loading')
        self.assertTrue(self.presenter.loaded)
        self.assertEqual(self.presenter.viewModel.values[2],'ASIA1  12,345')
    def test_native_server_updates_refresh_counter(self):
        self.presenter._onLoading()
        self.stats=('21,456','100,000','regionCCU/clusterCCU')
        self.controller.onStatsReceived.fire()
        self.assertEqual(self.presenter.viewModel.values[2],'ASIA1  21,456')
    def test_unavailable_data_clears_old_count(self):
        self.presenter._onLoading()
        self.stats=('old','old','unavailable');self.controller.onStatsReceived.fire()
        self.assertEqual(self.presenter.viewModel.values[2],'ASIA1  ' + chr(0x2014))
    def test_disconnect_and_leaving_account_clear_data(self):
        for event in (self.events.onDisconnected,self.events.onAccountBecomeNonPlayer):
            self.presenter._onLoading(); event.fire()
            self.assertEqual(self.presenter.viewModel.values[2],'')
    def test_native_zero_is_preserved_and_missing_values_are_not_fabricated(self):
        for value,expected in [('0','0'),('-', ''),(None,''),('', '')]:
            self.stats=(value,'100','clusterCCUs');self.controller.onStatsReceived.fire()
            self.assertEqual(self.presenter.viewModel.values[2],'ASIA1  ' + (expected or chr(0x2014)))
    def test_provider_error_clears_old_value_without_crashing(self):
        self.presenter._onLoading(); self.fail=True;self.controller.onStatsReceived.fire()
        self.assertEqual(self.presenter.viewModel.values[2],'ASIA1  ' + chr(0x2014))
    def test_native_server_change_updates_name_and_count_together(self):
        self.presenter._onLoading()
        self.connection.serverUserNameShort = 'asia2'
        self.stats = ('23,456', '100,000', 'regionCCU/clusterCCU')
        self.controller.onStatsReceived.fire()
        self.assertEqual(self.presenter.viewModel.values[2], 'ASIA2  23,456')
    def test_missing_server_name_does_not_show_a_guessed_name(self):
        self.connection.serverUserNameShort = None
        self.presenter._onLoading()
        self.assertEqual(self.presenter.viewModel.values[2], '')
    def test_native_unicode_number_format_is_preserved(self):
        self.stats = ('12' + chr(0x202f) + '345', '100,000', 'clusterCCUs')
        self.presenter._onLoading()
        self.assertEqual(self.presenter.viewModel.values[2], 'ASIA1  12' + chr(0x202f) + '345')
    def test_repeat_install_does_not_wrap_model_twice(self):
        self.scope['_install']()
        self.assertEqual(self.Model().properties,3)
        self.assertEqual(len(self.presenter._getEvents()),4)


class Reader:
    def __init__(self,data):self.f=io.BytesIO(data);self.refs=[]
    def integer(self):return struct.unpack('<i',self.f.read(4))[0]
    def read(self):
        tag=self.f.read(1)
        if tag==b'N':return None
        if tag==b'T':return True
        if tag==b'F':return False
        if tag==b'i':return self.integer()
        if tag in (b's',b't',b'u'):
            value=self.f.read(self.integer())
            if tag==b't':self.refs.append(value)
            return value
        if tag==b'R':return self.refs[self.integer()]
        if tag==b'(':return tuple(self.read() for _ in range(self.integer()))
        if tag==b'g':return struct.unpack('<d',self.f.read(8))[0]
        if tag==b'c':
            result=dict(zip(('argc','nlocals','stack','flags'),(self.integer() for _ in range(4))))
            for key in ('code','consts','names','varnames','freevars','cellvars','filename','name'):result[key]=self.read()
            result['line']=self.integer();result['lnotab']=self.read();return result
        raise ValueError(tag)


class Contract(unittest.TestCase):
    def test_game_model_and_stats_match_native_contract(self):
        def find(code,name):
            if code['name']==name:return code
            for child in code['consts']:
                if isinstance(child,dict):
                    found=find(child,name)
                    if found:return found
        with zipfile.ZipFile(GAME/'res/packages/scripts.pkg') as archive:
            model=Reader(archive.read('scripts/client/gui/impl/gen/view_models/views/lobby/page/header/user_account_model.pyc')[8:]).read()
            stats=Reader(archive.read('scripts/client/gui/game_control/ServerStats.pyc')[8:]).read()
            server_info=Reader(archive.read('scripts/client/gui/impl/lobby/page/server_info_presenter.pyc')[8:]).read()
            presenter=Reader(archive.read('scripts/client/gui/impl/lobby/page/user_account_presenter.pyc')[8:]).read()
        initialize=find(model,b'_initialize')
        self.assertEqual([value for value in initialize['consts'] if isinstance(value,bytes)][:2],[b'userInfo',b'subscriptions'])
        self.assertEqual(find(model,b'__init__')['argc'],3)
        self.assertIn(b'clusterCCU',find(stats,b'getStats')['consts'])
        self.assertEqual(find(stats,b'getStats')['varnames'][-3:],(b'clusterUsers',b'regionUsers',b'tooltipType'))
        self.assertIsNotNone(find(presenter,b'_getEvents'))
        self.assertIn(b'serverUserNameShort', find(server_info,b'__updateModel')['names'])
    def test_python27_loader_contains_exact_bridge_source(self):
        from build import loader
        code=Reader(loader(SOURCE)[8:]).read()
        self.assertEqual(code['consts'][0],SOURCE)
        self.assertEqual(code['filename'],b'mod_cleanheader.py')


if __name__=='__main__':unittest.main(verbosity=2)
