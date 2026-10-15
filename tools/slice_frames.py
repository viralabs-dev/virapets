"""Lê assets/{happy,barking,waiting,sleeping}.gif, a animação completa de cada humor.

Uso: python3 tools/slice_frames.py [saida.json] [--assets-dir assets] [--size 48]
Requer Pillow. Cada quadro é o quadrado de baixo do GIF (o que sobra em cima é
espaço para o ZzZ); o alfa define o fundo do terminal.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageSequence

from sleep_art import SLEEP_COLOR

ROOT = Path(__file__).resolve().parent.parent
MOODS = ('happy', 'barking', 'waiting', 'sleeping')


def reduce_sprite(tile, size):
    """Integra a área dos pixels e conserva o traço escuro nas bordas.

    Nearest perde linhas menores que um pixel do terminal. A média de área
    conserva a cor do pelo; a cobertura do traço evita um halo sem contorno.
    """
    tile = tile.copy()
    tile.putalpha(tile.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    reduced = tile.resize((size, size), Image.Resampling.BOX)
    dark = Image.new('L', tile.size)
    pixels = tile.get_flattened_data() if hasattr(tile, 'get_flattened_data') else tile.getdata()
    dark.putdata([255 if a and max(r, g, b) < 55 else 0
                  for r, g, b, a in pixels])
    dark = dark.resize((size, size), Image.Resampling.BOX)
    alpha = reduced.getchannel('A')
    output = Image.new('RGBA', reduced.size)
    for y in range(size):
        for x in range(size):
            r, g, b, a = reduced.getpixel((x, y))
            if a < 96:
                continue
            boundary = any(not (0 <= xx < size and 0 <= yy < size)
                           or alpha.getpixel((xx, yy)) < 96
                           for xx, yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            coverage = dark.getpixel((x, y))
            if (boundary and coverage >= 24) or coverage >= 80:
                r, g, b = 0, 0, 0
            output.putpixel((x, y), (r, g, b, 255))
    return output


def gif_frames(source):
    """Os quadros do GIF, sem o espaço de cima nem o ZzZ, que o terminal redesenha na escala dele."""
    zzz = tuple(int(SLEEP_COLOR[i:i + 2], 16) for i in (1, 3, 5))
    tiles = []
    with Image.open(source) as gif:
        side = gif.width
        if gif.height < side:
            raise ValueError(f'{source}: o quadro precisa ser ao menos tão alto quanto largo')
        for frame in ImageSequence.Iterator(gif):
            tile = frame.convert('RGBA').crop((0, gif.height - side, side, gif.height))
            if tile.getchannel('A').getextrema()[0] == 255:
                raise ValueError(f'{source}: o fundo precisa ter transparência real')
            # O build_gifs.py reserva a cor exata do ZzZ na paleta: basta compará-la.
            pixels = tile.load()
            for y in range(side):
                for x in range(side):
                    if pixels[x, y][3] and pixels[x, y][:3] == zzz:
                        pixels[x, y] = (0, 0, 0, 0)
            tiles.append(tile)
    return tiles


def durations(assets_dir=ROOT / 'assets'):
    """O tempo de cada quadro, em ms, como gravado em cada GIF."""
    result = {}
    for mood in MOODS:
        with Image.open(Path(assets_dir) / f'{mood}.gif') as gif:
            result[mood] = [frame.info['duration'] for frame in ImageSequence.Iterator(gif)]
    return result


def extract(assets_dir=ROOT / 'assets', size=48, preserve_edges=False):
    if size < 8 or size % 2:
        raise ValueError('size deve ser par e >= 8')
    result = {}
    for mood in MOODS:
        result[mood] = []
        for tile in gif_frames(Path(assets_dir) / f'{mood}.gif'):
            tile = reduce_sprite(tile, size) if preserve_edges else tile.resize((size, size), Image.Resampling.NEAREST)

            def pixel(x, y):
                r, g, b, a = tile.getpixel((x, y))
                return '#%02x%02x%02x' % (r, g, b) if a >= 128 else ''

            result[mood].append([[[pixel(x, y), pixel(x, y + 1)] for x in range(size)]
                                 for y in range(0, size, 2)])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?')
    parser.add_argument('--assets-dir', type=Path, default=ROOT / 'assets')
    parser.add_argument('--size', type=int, default=48)
    args = parser.parse_args()
    text = json.dumps(extract(args.assets_dir, size=args.size))
    if args.output:
        Path(args.output).write_text(text + '\n')
    else:
        print(text)


if __name__ == '__main__':
    main()
