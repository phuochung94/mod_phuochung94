# -*- coding: utf-8 -*-
from __future__ import division
import imp
import math
import os
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get('AP_TEST_BYTECODE'):
    mod = imp.load_compiled('armorshotanalyzer_shell_info_test', os.path.join(
        os.path.dirname(ROOT), 'scripts/client/armorshotanalyzer/core/armorshotanalyzer_shell_info.pyc'))
else:
    mod = imp.load_source('armorshotanalyzer_shell_info_test', os.path.join(ROOT, 'source', 'armorshotanalyzer_shell_info.py'))

class Obj(object):
    def __init__(self, **kw): self.__dict__.update(kw)

def shell(kind='HOLLOW_CHARGE', spread=0.25, shield=True):
    return Obj(kind=kind, piercingPowerRandomization=spread,
               type=Obj(piercingPowerLossFactorByDistance=0.5,
                        shieldPenetration=shield))

def layer(armor, distance, body=False, component=1, cosine=1.0, kind=1, once=False):
    return Obj(compName=component, dist=distance, hitAngleCos=cosine,
               matInfo=Obj(armor=armor, vehicleDamageFactor=body,
                           useHitAngle=True, kind=kind, collideOnceOnly=once,extra=False))

class Engine(object):
    _SHELL_EXTRA_DATA = dict((k, Obj(hasPenetrationLoss=(k=='HOLLOW_CHARGE')))
                            for k in mod.SHELL_LABELS)
    @staticmethod
    def _CrosshairShotResults__isDestructibleComponent(entity, component): return True
    @staticmethod
    def _shouldRicochet(shell, cosine, material): return cosine < 0.05
    @staticmethod
    def _computePenetrationArmor(shell, cosine, material): return material.armor / cosine

class CalculationTests(unittest.TestCase):
    def reference_overlay(self, details, loaded, modern=False, factor=3):
        import marshal,__builtin__
        filename=os.path.join(ROOT,'reference_2_2_0/ap_hooks.pyc')
        code=marshal.loads(open(filename,'rb').read()[8:])
        name='my_shot_result_modern_he' if modern else 'my_shot_result_default'
        function=next(c for c in code.co_consts if isinstance(c,types.CodeType) and c.co_name==name)
        captured=[]
        namespace=dict(__builtins__=__builtin__.__dict__,
            _SHOT_RESULT=Obj(NOT_PIERCED=1,LITTLE_PIERCED=2,GREAT_PIERCED=3,UNDEFINED=0),
            MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS=factor,
            call_update_gui=lambda *args:captured.append(args),log=lambda *args:None)
        class Proxy(Engine):pass
        Proxy._CRIT_ONLY_SHOT_RESULT=1
        Proxy._CrosshairShotResults__collectDebugPiercingData=staticmethod(lambda *args:None)
        Proxy._CrosshairShotResults__sendDebugInfo=staticmethod(lambda *args:None)
        loaded.armorDamage=(100,100);loaded.type.maxDamage=300
        types.FunctionType(function,namespace)(Proxy,None,details,300,loaded,75,125,Obj(health=100))
        self.assertTrue(captured)
        return captured[-1]

    def analyze(self, details, loaded=None, **kw):
        return mod.analyze_shot(Engine, details, 300, loaded or shell(), Obj(), **kw)
    def test_all_shell_labels(self):
        for kind, label in [('ARMOR_PIERCING','AP'),('ARMOR_PIERCING_CR','APCR'),
                            ('HOLLOW_CHARGE','HEAT'),('HIGH_EXPLOSIVE','HE')]:
            info=self.analyze([layer(300,0,True)], shell(kind))
            self.assertEqual(info['shell'], label)
            self.assertAlmostEqual(info['probability'],50)
    def test_heat_spaced_armor_matches_reference_mean_loss(self):
        info=self.analyze([layer(20,0),layer(180,1.02,True)])
        # Reference: 20mm screen + 140mm mean jet loss + 180mm hull.
        self.assertAlmostEqual(info['required'],340)
        self.assertGreater(info['probability'],0)
        self.assertEqual(mod.format_info(info),'SPACED')
    def test_heat_screen_does_not_imply_no_penetration(self):
        info=self.analyze([layer(10,0),layer(100,.11,True)])
        self.assertGreater(info['probability'],99)
        self.assertTrue(info['spaced'])
        self.assertNotIn('NO PEN',mod.format_info(info))
    def test_ap_has_no_heat_air_gap_penalty(self):
        info=self.analyze([layer(20,0),layer(180,1.02,True)],shell('ARMOR_PIERCING'))
        self.assertEqual(info['required'],200)
        self.assertEqual(info['probability'],100)
    def test_multiple_heat_gaps(self):
        info=self.analyze([layer(20,0),layer(20,.42,kind=2),layer(100,.84,True)])
        self.assertAlmostEqual(info['required'],236.8)
    def test_duplicate_collide_once_matches_reference_gap_order(self):
        first=layer(20,0,component=0,once=True)
        duplicate=layer(20,.52,component=0,once=True)
        info=self.analyze([first,duplicate,layer(100,1.02,True)])
        self.assertAlmostEqual(info['required'],295)
    def test_exhausted_jet_is_zero(self):
        info=self.analyze([layer(20,0),layer(100,3.02,True)])
        self.assertEqual(info['required'],540)
        self.assertEqual(info['probability'],0)
    def test_track_only_cannot_damage_hull(self):
        info=self.analyze([layer(20,0,component=0)])
        self.assertTrue(info['hit_track'])
        self.assertEqual(info['probability'],0)
        self.assertIn('NO HULL',mod.format_info(info))
    def test_ricochet(self):
        info=self.analyze([layer(100,0,True,cosine=.01)])
        self.assertTrue(info['ricochet'])
        self.assertIn('RICOCHET',mod.format_info(info))
    def test_no_secondary_heat_ricochet(self):
        info=self.analyze([layer(10,0),layer(1,.01,True,cosine=.01)])
        self.assertFalse(info['ricochet'])
        self.assertTrue(info['hit_body'])
    def test_modern_he_screen_multiplier(self):
        info=self.analyze([layer(20,0),layer(100,1.02,True)],shell('HIGH_EXPLOSIVE'),modern_he=True,shield_factor=3)
        self.assertEqual(info['required'],160)
    def test_he_that_cannot_pass_shield(self):
        info=self.analyze([layer(20,0),layer(100,.02,True)],shell('HIGH_EXPLOSIVE',shield=False),modern_he=True)
        self.assertTrue(info['blocked'])
        self.assertEqual(info['probability'],0)
        self.assertIn('NO PEN',mod.format_info(info))
    def test_unknown_material_is_not_faked(self):
        hit=layer(0,0);hit.matInfo.armor=None
        info=self.analyze([hit])
        self.assertFalse(info['known'])
        self.assertTrue(mod.format_info(info).endswith('?'))
    def test_empty_collisions(self): self.assertIsNone(self.analyze([]))
    def test_rng_bounds_and_nonstandard_shell(self):
        self.assertEqual(mod.penetration_probability(300,225,.25),100)
        self.assertEqual(mod.penetration_probability(300,375,.25),0)
        self.assertEqual(mod.penetration_probability(300,300,0),50)
        self.assertEqual(mod.penetration_probability(0,100,.25),0)
        self.assertAlmostEqual(mod.penetration_probability(300,300,.1),50)
        self.assertGreater(mod.penetration_probability(300,331,.1),0)

    def test_reference_bytecode_armor_accumulation_matches_overlay(self):
        scenarios=[([layer(100,0,True)],shell('ARMOR_PIERCING'),False),
            ([layer(20,0),layer(180,1.02,True)],shell(),False),
            ([layer(20,0),layer(20,.42,kind=2),layer(100,.84,True)],shell(),False),
            ([layer(20,0,component=0,once=True),layer(20,.52,component=0,once=True),layer(100,1.02,True)],shell(),False),
            ([layer(20,0),layer(100,3.02,True)],shell(),False),
            ([layer(20,0,component=0)],shell('ARMOR_PIERCING'),False),
            ([layer(20,0),layer(100,.02,True)],shell('HIGH_EXPLOSIVE'),True),
            ([layer(400,0),layer(100,.02,True)],shell('HIGH_EXPLOSIVE'),True),
            ([layer(20,0),layer(100,.02,True)],shell('HIGH_EXPLOSIVE',shield=False),True)]
        for details,loaded,modern in scenarios:
            reference=self.reference_overlay(details,loaded,modern)
            info=self.analyze(details,loaded,modern_he=modern,shield_factor=3)
            self.assertAlmostEqual(info['required'],reference[1])
            self.assertEqual(info['ricochet'],reference[2])
            self.assertEqual(info['hit_body'],reference[3])

    def test_reference_gaussian_bytecode_matches_probability(self):
        import marshal,__builtin__
        code=marshal.loads(open(os.path.join(ROOT,'reference_2_2_0/ap_math.pyc'),'rb').read()[8:])
        function=next(c for c in code.co_consts if isinstance(c,types.CodeType) and c.co_name=='gaussian_probability')
        original=types.FunctionType(function,dict(__builtins__=__builtin__.__dict__,
                                    math=math,_SIX_SQRT_2=6*math.sqrt(2)))
        for average in (100,250,300,420):
            for ratio in (.5,.75,.8,.9,1,1.1,1.2,1.25,1.5):
                self.assertAlmostEqual(mod.penetration_probability(average,average*ratio,.1),
                                       original(average,average*ratio))
    def test_near_zero_does_not_say_impossible(self):
        info=self.analyze([layer(374,0,True)])
        self.assertGreater(info['probability'],0)
        self.assertNotIn('NO PEN',mod.format_info(info))

    def test_compact_probability_and_spaced_format(self):
        info=self.analyze([layer(10,0),layer(100,.11,True)])
        info['probability']=72.3
        self.assertEqual(mod.format_info(info),'SPACED')
        info['spaced']=False
        self.assertEqual(mod.format_info(info),'')

    def test_hesh_modern_he_direct_armor_and_rng(self):
        # HESH uses the client's HIGH_EXPLOSIVE kind and actual penetration RNG,
        # not a separate HESH physics branch or the HEAT air-gap model.
        hesh=shell('HIGH_EXPLOSIVE',spread=.1)
        info=self.analyze([layer(300,0,True)],hesh,modern_he=True)
        self.assertEqual(info['required'],300)
        self.assertAlmostEqual(info['probability'],50)
        self.assertFalse(info['ricochet'])

    def test_hesh_spaced_armor_uses_he_shield_factor_without_heat_loss(self):
        hesh=shell('HIGH_EXPLOSIVE')
        info=self.analyze([layer(20,0),layer(100,3.02,True)],hesh,
                          modern_he=True,shield_factor=3)
        self.assertEqual(info['required'],160)
        self.assertTrue(info['spaced'])
        self.assertEqual(info['probability'],100)

    def test_hesh_shield_blocked_is_full_penetration_only(self):
        info=self.analyze([layer(20,0),layer(100,.02,True)],
                          shell('HIGH_EXPLOSIVE',shield=False),modern_he=True)
        self.assertTrue(info['blocked'])
        self.assertEqual(mod.format_info(info),'NO PEN')

class FakeLabel(object):
    def __init__(self):
        self.visible=False;self.last_state=None;self.settings=Obj(ENABLED=True)
    def hide(self):self.visible=False
    def update_gui(self,value,color):self.visible=True;self.value=value;self.color=color
class FakeState(object):
    def __init__(self):
        self.enabled=True;self.prob_label=FakeLabel();self.armor_label=FakeLabel();self.angle_label=FakeLabel()
        self.track_indicator=Obj(show=lambda:None,hide=lambda:None)
    def update_gui(self,*args):self.args=args
    def hide_labels(self):self.prob_label.hide();self.armor_label.hide()
    def hide_all(self):self.hide_labels();self.angle_label.hide();self.track_indicator.hide()
    def create_window(self):self.enabled=True
    def destroy_window(self):self.hide_all();self.enabled=False

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.saved=dict(sys.modules);self.state=FakeState();self.params={};self.logs=[]
        self.global_settings=Obj(MOD_ENABLED=True)
        self.angle_settings=Obj(ENABLED=True)
        def original(cls,*args):return 'UNCHANGED_GAME_RESULT'
        class Client(Engine):pass
        Client._CrosshairShotResults__shotResultDefault=classmethod(original)
        Client._CrosshairShotResults__shotResultModernHE=classmethod(original)
        self.client=Client
        modules={
          'AvatarInputHandler':dict(gun_marker_ctrl=Obj(_CrosshairShotResults=Client)),
          'items.components.component_constants':dict(MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS=3),
          'armorshotanalyzer.gui.armorshotanalyzer_gui':dict(gui_state=self.state),
          'armorshotanalyzer.gui.armorshotanalyzer_gameface_api':dict(ap_window=Obj(update_params=lambda p:self.params.update(p))),
          'armorshotanalyzer.gui.armorshotanalyzer_constants':dict(GlobalSettings=self.global_settings,AngleLabelSettings=self.angle_settings,Colors=Obj(GREY='D0D0D0',LOW_CHANCE='FF4040',MEDIUM_CHANCE='FFC04D'),TrackIndicatorSettings=Obj(ENABLED=True),get_color_from_prob=lambda p:'FF4040' if p==0 else '9CFF3A',get_ricochet_color=lambda:'FF4040'),
          'armorshotanalyzer.debug':dict(log=self.logs.append)}
        for name, attrs in modules.items():
            parts=name.split('.')
            for i in range(1,len(parts)):
                parent='.'.join(parts[:i])
                if parent not in sys.modules:
                    package=types.ModuleType(parent);package.__path__=[]
                    sys.modules[parent]=package
            module=types.ModuleType(name);module.__dict__.update(attrs);sys.modules[name]=module
        mod.uninstall();mod._INSTALLED=False;mod._ERROR_REPORTED=False;mod.install()
    def tearDown(self):
        if hasattr(self,'lifecycle_module'):
            self.lifecycle_module.uninstall()
        for name in list(sys.modules):
            if name not in self.saved:del sys.modules[name]
        sys.modules.update(self.saved)
        mod.uninstall();mod._INSTALLED=False
    def call(self,details,loaded=None,method='_CrosshairShotResults__shotResultDefault'):
        return getattr(self.client,method)(None,details,300,loaded or shell(),75,125,Obj())
    def test_loaded_ammo_changes_label_and_preserves_result(self):
        self.assertEqual(self.call([layer(300,0,True)]),'UNCHANGED_GAME_RESULT')
        self.assertEqual('',self.params['probText'])
        self.call([layer(300,0,True)],shell('ARMOR_PIERCING',spread=0))
        self.assertEqual('',self.params['probText'])
        self.assertFalse(self.params['probVisible'])
        self.call([layer(10,0),layer(100,.01,True)],shell('ARMOR_PIERCING'))
        self.assertEqual(self.params['probText'],'')
        self.assertFalse(self.state.prob_label.visible)
        self.state.hide_labels();self.assertFalse(self.state.prob_label.visible)
    def test_heat_screen_updates_effective_armor_and_color(self):
        self.call([layer(20,0),layer(180,1.02,True)])
        self.assertEqual(self.state.args[0],340)
        self.assertEqual(self.params['probColor'],'9CFF3A')
        self.assertEqual(self.params['probText'],'')
    def test_ricochet_remains_red(self):
        self.call([layer(100,0,True,cosine=.01)])
        self.assertEqual(self.params['probColor'],'FF4040')

    def test_all_status_rows_stay_hidden_and_angle_remains_visible(self):
        for details in ([layer(20,0),layer(100,.02,True)],
                        [layer(400,0,True)], [layer(20,0,component=0)],
                        [layer(100,0,True,cosine=.01)]):
            self.state.prob_label.settings.ENABLED=True
            self.call(details)
            self.assertEqual(self.params['probText'],'')
            self.assertFalse(self.params['probVisible'])
            self.assertFalse(self.state.prob_label.visible)
            self.assertFalse(self.state.prob_label.settings.ENABLED)
        self.assertTrue(self.params['angleVisible'])
        self.assertEqual(self.params['angleColor'],'FFFFFF')

    def test_hidden_status_color_still_applies_to_armor(self):
        track=layer(20,0,component=0);track.matInfo.extra=True
        self.call([track,layer(400,.02,True)])
        self.assertEqual(self.state.armor_label.color,'FFC04D')
        self.assertFalse(self.params['probVisible'])

    def test_no_hull_module_shows_orange_dash_without_angle_or_status(self):
        track=layer(20,0,component=0);track.matInfo.extra=True
        self.assertEqual(self.call([track]),'UNCHANGED_GAME_RESULT')
        self.assertTrue(self.state.armor_label.visible)
        self.assertEqual(self.state.armor_label.value,'-')
        self.assertEqual(self.state.armor_label.color,'FFC04D')
        self.assertFalse(self.params['angleVisible'])
        self.assertFalse(self.params['probVisible'])
        self.assertEqual(self.params['probText'],'')
    def test_install_is_idempotent(self):
        before=getattr(self.client,'_CrosshairShotResults__shotResultDefault').__func__
        mod.install()
        self.assertIs(before,getattr(self.client,'_CrosshairShotResults__shotResultDefault').__func__)
    def test_disabled_mod_hides_extra_row(self):
        self.state.prob_label.visible=True;self.global_settings.MOD_ENABLED=False
        self.call([layer(300,0,True)])
        self.assertFalse(self.state.prob_label.visible)
    def test_unsupported_client_data_fails_without_changing_result(self):
        self.assertEqual(self.call([layer(300,0,True)],shell('UNKNOWN_KIND')),'UNCHANGED_GAME_RESULT')
        self.assertFalse(self.state.prob_label.visible)
        self.assertEqual(len(self.logs),1)
        self.call([layer(300,0,True)],shell('UNKNOWN_KIND'))
        self.assertEqual(len(self.logs),1)
    @unittest.skipUnless(sys.version_info[:2] == (2,7), 'Python 2.7 game loader')
    def test_compiled_entrypoint_installs_once(self):
        core=types.ModuleType('armorshotanalyzer.core');core.__path__=[]
        core.armorshotanalyzer_shell_info=mod;sys.modules['armorshotanalyzer.core']=core
        core.armorshotanalyzer_hooks=Obj(install=lambda:None,uninstall=lambda:None)
        before=getattr(self.client,'_CrosshairShotResults__shotResultDefault').__func__
        imp.load_compiled('entrypoint_test',os.path.join(os.path.dirname(ROOT),
            'scripts/client/gui/mods/mod_armorshotanalyzer.pyc'))
        self.assertIs(before,getattr(self.client,'_CrosshairShotResults__shotResultDefault').__func__)
    def test_modern_he_wrapper(self):
        self.call([layer(20,0),layer(100,.02,True)],shell('HIGH_EXPLOSIVE'),
                  '_CrosshairShotResults__shotResultModernHE')
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.state.args[0],160)

    def test_angle_is_white_and_visible_after_settings_refresh(self):
        self.assertTrue(self.angle_settings.ENABLED)
        self.angle_settings.ENABLED=False
        self.state.angle_label.visible=True
        self.call([layer(100,0,True,cosine=0)])
        self.assertTrue(self.angle_settings.ENABLED)
        self.assertTrue(self.state.angle_label.visible)
        self.assertTrue(self.params['angleVisible'])
        self.assertEqual(self.params['angleText'],'90\xc2\xb0')
        self.assertEqual(self.params['angleColor'],'FFFFFF')

    def test_unknown_or_track_only_has_no_fake_angle(self):
        self.call([layer(20,0,component=0)])
        self.assertFalse(self.params['angleVisible'])
        detail=layer(20,0);detail.matInfo.armor=None
        self.call([detail])
        self.assertFalse(self.params['angleVisible'])

    def test_normal_impact_zero_degrees_is_valid(self):
        self.call([layer(100,0,True)])
        self.assertTrue(self.params['angleVisible'])
        self.assertEqual(self.params['angleText'],'0\xc2\xb0')

    def test_angle_uses_collision_even_without_armor_angle_multiplier(self):
        detail=layer(100,0,True,cosine=0)
        detail.matInfo.useHitAngle=False
        self.call([detail])
        self.assertEqual(self.params['angleText'],'90\xc2\xb0')

    def test_single_status_prioritizes_no_hull_over_spaced(self):
        self.call([layer(20,0,component=0)])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'FF4040')

    def test_nonpenetrating_heat_is_red(self):
        self.call([layer(20,0),layer(240,1.02,True)])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'FF4040')

    def test_he_zero_penetration_has_unknown_damage(self):
        self.call([layer(20,0),layer(100,.02,True)],
                  shell('HIGH_EXPLOSIVE',shield=False),
                  '_CrosshairShotResults__shotResultModernHE')
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'D0D0D0')
        info=mod.analyze_shot(Engine,[layer(400,0,True)],300,
                              shell('HIGH_EXPLOSIVE'),Obj(),modern_he=True)
        self.assertFalse(mod.no_direct_hp_damage(info))

    def test_unknown_data_stays_grey(self):
        detail=layer(0,0);detail.matInfo.armor=None
        self.call([detail])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'D0D0D0')

    def test_penetrable_spaced_armor_uses_original_gradient(self):
        calls=[]
        constants=sys.modules['armorshotanalyzer.gui.armorshotanalyzer_constants']
        constants.get_color_from_prob=lambda p:(calls.append(p) or 'ABC123')
        mod.uninstall();mod._INSTALLED=False
        mod.install()
        self.call([layer(20,0),layer(260,.02,True)])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'ABC123')
        self.assertTrue(any(0 < p < 100 for p in calls))

    def test_bright_palette_uses_real_base_gradient(self):
        gui_path=os.path.join(os.path.dirname(ROOT),'scripts/client/armorshotanalyzer/gui')
        imp.load_compiled('armorshotanalyzer.gui.armorshotanalyzer_config',
                          os.path.join(gui_path,'armorshotanalyzer_config.pyc'))
        constants=imp.load_compiled('armorshotanalyzer.gui.armorshotanalyzer_constants',
                          os.path.join(gui_path,'armorshotanalyzer_constants.pyc'))
        mod.uninstall();mod._INSTALLED=False
        mod.install()
        for key,value in mod.DISPLAY_PALETTE.items():
            self.assertEqual(getattr(constants.Colors,key),value)
        self.assertTrue(constants.Colors.GRADIENT)
        self.assertEqual(constants.get_color_from_prob(0),'FF4040')
        self.assertEqual(constants.get_color_from_prob(50),'FFC04D')
        self.assertEqual(constants.get_color_from_prob(100),'9CFF3A')
        self.assertNotIn(constants.get_color_from_prob(72.3),mod.DISPLAY_PALETTE.values())

    def test_penetrable_track_module_without_hull_is_orange(self):
        track=layer(20,0,component=0)
        track.matInfo.extra=True
        self.call([track])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'FFC04D')

    def test_unreachable_module_is_not_marked_damage_possible(self):
        track=layer(400,0,component=0)
        track.matInfo.extra=True
        self.call([track])
        self.assertEqual(self.params['probColor'],'FF4040')

    def test_module_before_impenetrable_hull_is_orange(self):
        track=layer(20,0,component=0)
        track.matInfo.extra=True
        self.call([track,layer(400,.02,True)])
        self.assertEqual(self.params['probText'],'')
        self.assertEqual(self.params['probColor'],'FFC04D')

    def test_hesh_uses_modern_he_wrapper_and_preserves_result(self):
        result=self.call([layer(20,0),layer(100,3.02,True)],
                         shell('HIGH_EXPLOSIVE'),
                         '_CrosshairShotResults__shotResultModernHE')
        self.assertEqual(result,'UNCHANGED_GAME_RESULT')
        self.assertEqual(self.state.args[0],160)
        self.assertEqual(self.params['probText'],'')

    def replace_client_method(self, function):
        mod.uninstall()
        self.client._CrosshairShotResults__shotResultDefault=classmethod(function)
        mod.install()

    def test_original_receives_identical_objects_and_result(self):
        result=object();seen=[]
        def original(owner,*args):seen.append(args);return result
        self.replace_client_method(original)
        details=[layer(100,0,True)];loaded=shell()
        actual=self.call(details,loaded)
        self.assertIs(actual,result)
        self.assertIs(seen[0][1],details)
        self.assertIs(seen[0][3],loaded)

    def test_iterator_is_not_consumed_before_client(self):
        observed=[];result=object()
        def original(owner,marker,details,*args):
            observed.extend(details);return result
        self.replace_client_method(original)
        hit=layer(100,0,True)
        self.assertIs(self.call(iter([hit])),result)
        self.assertEqual(observed,[hit])
        self.assertFalse(self.state.prob_label.visible)

    def test_original_exception_propagates_unchanged(self):
        error=RuntimeError('client error')
        def original(owner,*args):raise error
        self.replace_client_method(original)
        try:self.call([layer(100,0,True)])
        except RuntimeError as caught:self.assertIs(caught,error)
        else:self.fail('Client error was swallowed')

    def test_overlay_and_error_cleanup_failures_cannot_change_result(self):
        def broken(*args):raise RuntimeError('GUI unavailable')
        self.state.update_gui=broken;self.state.hide_all=broken
        self.assertEqual(self.call([layer(100,0,True)]),'UNCHANGED_GAME_RESULT')

    def test_uninstall_restores_descriptors_and_allows_reinstall(self):
        mod.uninstall()
        before=dict(self.client.__dict__)
        mod.install();mod.install();mod.uninstall();mod.uninstall()
        for name in ('_CrosshairShotResults__shotResultDefault',
                     '_CrosshairShotResults__shotResultModernHE'):
            self.assertIs(self.client.__dict__[name],before[name])
        mod.install()
        self.assertEqual(self.call([layer(100,0,True)]),'UNCHANGED_GAME_RESULT')

    def lifecycle_fixture(self):
        class Event(object):
            def __init__(self):self.callbacks=[]
            def __iadd__(self,callback):self.callbacks.append(callback);return self
            def __isub__(self,callback):self.callbacks.remove(callback);return self
        events=Obj(onAvatarReady=Event(),onAvatarBecomeNonPlayer=Event())
        class Input(object):
            def activatePostmortem(self,*args,**kwargs):return 'POST_RESULT'
        avatar=sys.modules['AvatarInputHandler'];avatar.AvatarInputHandler=Input
        self.client.getShotResult=classmethod(lambda owner,*a,**k:'SHOT_RESULT')
        player=types.ModuleType('PlayerEvents');player.g_playerEvents=events
        sys.modules['PlayerEvents']=player
        constants=types.ModuleType('aih_constants');constants.SHOT_RESULT=Obj(UNDEFINED='NONE')
        sys.modules['aih_constants']=constants
        base=os.path.dirname(ROOT)
        if os.environ.get('AP_TEST_BYTECODE'):
            lifecycle=imp.load_compiled('lifecycle_test',os.path.join(base,
                'scripts/client/armorshotanalyzer/core/armorshotanalyzer_hooks.pyc'))
        else:
            lifecycle=imp.load_source('lifecycle_test',os.path.join(ROOT,
                'source/armorshotanalyzer_hooks.py'))
        self.lifecycle_module=lifecycle
        return lifecycle,Input,events

    def test_lifecycle_cleanup_removes_events_and_restores_methods(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        shot=self.client.__dict__['getShotResult'];post=Input.__dict__['activatePostmortem']
        lifecycle.install();lifecycle.install()
        self.assertEqual(len(events.onAvatarReady.callbacks),1)
        self.assertEqual(len(events.onAvatarBecomeNonPlayer.callbacks),1)
        events.onAvatarReady.callbacks[0]()
        self.assertTrue(self.state.enabled)
        self.assertEqual(self.client.getShotResult(None),'SHOT_RESULT')
        self.assertEqual(Input().activatePostmortem(),'POST_RESULT')
        lifecycle.uninstall();lifecycle.uninstall()
        self.assertFalse(self.state.enabled)
        self.assertEqual(events.onAvatarReady.callbacks,[])
        self.assertEqual(events.onAvatarBecomeNonPlayer.callbacks,[])
        self.assertIs(self.client.__dict__['getShotResult'],shot)
        self.assertIs(Input.__dict__['activatePostmortem'],post)
        lifecycle.install()
        self.assertEqual(len(events.onAvatarReady.callbacks),1)

    def test_unload_does_not_overwrite_later_mod_hook(self):
        lifecycle,Input,events=self.lifecycle_fixture();lifecycle.install()
        later=classmethod(lambda owner,*a:'LATER_MOD')
        self.client.getShotResult=later
        lifecycle.uninstall()
        self.assertIs(self.client.__dict__['getShotResult'],later)

    def test_loader_fini_restores_all_hooks_and_events(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        mod.uninstall()
        before=dict(self.client.__dict__)
        core=types.ModuleType('armorshotanalyzer.core');core.__path__=[]
        core.armorshotanalyzer_shell_info=mod;core.armorshotanalyzer_hooks=lifecycle
        sys.modules['armorshotanalyzer.core']=core
        entry=imp.load_compiled('review_entry_test',os.path.join(os.path.dirname(ROOT),
            'scripts/client/gui/mods/mod_armorshotanalyzer.pyc'))
        entry.init()
        self.assertEqual(len(events.onAvatarReady.callbacks),1)
        entry.fini();entry.fini()
        self.assertEqual(events.onAvatarReady.callbacks,[])
        self.assertEqual(events.onAvatarBecomeNonPlayer.callbacks,[])
        for name in ('getShotResult','_CrosshairShotResults__shotResultDefault',
                     '_CrosshairShotResults__shotResultModernHE'):
            self.assertIs(self.client.__dict__[name],before[name])

    def test_partial_lifecycle_install_rolls_back(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        before=self.client.__dict__['getShotResult']
        class BrokenEvent(object):
            def __iadd__(self,callback):raise RuntimeError('subscription failed')
            def __isub__(self,callback):return self
        events.onAvatarBecomeNonPlayer=BrokenEvent()
        self.assertRaises(RuntimeError,lifecycle.install)
        self.assertFalse(lifecycle._INSTALLED)
        self.assertEqual(events.onAvatarReady.callbacks,[])
        self.assertIs(self.client.__dict__['getShotResult'],before)

    def test_failed_event_unsubscribe_is_inert_and_retryable(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        class RetryEvent(object):
            def __init__(self):self.callbacks=[];self.fail=True
            def __iadd__(self,callback):self.callbacks.append(callback);return self
            def __isub__(self,callback):
                if self.fail:raise RuntimeError('host event temporarily unavailable')
                self.callbacks.remove(callback);return self
        events.onAvatarReady=RetryEvent()
        lifecycle.install()
        old=events.onAvatarReady.callbacks[0]
        lifecycle.uninstall()
        self.assertTrue(lifecycle._EVENTS)
        old();self.assertFalse(self.state.enabled)
        lifecycle.install()
        self.state.enabled=False
        old();self.assertFalse(self.state.enabled)
        events.onAvatarReady.fail=False
        lifecycle.uninstall()
        self.assertEqual(events.onAvatarReady.callbacks,[])
        self.assertEqual(lifecycle._EVENTS,[])

    def test_window_closes_even_when_hide_or_destroy_fails(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        closed=[]
        window=sys.modules['armorshotanalyzer.gui.armorshotanalyzer_gameface_api'].ap_window
        window.close_window=lambda:closed.append(True)
        def broken():raise RuntimeError('label teardown failed')
        self.state.destroy_window=broken
        lifecycle.install();lifecycle.uninstall()
        self.assertFalse(self.state.enabled)
        self.assertTrue(closed)
        self.assertEqual(events.onAvatarReady.callbacks,[])

    def test_inherited_client_descriptors_restored_without_local_override(self):
        mod.uninstall()
        class Derived(self.client):pass
        sys.modules['AvatarInputHandler'].gun_marker_ctrl._CrosshairShotResults=Derived
        name='_CrosshairShotResults__shotResultDefault'
        original=getattr(Derived,name).__func__
        self.assertNotIn(name,Derived.__dict__)
        mod.install();mod.uninstall()
        self.assertNotIn(name,Derived.__dict__)
        self.assertIs(getattr(Derived,name).__func__,original)

    def test_lifecycle_preserves_original_exceptions(self):
        lifecycle,Input,events=self.lifecycle_fixture()
        error=RuntimeError('stock failure')
        def broken(*args,**kwargs):raise error
        self.client.getShotResult=classmethod(broken)
        Input.activatePostmortem=broken
        lifecycle.install()
        for action in (lambda:self.client.getShotResult(None),lambda:Input().activatePostmortem()):
            try:action()
            except RuntimeError as caught:self.assertIs(caught,error)
            else:self.fail('Stock exception changed')

    def test_retained_old_wrapper_is_inert_after_unload_and_reload(self):
        old=getattr(self.client,'_CrosshairShotResults__shotResultDefault').__func__
        mod.uninstall();mod.install()
        self.params.clear()
        result=old(self.client,None,[layer(100,0,True)],300,shell(),75,125,Obj())
        self.assertEqual(result,'UNCHANGED_GAME_RESULT')
        self.assertEqual(self.params,{})

    def test_current_client_default_and_he_methods_return_exact_results(self):
        import marshal,zipfile,__builtin__
        path=r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia\res\packages\scripts.pkg'
        with zipfile.ZipFile(path) as archive:
            top=marshal.loads(archive.read('scripts/client/AvatarInputHandler/gun_marker_ctrl.pyc')[8:])
        cls_code=next(c for c in top.co_consts if isinstance(c,types.CodeType)
                      and c.co_name=='_CrosshairShotResults')
        enum=Obj(NOT_PIERCED=1,LITTLE_PIERCED=2,GREAT_PIERCED=3,UNDEFINED=0)
        namespace=dict(__builtins__=__builtin__.__dict__,_SHOT_RESULT=enum,round_py2_style=round,
            MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS=3,
            MODERN_HE_DAMAGE_ABSORPTION_FACTOR=2,_logger=Obj(error=lambda *a:None))
        mod.uninstall()
        methods={}
        for name in ('__shotResultDefault','__shotResultModernHE'):
            code=next(c for c in cls_code.co_consts if isinstance(c,types.CodeType) and c.co_name==name)
            function=types.FunctionType(code,namespace)
            methods[name]=function
            setattr(self.client,'_CrosshairShotResults'+name,classmethod(function))
        self.client._CRIT_ONLY_SHOT_RESULT=enum.NOT_PIERCED
        trace=[]
        self.client._CrosshairShotResults__collectDebugPiercingData=staticmethod(
            lambda *args:trace.append(('collect',args)))
        self.client._CrosshairShotResults__sendDebugInfo=staticmethod(
            lambda *args:trace.append(('send',args)))
        cases=[('__shotResultDefault',[layer(400,0),layer(1,.01,True)],shell('ARMOR_PIERCING')),
               ('__shotResultDefault',[layer(100,0,True)],shell('ARMOR_PIERCING')),
               ('__shotResultModernHE',[layer(20,0),layer(1,.02,True)],shell('HIGH_EXPLOSIVE')),
               ('__shotResultModernHE',[layer(100,0,True)],shell('HIGH_EXPLOSIVE'))]
        for _,_,loaded in cases:loaded.type.maxDamage=30
        expected=[];expected_traces=[]
        for name,details,loaded in cases:
            del trace[:]
            expected.append(methods[name](self.client,None,details,300,loaded,75,125,Obj()))
            expected_traces.append(list(trace))
        # Nonzero absorption blocks the screen+HE case in this injected client
        # environment. The overlay must not replace that client's decision.
        self.assertEqual(expected[2],enum.NOT_PIERCED)
        self.assertEqual(expected[0],enum.NOT_PIERCED)
        mod.install()
        for (name,details,loaded),result,expected_trace in zip(cases,expected,expected_traces):
            del trace[:]
            actual=getattr(self.client,'_CrosshairShotResults'+name)(
                None,details,300,loaded,75,125,Obj())
            self.assertEqual(actual,result)
            self.assertEqual(trace,expected_trace)
        mod.uninstall()
        for name,function in methods.items():
            self.assertIs(getattr(self.client,'_CrosshairShotResults'+name).__func__,function)

if __name__=='__main__':unittest.main()
