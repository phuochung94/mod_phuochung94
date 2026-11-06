from __future__ import absolute_import

import logging
from helpers import getClientLanguage
from gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue import BattleQueue, RandomQueueProvider

_log = logging.getLogger('phuochung94.compact_queue')
_originals = {}


def _is_random(view):
    return type(view._getProvider()) is RandomQueueProvider


def _type_info(view, data):
    if _is_random(view):
        data = dict(data)
        language = (getClientLanguage() or '').lower().replace('-', '_')
        vietnamese = language.split('_')[0] in ('vi', 'vn')
        data['title'] = 'MOD_QUEUE_VI' if vietnamese else 'MOD_QUEUE_EN'
        data['tankLabel'] = ''
        data['tankIcon'] = ''
        data['tankName'] = ''
    return _originals['type_info'](view, data)


def _populate(view):
    result = _originals['populate'](view)
    if _is_random(view):
        view._blur.disable()
    return result


def _show_externals(view, event):
    if _is_random(view):
        view._blur.disable()
        return
    return _originals['show_externals'](view, event)


def init():
    if _originals:
        return
    _originals.update(type_info=BattleQueue.as_setTypeInfoS,
                      populate=BattleQueue._populate,
                      show_externals=BattleQueue._onShowExternals)
    BattleQueue.as_setTypeInfoS = _type_info
    BattleQueue._populate = _populate
    BattleQueue._onShowExternals = _show_externals
    _log.info('Compact random battle queue enabled, Vietnamese/English')


def fini():
    if not _originals:
        return
    BattleQueue.as_setTypeInfoS = _originals['type_info']
    BattleQueue._populate = _originals['populate']
    BattleQueue._onShowExternals = _originals['show_externals']
    _originals.clear()
