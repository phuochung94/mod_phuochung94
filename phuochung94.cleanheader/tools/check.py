"""Check the header resource patch and render its isolated native components."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

from build import ROOT, GAME, PACKAGE_NAME, MOD_VERSION, ONLINE_RESOURCE, loader
from cleanheader import RESOURCE, transform, PLUS_START, PLUS_END, SHOP_NODE, PROFILE_TAIL, ONLINE_COMPONENT, parse_online_sprites, online_component

NODE = Path(r'C:\Users\phuochung94\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')


class Header(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(GAME / 'res/packages/gui-part1.pkg') as archive:
            cls.original = archive.read(RESOURCE).decode('utf-8')
        with zipfile.ZipFile(GAME / 'res/packages/gui-part3.pkg') as archive:
            cls.footer = archive.read('gui/gameface/_dist/production/mono/hangar/footer/bundle.js').decode('utf-8')
        cls.sprites = parse_online_sprites(cls.footer)
        cls.component = online_component(cls.sprites)
        cls.patched = (ROOT / 'res' / RESOURCE).read_text(encoding='utf-8')
    def test_build_matches_transform(self):
        self.assertEqual(self.patched, transform(self.original, self.sprites))
    def test_plus_and_internal_separator_removed_from_render_tree(self):
        self.assertNotIn('"data-test-id":"wotPlus"', self.patched)
        self.assertNotIn(PLUS_END, self.patched)
        self.assertEqual(self.patched.count('"data-test-id":"premium"'), 1)
    def test_premium_subtree_is_byte_for_byte_unchanged(self):
        marker = '(0,Ve.jsxs)("div",{...a,className:Yt,"data-test-id":"premium"'
        def premium(text):
            start = text.index(marker)
            return text[start:text.index(',va=(0,Se.memo)', start)]
        self.assertEqual(premium(self.original), premium(self.patched))
    def test_user_name_and_vip_keep_original_order_without_shop_child(self):
        expected = 'children:[t&&(0,Ve.jsx)(qt,{options:{rootId:ya}}),t&&(0,Ve.jsx)(va,{options:{rootId:ya}}),t&&(0,Ve.jsx)(ChOnlineWidget,{})]'
        self.assertIn(expected, self.patched)
        self.assertNotIn(SHOP_NODE, self.patched)
    def test_only_requested_sections_are_changed(self):
        start = self.original.index(PLUS_START)
        end = self.original.index(PLUS_END, start) + len(PLUS_END)
        expected = (self.original[:start] + 'children:[' + self.original[end:]).replace(SHOP_NODE, '', 1)
        expected = expected.replace(PROFILE_TAIL, PROFILE_TAIL[:-1] + ',t&&(0,Ve.jsx)(ChOnlineWidget,{})]', 1)
        expected = expected.replace('function Na({className:e})', self.component + 'function Na({className:e})', 1)
        expected = expected.replace('}from"../chunks/lib.js";', ',ir as ChSprite}from"../chunks/lib.js";', 1)
        self.assertEqual(self.patched, expected)
    def test_unknown_client_component_markers_are_rejected(self):
        for marker in (PLUS_START, PLUS_END, SHOP_NODE):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                transform(self.original.replace(marker, '', 1), self.sprites)
        with self.assertRaises(ValueError): transform(self.original + SHOP_NODE, self.sprites)
        with self.assertRaises(ValueError): transform(self.original.replace('function Na({className:e})', 'function UnknownProfile({className:e})'), self.sprites)
    def test_wotmod_contains_only_header_resource_and_metadata(self):
        with zipfile.ZipFile(ROOT / 'dist' / PACKAGE_NAME) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {'res/' + RESOURCE, 'res/' + ONLINE_RESOURCE, 'meta.xml'})
            self.assertEqual(archive.read('res/' + RESOURCE).decode('utf-8'), self.patched)
            self.assertTrue(all(entry.compress_type == zipfile.ZIP_STORED for entry in archive.infolist()))
            metadata = ET.fromstring(archive.read('meta.xml'))
            self.assertEqual(metadata.findtext('version'), MOD_VERSION)
            self.assertEqual(metadata.findtext('id'), 'phuochung94.cleanheader')
            self.assertEqual(metadata.findtext('name'), 'Clean Garage Header')
    def test_no_show_tank_or_vehicle_control_resources_in_active_project(self):
        resources = {p.relative_to(ROOT / 'res').as_posix() for p in (ROOT / 'res').rglob('*') if p.is_file()}
        self.assertEqual(resources, {RESOURCE, ONLINE_RESOURCE})
        self.assertFalse((ROOT / 'src/mod_showtank.py').exists())
        self.assertFalse((ROOT / 'tools/client_catalog.py').exists())
        bridge = (ROOT / 'src/mod_cleanheader.py').read_text()
        for token in ('HeroTank', 'HangarVehicle', 'KEY_', 'VehicleDescr', 'turretRotator'):
            self.assertNotIn(token, bridge)
        self.assertEqual((ROOT / 'res' / ONLINE_RESOURCE).read_bytes(), loader((ROOT / 'src/mod_cleanheader.py').read_bytes()))
    def test_manifest_checksums_and_native_styles(self):
        manifest = json.loads((ROOT / 'dist/cleanheader.json').read_text())
        self.assertEqual(hashlib.sha256(self.original.encode()).hexdigest(), manifest['source_sha256'])
        self.assertEqual(hashlib.sha256(self.patched.encode()).hexdigest(), manifest['patched_sha256'])
        self.assertFalse(manifest['native_css_modified'])
        self.assertFalse(manifest['show_tank_enabled'])
        self.assertFalse(any((ROOT / 'res').rglob('*.css')))
    def test_native_contacts_icon_assets_exist_with_correct_frames(self):
        import struct
        for sprite in self.sprites.values():
            asset = 'gui/maps/icons/' + sprite['path'].replace('.', '/') + '.png'
            found = False
            for package in (GAME / 'res/packages').glob('gui*.pkg'):
                with zipfile.ZipFile(package) as archive:
                    if asset not in archive.namelist(): continue
                    data = archive.read(asset)
                    width, height = struct.unpack('>II', data[16:24])
                    self.assertEqual(sprite['config']['meta']['size'], dict(w=width, h=height))
                    frame = sprite['config']['frames']['contacts']
                    self.assertLessEqual(frame['x'] + frame['w'], width)
                    self.assertLessEqual(frame['y'] + frame['h'], height)
                    found = True
                    break
            self.assertTrue(found, asset)
    def test_changed_native_sprite_mapping_is_rejected(self):
        with self.assertRaises(ValueError): parse_online_sprites(self.footer.replace('contacts:{', 'missingContacts:{'))
    def test_javascript_syntax(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'header.mjs'
            source.write_text(self.patched, encoding='utf-8')
            result = subprocess.run([str(NODE), '--check', str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
    def test_isolated_native_components_render_vip_only_with_working_click(self):
        start = self.patched.index('var pa=I(function({className:e})')
        premium = self.patched[start:self.patched.index(',va=(0,Se.memo)', start)] + ';'
        start = self.patched.index('function Na({className:e})')
        profile = self.patched[start:self.patched.index('var Ba=', start)]
        script = r'''
const vm = require('node:vm');
const assert = require('node:assert/strict');
let opens=0, plusOpens=0, active=true, online='ASIA1  12,345', iconSize='small';
const tooltip=()=>({onClick(){},onMouseEnter(){}});
const ctx={ChSprite:'native-sprite',E:value=>value,j:()=>({value:iconSize}),$:()=>{},Math, R:{invalid:()=>0}, I:fn=>fn, T:(...parts)=>parts.filter(Boolean).join(' '),
  Ve:{jsx:(type,props)=>({type,props}),jsxs:(type,props)=>({type,props})},
  Se:{useRef:()=>({current:false}),useMemo:fn=>fn()},
  ie:()=>({play(){}}),r:tooltip,i:tooltip,_:tooltip,
  ma:{read:()=>1},ba:{read:()=>1},_a:{readOrEmpty:key=>key},
  ue:{Active:'Active',Cancelled:'Cancelled'},de:{Pro:'Pro'},da:{Active:'Active',Inactive:'Inactive'},
  O:()=>select=>{const model=select({observableModel:{primitives:()=>({cleanheaderOnline:{get:()=>online}})}});return ['online-provider',()=>({model})];},
  Qt:'native-premiums',ua:'native-premiums',Yt:'native-subscription',Kt:'disabled',Jt:'native-text',
  ra:'native-premium-icon',na:'native-premium-disabled',s:'native-time',
  fa:'native-profile',ga:'native-gap',le:'native-divider',qt:'user-name',va:'premium-widget',ya:1,l:()=>true};
ctx.me=()=>({model:{wotPlus:{get:()=>({type:'Core',state:'Inactive',isWotPlusEnabled:true})},
  benefits:{get:()=>[]},proBenefits:{get:()=>[]},subscriptionPrimitives:{isCnRealm:{get:()=>false}},
  getTooltipVariant:()=>'',premiums:{basic:{get:()=>({unit:'days',value:972})}},
  premiumAccount:{get:()=>({state:active?'Active':'Inactive'})}},
  controls:{openPremiumSubscriptionPage(){opens++;},openWotPlusSubscriptionPage(){plusOpens++;}}});
vm.createContext(ctx);
vm.runInContext(PREMIUM + ONLINE + PROFILE, ctx);
function all(node){if(!node||typeof node!=='object')return [];const c=node.props?.children;
  return [node,...(Array.isArray(c)?c:[c]).flatMap(all)];}
let nodes=all(ctx.pa({className:'keep-native-spacing'}));
assert.equal(nodes.filter(n=>n.props?.['data-test-id']==='premium').length,1);
assert.equal(nodes.filter(n=>n.props?.['data-test-id']==='wotPlus').length,0);
assert.equal(nodes.find(n=>n.type==='native-time').props.params.day,972);
nodes.find(n=>n.props?.['data-test-id']==='premium').props.onClick({});
assert.equal(opens,1);assert.equal(plusOpens,0);
active=false;nodes=all(ctx.pa({}));
assert(nodes.some(n=>n.props?.className==='native-premium-icon native-premium-disabled'));
assert(nodes.some(n=>n.props?.children==='menu.common.premiumBuy'));
const row=ctx.Na({}).props.children;
assert.equal(row.type,'native-divider');assert.equal(row.props.className,'native-gap');
assert.deepEqual(Array.from(row.props.children,n=>typeof n.type==='function'?n.type.name:n.type),['user-name','premium-widget','ChOnlineWidget']);
for(const [size,side] of [['small',24],['medium',32],['upscale',64]]){
 iconSize=size;const onlineNode=ctx.ChOnline();
 const [icon,text]=onlineNode.props.children;
 assert.equal(icon.type,'native-sprite');assert.equal(icon.props.icon,'contacts');
 assert.equal(icon.props.config.frames.contacts.w,side);
 assert.equal(icon.props.config.frames.contacts.h,side);
 assert.equal(text.props.children,'ASIA1  12,345');assert(text.props.children.includes('  '));assert(!text.props.children.includes('PING'));assert.equal(text.props.className,'native-text');
 assert.equal(text.props.style.whiteSpace,'pre');assert.equal(onlineNode.props.style,undefined);
}
online='';assert.equal(ctx.ChOnline().props.children[1].props.children,'\u2014');
console.log('PASS: native VIP rendering, expiry, inactive state, click, name/VIP order and separator');
'''
        script = 'const PREMIUM=' + json.dumps(premium) + ';const ONLINE=' + json.dumps(self.component) + ';const PROFILE=' + json.dumps(profile) + ';\n' + script
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'render.cjs'
            source.write_text(script, encoding='utf-8')
            result = subprocess.run([str(NODE), str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__': unittest.main(verbosity=2)
