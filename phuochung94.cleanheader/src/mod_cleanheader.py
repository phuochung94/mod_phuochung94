# -*- coding: utf-8 -*-
"""Expose the game's current-cluster online count to the native header model."""
import traceback
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IServerStatsController
from gui.game_control.ServerStats import STATS_TYPE
from gui.impl.gen.view_models.views.lobby.page.header.user_account_model import UserAccountModel
from gui.impl.lobby.page.user_account_presenter import UserAccountPresenter

_PROPERTY = 2
try:
    _text_type = unicode
except NameError:
    _text_type = str


def _text(value):
    if value is None:
        return u''
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return _text_type(value)


def _install():
    if getattr(UserAccountModel, '_cleanheader_online_installed', False):
        return
    original_init = UserAccountModel.__init__
    original_initialize = UserAccountModel._initialize
    original_events = UserAccountPresenter._getEvents
    original_loading = UserAccountPresenter._onLoading

    def model_init(self, properties=2, commands=1):
        original_init(self, properties=properties + 1, commands=commands)

    def initialize(self):
        original_initialize(self)
        self._addStringProperty('cleanheaderOnline', '')

    def clear_online(self, *args, **kwargs):
        with self.viewModel.transaction():
            self.viewModel._setString(_PROPERTY, '')

    def update_online(self, *args, **kwargs):
        value = u''
        server = u''
        try:
            server = _text(dependency.instance(IConnectionManager).serverUserNameShort).strip().upper()
            cluster, region, status = dependency.instance(IServerStatsController).getStats()
            count = _text(cluster) if status != STATS_TYPE.UNAVAILABLE and cluster not in (None, '', '-') else u'\u2014'
            if server:
                value = server + u'  ' + count
        except Exception:
            if server:
                value = server + u'  \u2014'
            print('[cleanheader] Server population unavailable')
            traceback.print_exc()
        with self.viewModel.transaction():
            self.viewModel._setString(_PROPERTY, value)

    def events(self):
        controller = dependency.instance(IServerStatsController)
        return tuple(original_events(self)) + (
            (controller.onStatsReceived, self._cleanheader_update_online),
            (g_playerEvents.onDisconnected, self._cleanheader_clear_online),
            (g_playerEvents.onAccountBecomeNonPlayer, self._cleanheader_clear_online))

    def loading(self, *args, **kwargs):
        result = original_loading(self, *args, **kwargs)
        self._cleanheader_update_online()
        return result

    UserAccountModel.__init__ = model_init
    UserAccountModel._initialize = initialize
    UserAccountPresenter._cleanheader_update_online = update_online
    UserAccountPresenter._cleanheader_clear_online = clear_online
    UserAccountPresenter._getEvents = events
    UserAccountPresenter._onLoading = loading
    UserAccountModel._cleanheader_online_installed = True
    print('[cleanheader] Native current-server online counter installed')


try:
    _install()
except Exception:
    print('[cleanheader] Cannot install online counter on this client')
    traceback.print_exc()
