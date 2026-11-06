"""Restore native garage atmosphere, excluding directional beam effects."""
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia\res\packages')


def u16(b, p):
    return struct.unpack_from('<H', b, p)[0]


def u32(b, p):
    return struct.unpack_from('<I', b, p)[0]


def parse(b):
    assert u32(b, 0) == 0x62a14e45
    keys = []
    pos = 5
    while b[pos]:
        end = b.index(0, pos)
        keys.append(b[pos:end].decode())
        pos = end + 1
    pos += 1

    def node(start, end, kind, path):
        if kind:
            return dict(kind=kind, data=b[start:end], path=path, children=[])
        count = u16(b, start)
        first = u32(b, start + 2)
        base = start + 6 + count * 6
        previous = first & 0xfffffff
        result = dict(kind=0, own=first >> 28, data=b[base:base+previous], path=path, children=[])
        for i in range(count):
            p = start + 6 + 6*i
            key = u16(b, p)
            value = u32(b, p+2)
            last = value & 0xfffffff
            result['children'].append((key, node(base+previous, base+last, value >> 28, path+'/'+keys[key])))
            previous = last
        assert base + previous == end
        return result

    return b[:pos], node(pos, len(b), 0, '')


def encode(n):
    if n['kind']:
        return n['data']
    parts = [(key, child, encode(child)) for key, child in n['children']]
    offset = len(n['data'])
    header = struct.pack('<HI', len(parts), offset | n['own'] << 28)
    for key, child, data in parts:
        offset += len(data)
        header += struct.pack('<HI', key, offset | child['kind'] << 28)
    return header + n['data'] + b''.join(data for _, _, data in parts)


def walk(n):
    yield n
    for _, child in n['children']:
        yield from walk(child)


def save(name, data):
    dest = ROOT / 'res' / name
    dest.resolve().relative_to((ROOT/'res').resolve())
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def main():
    garage = ROOT/'res/spaces/hangar_v4'
    for p in garage.rglob('*'):
        if p.is_file():
            p.resolve().relative_to(garage.resolve())
            p.unlink()
    with zipfile.ZipFile(GAME/'hangar_v4.pkg') as archive:
        environments = [n for n in archive.namelist() if n.startswith('spaces/hangar_v4/environments/') and n.endswith('/environment.xml')]
        for name in environments:
            source = archive.read(name)
            header, tree = parse(source)
            assert header+encode(tree) == source
            for n in walk(tree):
                if n['path'] in ('/GodRays/enable', '/VolumetricFog/sampleShadows', '/VolumetricFog/useLightMarching', '/VolumetricFog/enableLocalLights'):
                    n.update(kind=1, data=b'false')
                elif n['path'] == '/VolumetricFog/sunLightScatterCoef':
                    n.update(kind=3, data=struct.pack('<f', 0))
            output = header+encode(tree)
            h, t = parse(output)
            assert h+encode(t) == output
            save(name, output)
        scene = bytearray(archive.read('spaces/hangar_v4/space.bin'))
    sections = {}
    for i in range(u32(scene, 20)):
        p = 24+24*i
        sections[scene[p:p+4].decode()] = struct.unpack_from('<QQ', scene, p+8)
    st = sections['BWST'][0]
    assert u32(scene, st) == 12
    count = u32(scene, st+4)
    base = st+12+12*count
    strings = {}
    for i in range(count):
        key, offset, size = struct.unpack_from('<III', scene, st+8+12*i)
        strings[key] = scene[base+offset:base+offset+size].decode()
    arrays = []
    p = sections['BSMA'][0]
    for expected in (16, 4, 12, 64, 16):
        stride, count = struct.unpack_from('<II', scene, p)
        assert stride == expected
        arrays.append((p+8, count))
        p += 8+stride*count
    patches = []
    for i in range(arrays[0][1]):
        shader, start, end, _ = struct.unpack_from('<IIII', scene, arrays[0][0]+16*i)
        if shader >= arrays[1][1]:
            continue
        shader_name = strings[u32(scene, arrays[1][0]+4*shader)]
        if shader_name not in ('shaders/custom/vector_animation_2.fx', 'shaders/custom/volumetric_effect_vtx.fx'):
            continue
        texture, tint = '', None
        for j in range(start, end+1):
            key, kind, value = struct.unpack_from('<III', scene, arrays[2][0]+12*j)
            if strings.get(key) == 'diffuseMap' and kind == 6:
                texture = strings[value]
            elif strings.get(key) == 'TintlColor' and kind == 5:
                tint = value
        if texture.endswith(('/Rays_01.dds', '/volume_lights_white.dds')):
            assert tint is not None
            patches.append(arrays[4][0]+16*tint)
    assert len(patches) == 6
    for offset in patches:
        scene[offset:offset+16] = bytes(16)
    save('spaces/hangar_v4/space.bin', scene)
    # Rebuild sequence overrides from native files: retain fog and steam objects.
    folder = ROOT/'res/particles/eff_sequence'
    for path in folder.glob('h_v4_*.seq'):
        path.resolve().relative_to(folder.resolve())
        path.unlink()
    removed, sequences = 0, 0
    for pkg in GAME.glob('particles*.pkg'):
        with zipfile.ZipFile(pkg) as archive:
            for name in archive.namelist():
                if not name.startswith('particles/eff_sequence/h_v4_') or not name.endswith('.seq'):
                    continue
                source = archive.read(name)
                header, tree = parse(source)
                assert header+encode(tree) == source
                keep = []
                for key, child in tree['children']:
                    resources = [n['data'].decode() for _, n in child['children'] if n['path'] == '/sequenceObject/resource' and n['kind'] == 1]
                    beam = any(('environment/hangar_v4/godrays' in r or 'environment/hangar_v4/volume_lights' in r or 'hangar_v4_dust_volume_ray_' in r) for r in resources)
                    if beam:
                        removed += 1
                    else:
                        keep.append((key, child))
                if len(keep) == len(tree['children']):
                    continue
                tree['children'] = keep
                output = header+encode(tree)
                h, t = parse(output)
                assert h+encode(t) == output
                save(name, output)
                sequences += 1
    print('Restored native garage: %d environments; disabled %d beam materials and %d beam objects in %d sequences' % (len(environments), len(patches), removed, sequences))


if __name__ == '__main__':
    main()
