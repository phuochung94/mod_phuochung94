import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class QueueIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.language = 'en'
        class RandomProvider:
            pass
        class OtherProvider:
            pass
        class View:
            def __init__(self, provider):
                self.provider = provider
                self._blur = Mock()
                self.data = None
                self.populated = 0

            def _getProvider(self):
                return self.provider

            def as_setTypeInfoS(self, data):
                self.data = data
                return 'sent'

            def _populate(self):
                self.populated += 1
                self._blur.enable()

            def _onShowExternals(self, event):
                self._blur.enable()

        self.View = View
        self.random = RandomProvider
        self.other = OtherProvider
        path = 'gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue'
        modules = {'helpers': types.SimpleNamespace(getClientLanguage=lambda: self.language),
                   path: types.SimpleNamespace(BattleQueue=View, RandomQueueProvider=RandomProvider)}
        for i in range(1, len(path.split('.'))):
            modules['.'.join(path.split('.')[:i])] = types.ModuleType('.'.join(path.split('.')[:i]))
        self.environment = patch.dict(sys.modules, modules)
        self.environment.start()
        spec = importlib.util.spec_from_file_location('compact_queue_tested', ROOT/'src/mod_compact_queue.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.init()

    def tearDown(self):
        self.module.fini()
        self.environment.stop()

    def test_vietnamese_and_english_fallback(self):
        view = self.View(self.random())
        for language, marker in [('vi', 'VI'), ('vi_VN', 'VI'), ('vn', 'VI'), ('en', 'EN'), ('de', 'EN'), ('ru', 'EN'), ('zh_CN', 'EN')]:
            self.language = language
            self.assertEqual(view.as_setTypeInfoS({'title': 'native', 'tankName': '121B'}), 'sent')
            self.assertEqual(view.data['title'], 'MOD_QUEUE_'+marker)
            self.assertEqual(view.data['tankName'], '')

    def test_native_input_is_not_mutated(self):
        data = {'title': 'native', 'tankName': '121B', 'additional': 'native warning'}
        view = self.View(self.random())
        view.as_setTypeInfoS(data)
        self.assertEqual(data['title'], 'native')
        self.assertEqual(data['tankName'], '121B')
        self.assertEqual(view.data['additional'], 'native warning')

    def test_other_modes_use_native_data_and_blur(self):
        view = self.View(self.other())
        data = {'title': 'native', 'tankName': '121B'}
        view.as_setTypeInfoS(data)
        self.assertIs(view.data, data)
        view._populate()
        view._onShowExternals(None)
        self.assertEqual(view._blur.enable.call_count, 2)
        view._blur.disable.assert_not_called()

    def test_random_queue_runs_native_population_and_removes_blur(self):
        view = self.View(self.random())
        view._populate()
        view._onShowExternals(None)
        self.assertEqual(view.populated, 1)
        self.assertEqual(view._blur.disable.call_count, 2)

    def test_install_is_idempotent_and_uninstall_restores_native_entry_points(self):
        entry = self.View.as_setTypeInfoS
        self.module.init()
        self.assertIs(self.View.as_setTypeInfoS, entry)
        self.module.fini()
        view = self.View(self.random())
        data = {'title': 'native'}
        view.as_setTypeInfoS(data)
        self.assertIs(view.data, data)


if __name__ == '__main__':
    unittest.main()
