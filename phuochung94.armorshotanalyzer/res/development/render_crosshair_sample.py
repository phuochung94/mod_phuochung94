"""Author the static settings sample from the current HUD font/palette (Pillow)."""
from pathlib import Path
import re
import runpy
import zlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = Path(__file__).resolve().parent
gui = HERE.parent / 'gui/ArmorShotAnalyzer/gameface'
css = (gui / 'ArmorShotAnalyzerBattleView.css').read_text()
font = gui / re.search(r'src:\s*url\("([^"]+)"\)', css).group(1)
palette = runpy.run_path(str(HERE / 'source/armorshotanalyzer_shell_info.py'))['DISPLAY_PALETTE']
def rgb(value): return tuple(int(value[n:n+2], 16) for n in (0,2,4))
color = tuple(round(a + (b-a) * (72.3-50)/43)
              for a,b in zip(rgb(palette['MEDIUM_CHANCE']), rgb(palette['HIGH_CHANCE'])))
scale = 3
image = Image.new('RGBA', (256*scale, 256*scale))
mask = Image.new('L', image.size)
colored_masks = []
for text, size, y, center, ink in [('215',22,155,128,color),
        ('45\u00b0',16,165,160,(255,255,255))]:
    row_mask = Image.new('L', image.size)
    draw = ImageDraw.Draw(row_mask)
    face = ImageFont.truetype(str(font), size*scale)
    box = draw.textbbox((0,0), text, font=face)
    assert (box[2]-box[0])/scale <= 244
    x = center*scale - (box[2]-box[0])/2 - box[0]
    top = y*scale - (box[3]-box[1])/2 - box[1]
    draw.text((x,top), text, font=face, fill=255)
    mask = ImageChops.lighter(mask, row_mask)
    colored_masks.append((row_mask, ink))
shadow = Image.new('RGBA', image.size, (0,0,0,0))
shadow.putalpha(ImageChops.offset(mask, 0, 2*scale).filter(
    ImageFilter.GaussianBlur(2*scale)).point(lambda a: round(a*.75)))
image.alpha_composite(shadow)
for row_mask, ink in colored_masks:
    dark = tuple(int(channel*.25 + .5) for channel in ink)
    outline = Image.new('RGBA', image.size, dark+(0,))
    outline.putalpha(row_mask.filter(ImageFilter.MaxFilter(2*scale+1)))
    image.alpha_composite(outline)
for row_mask, ink in colored_masks:
    letters = Image.new('RGBA', image.size, ink+(0,)); letters.putalpha(row_mask)
    image.alpha_composite(letters)
image = image.resize((256,256), Image.Resampling.LANCZOS)
out = HERE / 'resources'; out.mkdir(exist_ok=True)
image.save(out / 'crosshair_preview.png')
raw = bytearray()
for red,green,blue,alpha in image.get_flattened_data():
    raw.extend((alpha, round(red*alpha/255), round(green*alpha/255), round(blue*alpha/255)))
(out / 'crosshair_preview.argb.zlib').write_bytes(zlib.compress(bytes(raw)))
background = Image.new('RGBA', image.size, (90,100,78,255))
background.alpha_composite(image)
background.convert('RGB').save(out / 'crosshair_preview_check.png')
print('Refreshed sample:', font.name, color)
