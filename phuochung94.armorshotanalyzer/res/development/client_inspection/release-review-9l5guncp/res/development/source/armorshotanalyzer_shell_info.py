# -*- coding: utf-8 -*-
"""Loaded-shell penetration overlay. Python 2.7 / BigWorld compatible.

Only presentation is changed: the existing shot-result methods retain their
return values and remain responsible for the game's crosshair result.
"""
import math

SHELL_LABELS = {
    'ARMOR_PIERCING': 'AP',
    'ARMOR_PIERCING_CR': 'APCR',
    'ARMOR_PIERCING_COMPOSITE_RIGID': 'APCR',
    'HOLLOW_CHARGE': 'HEAT',
    'HIGH_EXPLOSIVE_ANTI_TANK': 'HEAT',
    'HIGH_EXPLOSIVE': 'HE',
    'HIGH_EXPLOSIVE_SQUASH_HEAD': 'HESH',
}
_INSTALLED = False
_ERROR_REPORTED = False
_METHOD_HOOKS = []
_SESSION = None
DISPLAY_PALETTE = dict(HIGH_CHANCE='9CFF3A', MEDIUM_CHANCE='FFC04D',
                       LOW_CHANCE='FF4040', RICOCHET='FF4040', GREY='D0D0D0')


def penetration_probability(average, required, randomization):
    """Reference 2.2.0 Gaussian with fixed 75%-125% bounds.

    randomization is retained for caller compatibility; the reference Gaussian
    does not use it (the layer/module calculation still uses shell RNG).
    """
    if average <= 0 or math.isinf(required):
        return 0.0
    if required <= average * 0.75:
        return 100.0
    if required >= average * 1.25:
        return 0.0
    z = 6.0 * math.sqrt(2.0) * (required - average) / average
    return (1.0 - 0.5 * (1.0 + math.erf(z))) * 100.0


def impact_angle(detail):
    cosine = getattr(detail, 'hitAngleCos', None)
    if cosine is None or not -1.0 <= cosine <= 1.0:
        return None
    return int(math.degrees(math.acos(cosine)))


def analyze_shot(cls, collisions, average, shell, entity, modern_he=False,
                 shield_factor=1.0, max_pp=125):
    """Reference 2.2.0 overlay armor accumulation, separate from client results.

    HEAT adds the penetration lost by the mean shot, not armor/scale.
    Current game helpers supply armor and ricochet. Missing data stays unknown.
    """
    label = SHELL_LABELS.get(shell.kind, str(shell.kind))
    info = dict(shell=label, average=float(average), required=0.0,
                probability=0.0, spaced=False, ricochet=False,
                hit_body=False, hit_track=False, angle=None, known=True,
                blocked=False, module_possible=False)
    if not collisions:
        return None
    extra = cls._SHELL_EXTRA_DATA[shell.kind]
    has_loss = bool(extra.hasPenetrationLoss) and not modern_he
    remaining = float(average)
    jet_start = None
    ignored = set()
    seen = False
    for detail in collisions:
        if not cls._CrosshairShotResults__isDestructibleComponent(entity, detail.compName):
            break
        material = detail.matInfo
        seen = True
        info['hit_track'] |= detail.compName == 0 or detail.compName >= 4
        if has_loss and jet_start is not None:
            gap = max(0.0, detail.dist - jet_start)
            loss = float(shell.type.piercingPowerLossFactorByDistance)
            if gap > 0:
                factor = 1.0 - gap * loss
                info['required'] += max(0.0, remaining * (1.0 - factor))
                remaining *= factor
        if material is None:
            # Match the existing game's collision loop for module-only hits.
            if (remaining > 0 and info['required'] < average *
                    (1.0 + max(0.0, float(shell.piercingPowerRandomization)))):
                info['module_possible'] = True
            if has_loss:
                jet_start = detail.dist
            continue
        key = (detail.compName, material.kind)
        if key in ignored:
            continue
        if material.armor is None:
            info['known'] = False
            return info
        cosine = detail.hitAngleCos if material.useHitAngle else 1.0
        if not modern_he and jet_start is None and cls._shouldRicochet(shell, cosine, material):
            info['ricochet'] = True
            info['angle'] = impact_angle(detail)
            return info
        armor = max(0.0, float(cls._computePenetrationArmor(shell, cosine, material)))
        piercing_percent = (100.0 + (armor - remaining) / average * 100.0
                            if average > 0 and (modern_he or remaining > 0) else 1000.0)
        if material.vehicleDamageFactor:
            info['hit_body'] = True
            info['angle'] = impact_angle(detail)
            info['required'] += armor
            break
        if armor > 0.0:
            info['spaced'] = True
        if modern_he:
            if not shell.type.shieldPenetration:
                info['blocked'] = True
                return info
            armor *= shield_factor
        info['required'] += armor
        if modern_he or remaining > 0:
            remaining -= armor
        if modern_he and piercing_percent > max_pp:
            info['blocked'] = True
            return info
        if getattr(material, 'extra', None) and piercing_percent <= max_pp:
            info['module_possible'] = True
        if material.collideOnceOnly:
            ignored.add(key)
        if has_loss:
            jet_start = detail.dist + max(0.0, float(material.armor)) * 0.001
    if not seen:
        return None
    if info['hit_body'] and not info['blocked']:
        info['probability'] = penetration_probability(
            average, info['required'], shell.piercingPowerRandomization)
    return info


def primary_status(info):
    if info['ricochet']:
        return 'RICOCHET'
    if info['blocked']:
        return 'NO PEN'
    if not info['hit_body']:
        return 'NO HULL'
    if info['probability'] == 0:
        return 'NO PEN'
    return 'SPACED' if info['spaced'] else ''


def no_direct_hp_damage(info):
    # Full-penetration probability cannot determine HE/HESH explosion damage.
    # This concerns HP on the intersected target, not track/module damage.
    return (info['known'] and info['shell'] in ('AP', 'APCR', 'HEAT')
            and (info['ricochet'] or info['blocked'] or not info['hit_body']
                 or info['probability'] == 0))


def format_info(info):
    if not info['known']:
        return '?'
    return primary_status(info)


def install():
    global _INSTALLED, _SESSION
    if _INSTALLED:
        return
    from AvatarInputHandler import gun_marker_ctrl
    from items.components.component_constants import MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
    from armorshotanalyzer.gui.armorshotanalyzer_gui import gui_state
    from armorshotanalyzer.gui.armorshotanalyzer_gameface_api import ap_window
    from armorshotanalyzer.gui.armorshotanalyzer_constants import (GlobalSettings, Colors, AngleLabelSettings,
        TrackIndicatorSettings, get_color_from_prob, get_ricochet_color)
    from armorshotanalyzer.debug import log

    # Apply the integrated HUD palette to the original gradient and all labels.
    for name, value in DISPLAY_PALETTE.items():
        setattr(Colors, name, value)
    Colors.GRADIENT = True
    gui_state.prob_label.settings.ENABLED = False

    # Keep the existing base bytecode intact; enforce the approved UI setting
    # here at initialization and after any later settings refresh.
    AngleLabelSettings.ENABLED = True
    AngleLabelSettings.DISPLAY_THRESHOLD = 0
    AngleLabelSettings.WHITE = True
    gui_state.angle_label.hide()

    def show(info):
        AngleLabelSettings.ENABLED = False
        if not gui_state.enabled or not GlobalSettings.MOD_ENABLED or info is None:
            gui_state.hide_all()
            AngleLabelSettings.ENABLED = True
            return
        if info['known']:
            probability = info['probability']
            if primary_status(info) in ('NO PEN', 'NO HULL', 'RICOCHET'):
                if info['module_possible']:
                    color = Colors.MEDIUM_CHANCE
                elif no_direct_hp_damage(info):
                    color = Colors.LOW_CHANCE
                else:
                    # No splash-damage model: HE/HESH cannot be called futile.
                    color = Colors.GREY
            else:
                color = get_color_from_prob(probability)
            required = info['required']
            armor = int(round(required)) if not math.isinf(required) else 0
            gui_state.update_gui(armor, int(round(probability)), info['ricochet'],
                                 info['hit_body'], info['angle'] or 0, info['hit_track'])
            if (gui_state.armor_label.settings.ENABLED and
                    (info['hit_body'] or info['ricochet'] or info['module_possible'])):
                value = '-' if not info['hit_body'] or math.isinf(required) else armor
                gui_state.armor_label.update_gui(value, color)
            # A gradient need not equal the high-color endpoint even at >80%.
            if TrackIndicatorSettings.ENABLED:
                if info['hit_track'] and info['hit_body'] and probability > 80:
                    gui_state.track_indicator.show()
                else:
                    gui_state.track_indicator.hide()
        else:
            color = Colors.GREY
            gui_state.hide_labels()
            gui_state.track_indicator.hide()
        # Reuse the probability row, and its visibility state, so all existing
        # hide/postmortem/window teardown paths also hide this richer label.
        AngleLabelSettings.ENABLED = True
        AngleLabelSettings.DISPLAY_THRESHOLD = 0
        AngleLabelSettings.WHITE = True
        angle_visible = info['known'] and info['angle'] is not None
        if angle_visible:
            gui_state.angle_label.update_gui(info['angle'], 'FFFFFF')
        else:
            gui_state.angle_label.hide()
        # Keep status analysis for color decisions, but never display its row.
        text = ''
        gui_state.prob_label.settings.ENABLED = False
        gui_state.prob_label.visible = False
        gui_state.prob_label.last_state = None
        params = [('probText', text), ('probVisible', bool(text)), ('probColor', color),
                  ('angleVisible', angle_visible)]
        if angle_visible:
            params += [('angleText', '%d\xc2\xb0' % info['angle']), ('angleColor', 'FFFFFF')]
        ap_window.update_params(params)

    cls = gun_marker_ctrl._CrosshairShotResults
    session = _SESSION = object()
    def wrap(method, modern_he):
        original = getattr(cls, method).__func__
        def wrapped(owner, gunMarker, collisionsDetails, fullPiercingPower,
                    shell, minPP, maxPP, entity):
            # Call the real client first with the identical objects. Never
            # consume an iterator or replace its collision sequence.
            result = original(owner, gunMarker, collisionsDetails, fullPiercingPower,
                              shell, minPP, maxPP, entity)
            if not _INSTALLED or _SESSION is not session:
                return result
            try:
                if type(collisionsDetails) not in (list, tuple):
                    show(None)
                    return result
                info = analyze_shot(owner, tuple(collisionsDetails), fullPiercingPower, shell,
                    entity, modern_he,
                    MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS, maxPP)
                show(info)
            except Exception as error:
                global _ERROR_REPORTED
                try:
                    gui_state.hide_all()
                    AngleLabelSettings.ENABLED = True
                    if not _ERROR_REPORTED:
                        _ERROR_REPORTED = True
                        log('Loaded-shell overlay: %s' % error)
                except Exception:
                    pass
            return result
        return classmethod(wrapped)
    try:
        for method, modern_he in (
            ('_CrosshairShotResults__shotResultDefault', False),
            ('_CrosshairShotResults__shotResultModernHE', True)):
            had_local = method in cls.__dict__
            previous = next(base.__dict__[method] for base in cls.__mro__ if method in base.__dict__)
            replacement = wrap(method, modern_he)
            _METHOD_HOOKS.append((cls, method, had_local, previous, replacement))
            setattr(cls, method, replacement)
        _INSTALLED = True
    except Exception:
        uninstall()
        raise


def uninstall():
    global _INSTALLED, _ERROR_REPORTED, _SESSION
    _INSTALLED = False
    _SESSION = None
    for cls, name, had_local, previous, replacement in reversed(_METHOD_HOOKS):
        if cls.__dict__.get(name) is replacement:
            if had_local:
                setattr(cls, name, previous)
            else:
                delattr(cls, name)
    del _METHOD_HOOKS[:]
    _ERROR_REPORTED = False
