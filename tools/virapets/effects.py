"""Efeitos em pixels sincronizados às poses, sem repintar ou reduzir o pet."""
from PIL import Image, ImageDraw, ImageChops

GOLD = (255, 201, 0)
LIGHT = (255, 235, 104)

def emotion_layer(tile, effect, index, count):
    side = tile.width
    layer = Image.new('RGBA', tile.size)
    phase = min(7, index * 8 // count)
    active = (2, 4, 5) if effect == 'sparkles' else (2, 4)
    if phase not in active:
        return layer
    alpha = tile.getchannel('A')
    box = alpha.getbbox()
    if not box:
        return layer
    unit = max(1, round(side / 128))
    gold = (*GOLD, 255)
    light = (*LIGHT, 255)
    draw = ImageDraw.Draw(layer)
    if effect == 'sparkles':
        radius = (5 if phase == 4 else 4) * unit
        x = min(side - radius - 3 * unit, round(side * .76))
        local = alpha.crop((x - radius, 0, x + radius + 1, side)).getbbox()
        top = local[1] if local else box[1]
        y = max(radius + 3 * unit, top - radius - 5 * unit)
        draw.polygon([(x, y-radius), (x+unit, y-unit), (x+radius, y),
                      (x+unit, y+unit), (x, y+radius), (x-unit, y+unit),
                      (x-radius, y), (x-unit, y-unit)], fill=gold)
        draw.rectangle((x-unit, y-unit, x+unit, y+unit), fill=light)
    elif effect == 'bark':
        y = round(side * .62)
        spread = 9 * unit
        band = alpha.crop((0, max(0, y-spread-2*unit), side, min(side, y+spread+2*unit))).getbbox()
        right = band[2] if band else box[2]
        start = right + 3 * unit
        end = min(side - 4 * unit, start + 16 * unit)
        if end - start < 4 * unit:
            raise ValueError('BARKING precisa de margem lateral para o efeito de latido')
        width = max(2, 2 * unit)
        draw.line((start, y, end, y), fill=gold, width=width)
        draw.line((start, y-4*unit, end-2*unit, y-spread), fill=gold, width=width)
        draw.line((start, y+4*unit, end-2*unit, y+spread), fill=gold, width=width)
    else:
        raise ValueError(f'Efeito desconhecido: {effect}')
    # Mesmo uma referência com margens diferentes nunca é coberta pelo efeito.
    layer.putalpha(ImageChops.subtract(layer.getchannel('A'), alpha))
    return layer
