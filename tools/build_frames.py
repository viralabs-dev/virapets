"""Gera hooks/frames.ts a partir do GIF completo de cada humor (quadros e tempos). Uso: python3 tools/build_frames.py."""
import argparse
import base64
import struct
from pathlib import Path

from slice_frames import MOODS, ROOT, durations, extract
from sleep_art import GLYPHS, SLEEP_SIGNS, SLEEP_COLOR

DEFAULT = 0x01000000


# Duas linhas de terminal reservadas acima da imagem, sem redimensionar o cão.
SLEEP_ROWS = 2


def cells(grid, mood=None, frame=0):
    columns = len(grid[0])
    pixels = [[None] * columns for _ in range(2 * SLEEP_ROWS)]
    for row in grid:
        pixels.append([top for top, bottom in row])
        pixels.append([bottom for top, bottom in row])
    sign = SLEEP_SIGNS[frame % len(SLEEP_SIGNS)] if mood == 'sleeping' else None
    if sign:
        text, drift, row = sign
        # Mesmo bitmap do GIF, com tamanho mínimo legível no terminal.
        # Em painéis pequenos cabe uma letra; em 24+ colunas cabe a sequência.
        if columns < 24:
            text = text[-1]
        advance = 4
        x = max(1, min(columns - len(text) * advance, columns // 2 + round(drift * columns * 12 / 256)))
        first_ink = next(i for i, row in enumerate(pixels) if any(row))
        y = max(0, first_ink - 6 - (1 - row))
        for letter, char in enumerate(text):
            for dy, bits in enumerate(GLYPHS[char]):
                for dx, bit in enumerate(bits):
                    if bit == '1':
                        pixels[y + dy][x + letter * advance + dx] = SLEEP_COLOR
    words = []
    for y in range(0, len(pixels), 2):
        for top, bottom in zip(pixels[y], pixels[y + 1]):
            color_top = int(top[1:], 16) if top else DEFAULT
            color_bottom = int(bottom[1:], 16) if bottom else DEFAULT
            if top:
                words.extend((0x2580, color_top, color_bottom))
            elif bottom:
                words.extend((0x2584, color_bottom, DEFAULT))
            else:
                words.extend((0x20, DEFAULT, DEFAULT))
    return base64.b64encode(struct.pack('<%dI' % len(words), *words)).decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, default=ROOT / 'assets')
    parser.add_argument('--output', type=Path, default=ROOT / 'hooks/frames.ts')
    parser.add_argument('--size', type=int, default=48)
    args = parser.parse_args()
    frames = extract(args.assets_dir, size=args.size, preserve_edges=True)
    rows, columns = len(frames['happy'][0]) + SLEEP_ROWS, len(frames['happy'][0][0])
    out = ['// Gerado por tools/build_frames.py. Não edite à mão.',
           "import type { Mood } from '../types'",
           f'export const COLUMNS = {columns}', f'export const ROWS = {rows}',
           'export const FRAMES: Record<Mood, readonly string[]> = {']
    for mood in MOODS:
        out.append(f'  {mood}: [')
        out.extend(f"    '{cells(grid, mood, i)}'," for i, grid in enumerate(frames[mood]))
        out.append('  ],')
    out.append('}')
    out.append('/** Tempo de cada quadro em ms, lido do GIF. */')
    out.append('export const DURATIONS: Record<Mood, readonly number[]> = {')
    out.extend(f'  {mood}: {times},' for mood, times in durations(args.assets_dir).items())
    out.append('}')
    out.append('export type FrameSet = { columns: number; rows: number; frames: Record<Mood, readonly string[]> }')
    out.append('export const FRAME_SETS: Record<number, FrameSet> = {')
    out.append(f'  {columns}: {{ columns: COLUMNS, rows: ROWS, frames: FRAMES }},')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for size in (8, 16, 24, 32, 40):
        if size >= args.size:
            continue
        small = extract(args.assets_dir, size=size, preserve_edges=True)
        stem = f'{args.output.stem}-{size}'
        out.insert(1, f"import {{ FRAMES as FRAMES_{size} }} from './{stem}'")
        out.append(f'  {size}: {{ columns: {size}, rows: {size // 2 + SLEEP_ROWS}, frames: FRAMES_{size} }},')
        module = ['// Gerado por tools/build_frames.py. Não edite à mão.',
                  "import type { Mood } from '../types'",
                  'export const FRAMES: Record<Mood, readonly string[]> = {']
        for mood in MOODS:
            module.append(f'  {mood}: [')
            module.extend(f"    '{cells(grid, mood, i)}'," for i, grid in enumerate(small[mood]))
            module.append('  ],')
        module.append('}')
        args.output.with_name(stem + '.ts').write_text('\n'.join(module) + '\n')
    out.append('}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(out) + '\n')
    print(f'{args.output}: {columns} x {rows} células; {sum(len(v) for v in frames.values())} quadros')


if __name__ == '__main__':
    main()
