"""Remove only garage header promotion nodes; preserve native VIP markup/styles."""
import json
import re

RESOURCE = 'gui/gameface/_dist/production/mono/hangar/header/bundle.js'
PLUS_START = 'children:[(0,Ve.jsxs)("div",{...f?y:x'
PLUS_END = ',(0,Ve.jsx)(ce,{className:Xt}),'
SHOP_NODE = ',xa&&(0,Ve.jsx)(ca,{})'
PREMIUM_NODE = '"data-test-id":"premium"'
PROFILE_TAIL = ',t&&(0,Ve.jsx)(va,{options:{rootId:ya}})]'
ONLINE_COMPONENT = ('var ChOnlineSprites=__CLEANHEADER_NATIVE_SPRITES__;var[ChOnlineProvider,ChUseOnline]=O("CleanHeaderOnline")'
    '(({observableModel:e})=>e.primitives(["cleanheaderOnline"]),()=>({}));'
    'var ChOnline=I(function(){const{model:e}=ChUseOnline(),n=E(j({value:"small"},{medium:{value:"medium"}}).value,$);'
    'return(0,Ve.jsxs)("div",{className:Qt,"data-test-id":"cleanheader-online",'
    'children:[(0,Ve.jsx)(ChSprite,{...ChOnlineSprites[n],"data-test-id":"cleanheader-online-icon"}),'
    '(0,Ve.jsx)("div",{className:Jt,style:{whiteSpace:"pre"},children:(e.cleanheaderOnline.get()||"\u2014")})]})});'
    'function ChOnlineWidget(){return(0,Ve.jsx)(ChOnlineProvider,{options:{rootId:ya},'
    'children:(0,Ve.jsx)(ChOnline,{})})}')


def parse_online_sprites(footer_bundle):
    result = {}
    for size, variable, atlas in [('small', 'we', 'footer_small'),
                                  ('medium', 've', 'footer_large'),
                                  ('upscale', 'Ce', 'footer_upscale')]:
        pattern = (r'\b' + variable + r'=\{frames:\{(.*?)\},meta:\{size:\{h:(\d+),w:(\d+)\}\}\}')
        match = re.search(pattern, footer_bundle)
        if not match:
            raise ValueError('Native footer sprite atlas changed: ' + atlas)
        frame = re.search(r'contacts:\{h:(\d+),w:(\d+),x:(\d+),y:(\d+)\}', match[1])
        if not frame:
            raise ValueError('Native Contacts icon missing: ' + atlas)
        h, w, x, y = map(int, frame.groups())
        result[size] = {'config': {'frames': {'contacts': dict(h=h, w=w, x=x, y=y)},
            'meta': {'size': dict(h=int(match[2]), w=int(match[3]))}},
            'path': 'header_footer.' + atlas, 'icon': 'contacts'}
    return result


def online_component(sprites):
    return ONLINE_COMPONENT.replace('__CLEANHEADER_NATIVE_SPRITES__', json.dumps(sprites, separators=(',', ':')))


def transform(original, sprites):
    for marker in (PLUS_START, PLUS_END, SHOP_NODE, PREMIUM_NODE):
        if original.count(marker) != 1:
            raise ValueError('Unsupported header bundle: expected exactly one ' + marker)
    start = original.index(PLUS_START)
    end = original.index(PLUS_END, start) + len(PLUS_END)
    removed = original[start:end]
    if '"data-test-id":"wotPlus"' not in removed or PREMIUM_NODE in removed:
        raise ValueError('Unexpected subscription component boundaries')
    patched = original[:start] + 'children:[' + original[end:]
    patched = patched.replace(SHOP_NODE, '', 1)
    if patched.count(PROFILE_TAIL) != 1 or patched.count('function Na({className:e})') != 1:
        raise ValueError('Unsupported user profile layout')
    patched = patched.replace(PROFILE_TAIL, PROFILE_TAIL[:-1] + ',t&&(0,Ve.jsx)(ChOnlineWidget,{})]', 1)
    imports = '}from"../chunks/lib.js";'
    if patched.count(imports) != 1:
        raise ValueError('Unsupported native icon library import')
    patched = patched.replace(imports, ',ir as ChSprite' + imports, 1)
    return patched.replace('function Na({className:e})', online_component(sprites) + 'function Na({className:e})', 1)
