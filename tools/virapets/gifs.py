"""Compõe as faixas PNG e exporta GIFs com paleta estável e ZzZ animado."""
import json
from PIL import Image, ImageDraw

from .sleep import SLEEP_SIGNS
from .sleep import GLYPHS, SLEEP_COLOR
from .raster import MOODS, ROOT
from .effects import emotion_layer, GOLD, LIGHT



TIMINGS = {
    # Sorriso sustentado, língua e orelhas em movimento, piscada curta e recuperação.
    'happy': [240, 96, 96, 80, 80, 96, 96, 176],
    # Boca fecha, abre com força e sustenta o latido antes da recuperação.
    'barking': [360, 64, 64, 160, 128, 64, 64, 240],
    # Pausa de repouso com olhos abertos; a piscada não segura cada pose por 200 ms.
    'waiting': [1440, 120, 80, 80, 80, 80, 120, 400],
    # Cochila, tomba a cabeça, desperta brevemente e volta a dormir.
    'sleeping': [1000, 180, 240, 650, 220, 400, 250, 800],
}


def timings(mood, count, timing_map=TIMINGS):
    values = timing_map[mood]
    if len(values) != count or any(n <= 0 for n in values):
        raise ValueError(f'{mood}: quantidade de quadros ou durações inválidas')
    # GIF tem resolução de 10 ms. Arredondar os limites acumulados evita deriva.
    elapsed = previous = 0
    rounded = []
    for value in values:
        elapsed += value
        boundary = ((elapsed + 5) // 10) * 10
        rounded.append(boundary - previous)
        previous = boundary
    if any(n < 20 for n in rounded):
        raise ValueError(f'{mood}: duração curta demais para reprodução portátil em GIF')
    return values, rounded


def compose(strip, mood, sleep_signs=SLEEP_SIGNS, effects=None):
    side = strip.height
    if side < 48 or strip.width % side:
        raise ValueError(f'{mood}: use uma faixa de quadros quadrados, lado >= 48')
    if strip.getchannel('A').getextrema()[0] == 255:
        raise ValueError(f'{mood}: a faixa precisa de fundo transparente')
    scale = max(1, round(side / 128))
    line = 6 * scale
    headroom = 2 * line
    frames = []
    for i in range(strip.width // side):
        tile = strip.crop((i * side, 0, (i + 1) * side, side))
        tile.putalpha(tile.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
        effect = (effects or {}).get(mood)
        if effect:
            tile.alpha_composite(emotion_layer(tile, effect, i, strip.width // side))
        canvas = Image.new('RGBA', (side, side + headroom))
        canvas.alpha_composite(tile, (0, headroom))
        sign = sleep_signs[i % len(sleep_signs)] if mood == 'sleeping' else None
        if sign:
            text, drift, row = sign
            # Letra 50% maior; a posição segue o topo da cabeça, não o topo da tela.
            sign_scale = max(1, round(scale * 1.5))
            advance = 4 * sign_scale
            head_top = tile.getchannel('A').getbbox()[1] + headroom
            gap = max(4, round(side / 32))
            origin_y = max(0, head_top - gap - 5 * sign_scale - (1 - row) * 2 * sign_scale)
            x = max(scale, min(side - len(text) * advance - scale,
                               side // 2 + drift * advance))
            draw = ImageDraw.Draw(canvas)
            for letter, char in enumerate(text):
                for y, bits in enumerate(GLYPHS[char]):
                    for column, bit in enumerate(bits):
                        if bit == '1':
                            left = x + letter * advance + column * sign_scale
                            top = origin_y + y * sign_scale
                            draw.rectangle((left, top, left + sign_scale - 1, top + sign_scale - 1),
                                           fill=(205, 183, 246, 255))
        frames.append(canvas)
    return frames, headroom


def indexed_frames(frames):
    # Uma paleta para o ciclo inteiro evita que as cores oscilem entre poses.
    # O índice 0 é a transparência e o 1 a cor exata do ZzZ, só para os pixels do
    # ZzZ: na mediana ele, com poucos pixels, virava um rosa do pelo. O desenho
    # usa as cores restantes e nunca cai no lilás do ZzZ. Efeitos dourados,
    # quando presentes, também recebem entradas reservadas.
    zzz = tuple(int(SLEEP_COLOR[i:i + 2], 16) for i in (1, 3, 5))
    reserved = [zzz]
    visible_colors = {p[:3] for frame in frames for p in frame.get_flattened_data() if p[3]}
    reserved.extend(color for color in (GOLD, LIGHT) if color in visible_colors)
    offset = len(reserved) + 1
    drawing_count = 256 - offset
    samples = []
    for frame in frames:
        pixels = frame.get_flattened_data() if hasattr(frame, 'get_flattened_data') else frame.getdata()
        samples.extend((r, g, b) for r, g, b, a in pixels if a and (r, g, b) not in reserved)
    if not samples:
        raise ValueError('Animação vazia')
    width = 256
    height = (len(samples) + width - 1) // width
    swatch = Image.new('RGB', (width, height), samples[-1])
    swatch.putdata(samples + [samples[-1]] * (width * height - len(samples)))
    drawing = swatch.quantize(colors=drawing_count, method=Image.Quantize.MEDIANCUT).getpalette()[:drawing_count * 3]
    drawing += drawing[:3] * (drawing_count - len(drawing) // 3)
    palette = Image.new('P', (1, 1))
    # Completa 256 entradas com repetições, para nenhum pixel cair num preto de enchimento.
    palette.putpalette(drawing + drawing[:3] * offset)
    colors = [0, 0, 0] + [channel for color in reserved for channel in color] + drawing
    result = []
    for frame in frames:
        indexed = frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
        indexed = indexed.point([min(i + offset, 255) for i in range(256)])
        indexed.putpalette(colors)
        for position, color in enumerate(reserved, 1):
            mask = Image.new('L', frame.size)
            mask.putdata([255 if a and (r, g, b) == color else 0
                          for r, g, b, a in frame.get_flattened_data()])
            indexed.paste(position, mask=mask)
        indexed.paste(0, mask=frame.getchannel('A').point(lambda a: 255 if a == 0 else 0))
        indexed.info['transparency'] = 0
        result.append(indexed)
    return result


def save_and_verify(path, frames, durations):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, transparency=0, background=0, disposal=2, optimize=False)
    # Confere o GIF decodificado, inclusive limpeza do ZzZ e ausência de rastros.
    with Image.open(path) as decoded:
        if decoded.n_frames != len(frames) or decoded.info.get('loop') != 0:
            raise ValueError(f'{path}: número de quadros ou loop incorreto')
        for i, expected in enumerate(frames):
            decoded.seek(i)
            if decoded.info.get('duration') != durations[i]:
                raise ValueError(f'{path}: duração incorreta no quadro {i}')
            if decoded.convert('RGBA').tobytes() != expected.convert('RGBA').tobytes():
                raise ValueError(f'{path}: composição incorreta no quadro {i}')


def export_gifs(path, data):
    """Valida as quatro faixas antes de exportar o pet selecionado."""
    prepared = {}
    shape = None
    for mood in MOODS:
        with Image.open(path / 'sprites' / f'{mood}.png') as source:
            strip = source.convert('RGBA')
        side = strip.height
        if side < 48 or strip.width != side * len(data['timings'][mood]):
            raise ValueError(f'{mood}: largura deve ser lado × número de quadros de timings; lado >=48')
        if shape is not None and side != shape:
            raise ValueError('As quatro faixas precisam ter o mesmo lado por quadro')
        shape = side
        for i in range(strip.width // side):
            alpha = strip.crop((i*side, 0, (i+1)*side, side)).getchannel('A')
            if not alpha.point(lambda a: 255 if a >=128 else 0).getbbox() or alpha.getextrema()[0] != 0:
                raise ValueError(f'{mood}/{i}: quadro vazio ou sem transparência real')
        frames, headroom = compose(strip, mood, data['sleepSigns'], data.get('effects'))
        original, rounded = timings(mood, len(frames), data['timings'])
        prepared[mood] = (frames, headroom, original, rounded)
    destination = path / 'animations'
    destination.mkdir(exist_ok=True)
    manifest = {'loop':0, 'transparent':True, 'gifTimeResolutionMs':10, 'animations':{}}
    for mood, (frames, headroom, original, rounded) in prepared.items():
        save_and_verify(destination / f'{mood}.gif', indexed_frames(frames), rounded)
        manifest['animations'][mood] = {'file':f'{mood}.gif', 'width':frames[0].width,
            'height':frames[0].height, 'frameCount':len(frames), 'headroomPixels':headroom,
            'sourceDurationsMs':original, 'durationsMs':rounded, 'cycleMs':sum(rounded)}
    (destination/'animations.json').write_text(json.dumps(manifest, indent=2)+'\n')
