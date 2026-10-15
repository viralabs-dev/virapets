"""Exporta GIFs completos, transparentes e em loop, com a composição do Jojo.

Uso: python3 tools/build_gifs.py
Requer Pillow. Os tempos ficam em TIMINGS, abaixo; os ZzZ vêm de sleep_art.py.
Os GIFs são a fonte do painel: depois de gerá-los, rode tools/build_frames.py.
"""
import argparse
import base64
import json
from pathlib import Path

from PIL import Image, ImageDraw

from build_frames import SLEEP_SIGNS
from sleep_art import GLYPHS, SLEEP_COLOR
from slice_frames import MOODS, ROOT



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


def timings(mood, count):
    values = TIMINGS[mood]
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


def compose(strip, mood):
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
        canvas = Image.new('RGBA', (side, side + headroom))
        canvas.alpha_composite(tile, (0, headroom))
        sign = SLEEP_SIGNS[i % len(SLEEP_SIGNS)] if mood == 'sleeping' else None
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
    # usa as outras 254 cores e nunca cai no lilás do ZzZ.
    zzz = tuple(int(SLEEP_COLOR[i:i + 2], 16) for i in (1, 3, 5))
    samples = []
    for frame in frames:
        pixels = frame.get_flattened_data() if hasattr(frame, 'get_flattened_data') else frame.getdata()
        samples.extend((r, g, b) for r, g, b, a in pixels if a and (r, g, b) != zzz)
    if not samples:
        raise ValueError('Animação vazia')
    width = 256
    height = (len(samples) + width - 1) // width
    swatch = Image.new('RGB', (width, height), samples[-1])
    swatch.putdata(samples + [samples[-1]] * (width * height - len(samples)))
    drawing = swatch.quantize(colors=254, method=Image.Quantize.MEDIANCUT).getpalette()[:762]
    drawing += drawing[:3] * (254 - len(drawing) // 3)
    palette = Image.new('P', (1, 1))
    # Completa 256 entradas com repetições, para nenhum pixel cair num preto de enchimento.
    palette.putpalette(drawing + drawing[:3] * 2)
    colors = [0, 0, 0] + list(zzz) + drawing
    result = []
    for frame in frames:
        indexed = frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
        indexed = indexed.point([min(i + 2, 255) for i in range(256)])
        indexed.putpalette(colors)
        sleep = Image.new('L', frame.size)
        sleep.putdata([255 if a and (r, g, b) == zzz else 0
                       for r, g, b, a in (frame.get_flattened_data() if hasattr(frame, 'get_flattened_data') else frame.getdata())])
        indexed.paste(1, mask=sleep)
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


def gallery(manifest, directory):
    cards = []
    for mood, data in manifest['animations'].items():
        payload = base64.b64encode((directory / data['file']).read_bytes()).decode('ascii')
        uri = 'data:image/gif;base64,' + payload
        cards.append(f'''<figure><h2>{mood.upper()}</h2>
<img src="{uri}" width="{data['width']}" height="{data['height']}" alt="Jojo {mood}">
<figcaption>{data['frameCount']} quadros · {data['cycleMs'] / 1000:g} s por ciclo</figcaption>
<a href="{uri}" download="{data['file']}">Baixar GIF</a></figure>''')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Animações do Jojo</title><style>
*{box-sizing:border-box}body{margin:0;padding:32px;font:16px system-ui;background:#131820;color:#eee}
main{max-width:1200px;margin:auto}h1{margin-bottom:8px}p,figcaption{color:#aeb6c4}
input{margin:18px 5px 18px 16px}label{cursor:pointer}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
figure{margin:0;padding:20px;text-align:center;background:#252525;border:1px solid #49505b;border-radius:12px}
h2{font-size:14px;letter-spacing:.13em;margin:0}img{display:block;margin:auto;max-width:100%;height:auto;image-rendering:pixelated}
figcaption{font-size:13px;margin:10px 0}a{color:#bda1ed;font-size:14px}
#light:checked~.gallery figure{background:#f4f1eb;color:#242424}
#light:checked~.gallery figcaption{color:#555}#light:checked~.gallery a{color:#6f4197}
#checker:checked~.gallery figure{background-color:#333;background-image:conic-gradient(#444 25%,transparent 0 50%,#444 0 75%,transparent 0);background-size:24px 24px}
</style><main><h1>Animações do Jojo</h1><p>Quatro estados completos, em loop e com fundo transparente.</p>
<input id="dark" name="bg" type="radio" checked><label for="dark">Escuro</label>
<input id="light" name="bg" type="radio"><label for="light">Claro</label>
<input id="checker" name="bg" type="radio"><label for="checker">Xadrez</label>
<div class="gallery">''' + '\n'.join(cards) + '</div></main></html>\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, default=ROOT / 'assets')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'assets')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {'loop': 0, 'transparent': True, 'gifTimeResolutionMs': 10, 'animations': {}}
    for mood in MOODS:
        with Image.open(args.assets_dir / f'{mood}.png') as strip:
            frames, headroom = compose(strip.convert('RGBA'), mood)
        original, durations = timings(mood, len(frames))
        target = args.output_dir / f'{mood}.gif'
        save_and_verify(target, indexed_frames(frames), durations)
        manifest['animations'][mood] = {
            'file': target.name, 'width': frames[0].width, 'height': frames[0].height,
            'frameCount': len(frames), 'headroomPixels': headroom,
            'sourceDurationsMs': original, 'durationsMs': durations, 'cycleMs': sum(durations),
        }
        print(f'{target}: {len(frames)} quadros, {sum(durations)} ms, validado')
    (args.output_dir / 'animations.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (args.output_dir / 'animation-jojo.html').write_text(gallery(manifest, args.output_dir))


if __name__ == '__main__':
    main()
