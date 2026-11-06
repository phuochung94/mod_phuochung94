"""Warm only garage atmospheric fog, preserving luminance and beam removal."""
from pathlib import Path
import importlib.util
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('garage_reference', ROOT/'tools/restore-garage-reference.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def warm(data):
    values = list(struct.unpack('<'+'f'*(len(data)//4), data))
    assert len(values) in (3, 4)
    # Match the perceived brightness; change the hue, not alpha/density.
    luminance = sum(a*b for a, b in zip(values[:3], (0.2126, 0.7152, 0.0722)))
    tint = (1.0, 0.88, 0.67)
    gain = luminance / sum(a*b for a, b in zip(tint, (0.2126, 0.7152, 0.0722)))
    values[:3] = [c*gain for c in tint]
    return struct.pack('<'+'f'*len(values), *values)


def main():
    name = 'phuochung94.audioww+maps-ASIA 2.4.1.1 #991.wotmod'
    # Use the current package as the reference for unrelated resources.
    with zipfile.ZipFile(ROOT/name) as baseline:
        changed = 0
        for file in (ROOT/'res/spaces/hangar_v4/environments').rglob('environment.xml'):
            resource = file.relative_to(ROOT).as_posix()
            header, tree = g.parse(baseline.read(resource))
            before = [(n['path'], n['kind'], n['data']) for n in g.walk(tree)]
            allowed = set()
            for n in g.walk(tree):
                if n['path'].startswith('/Fog/') and n['path'].endswith(('/color', '/scatterColor')) and n['kind'] == 3:
                    # Zero-alpha fog/scattering is left disabled.
                    if len(n['data']) == 16 and struct.unpack_from('<f', n['data'], 12)[0] == 0:
                        continue
                    n['data'] = warm(n['data'])
                    allowed.add(n['path'])
                    changed += 1
            output = header+g.encode(tree)
            _, verified = g.parse(output)
            after = [(n['path'], n['kind'], n['data']) for n in g.walk(verified)]
            assert [v for v in before if v[0] not in allowed] == [v for v in after if v[0] not in allowed]
            file.write_bytes(output)
        scene_name = 'res/spaces/hangar_v4/space.bin'
        original = baseline.read(scene_name)
    scene = bytearray(original)
    sections = {}
    for i in range(g.u32(scene, 20)):
        p = 24+24*i
        sections[scene[p:p+4].decode()] = struct.unpack_from('<QQ', scene, p+8)
    st = sections['BWST'][0]
    count = g.u32(scene, st+4)
    blob = st+12+12*count
    strings = {}
    for i in range(count):
        key, offset, size = struct.unpack_from('<III', scene, st+8+12*i)
        strings[key] = scene[blob+offset:blob+offset+size].decode()
    arrays = []
    p = sections['BSMA'][0]
    for expected in (16, 4, 12, 64, 16):
        stride, count = struct.unpack_from('<II', scene, p)
        assert stride == expected
        arrays.append((p+8, count))
        p += 8+stride*count
    offsets = set()
    for i in range(arrays[0][1]):
        shader, start, end, _ = struct.unpack_from('<IIII', scene, arrays[0][0]+16*i)
        if shader >= arrays[1][1]:
            continue
        if strings[g.u32(scene, arrays[1][0]+4*shader)] != 'shaders/custom/volumetric_effect_vtx.fx':
            continue
        texture, tint = '', None
        for j in range(start, end+1):
            key, kind, value = struct.unpack_from('<III', scene, arrays[2][0]+12*j)
            if strings.get(key) == 'diffuseMap' and kind == 6:
                texture = strings[value]
            elif strings.get(key) == 'TintlColor' and kind == 5:
                tint = value
        if texture.endswith(('/volume_01.dds', '/cloud_fog.dds', '/dark_cloud_map_02_seamless.dds')):
            assert tint is not None
            offsets.add(arrays[4][0]+16*tint)
    for offset in offsets:
        scene[offset:offset+16] = warm(original[offset:offset+16])
    last = 0
    for offset in sorted(offsets):
        assert original[last:offset] == scene[last:offset]
        assert original[offset+12:offset+16] == scene[offset+12:offset+16]
        last = offset+16
    assert original[last:] == scene[last:]
    (ROOT/scene_name).write_bytes(scene)
    assert changed > 0 and offsets
    print('Verified warm background: %d atmospheric colors, %d fog materials; density, brightness and other scene data preserved' % (changed, len(offsets)))


if __name__ == '__main__':
    main()
