"""Presentation lifecycle only: no penetration algorithm replacements."""
import traceback

_INSTALLED = False
_METHODS = []
_EVENTS = []
_SESSION = None

def _safe(callback, *args, **kwargs):
    try:
        callback(*args, **kwargs)
    except Exception:
        traceback.print_exc()

def _state():
    from armorshotanalyzer.gui.armorshotanalyzer_gui import gui_state
    return gui_state

def _ready(*args, **kwargs):
    if _INSTALLED:
        _safe(lambda: _state().create_window())

def _leave(*args, **kwargs):
    if _INSTALLED:
        _close_window()

def _close_window():
    # A failure hiding one label must not skip disabling/closing the window.
    _safe(lambda: _state().destroy_window())
    _safe(lambda: setattr(_state(), 'enabled', False))
    def close():
        from armorshotanalyzer.gui.armorshotanalyzer_gameface_api import ap_window
        ap_window.close_window()
    _safe(close)

def _replace(cls, name, replacement):
    local = name in cls.__dict__
    previous = next(base.__dict__[name] for base in cls.__mro__ if name in base.__dict__)
    _METHODS.append((cls, name, local, previous, replacement))
    setattr(cls, name, replacement)

def install():
    global _INSTALLED, _SESSION
    if _INSTALLED:
        return
    if _EVENTS or _METHODS:
        uninstall()
    from AvatarInputHandler import AvatarInputHandler, gun_marker_ctrl
    from PlayerEvents import g_playerEvents
    from aih_constants import SHOT_RESULT
    cls = gun_marker_ctrl._CrosshairShotResults
    original_shot = cls.getShotResult.__func__
    original_postmortem = AvatarInputHandler.activatePostmortem
    session = _SESSION = object()
    def shot(owner, *args, **kwargs):
        result = original_shot(owner, *args, **kwargs)
        if _INSTALLED and _SESSION is session:
            def present():
                if result == SHOT_RESULT.UNDEFINED:
                    _state().hide_all()
            _safe(present)
        return result
    def postmortem(owner, *args, **kwargs):
        result = original_postmortem(owner, *args, **kwargs)
        if _INSTALLED and _SESSION is session:
            _safe(lambda: _state().hide_all())
        return result
    def ready(*args, **kwargs):
        if _INSTALLED and _SESSION is session:
            _ready(*args, **kwargs)
    def leave(*args, **kwargs):
        if _INSTALLED and _SESSION is session:
            _leave(*args, **kwargs)
    try:
        _replace(cls, 'getShotResult', classmethod(shot))
        _replace(AvatarInputHandler, 'activatePostmortem', postmortem)
        for event, callback in ((g_playerEvents.onAvatarReady, ready),
                                (g_playerEvents.onAvatarBecomeNonPlayer, leave)):
            _EVENTS.append((event, callback))
            event += callback
        _INSTALLED = True
    except Exception:
        uninstall()
        raise

def uninstall():
    global _INSTALLED, _SESSION
    _INSTALLED = False
    _SESSION = None
    pending = []
    for event, callback in reversed(_EVENTS):
        try:
            event -= callback
        except (ValueError, KeyError):
            pass  # Already removed by the host.
        except Exception:
            traceback.print_exc()
            pending.append((event, callback))
    _EVENTS[:] = list(reversed(pending))
    for cls, name, local, previous, replacement in reversed(_METHODS):
        # Do not erase a later hook installed by another mod. Our wrapper is
        # inert after uninstall even when another mod retained it in its chain.
        if cls.__dict__.get(name) is replacement:
            if local:
                setattr(cls, name, previous)
            else:
                delattr(cls, name)
    del _METHODS[:]
    _close_window()
