"""Gera generated/pets/<id>/frames.ts a partir do GIF completo de cada humor (quadros e tempos). Uso: python3 tools/pets.py build."""
import base64
import struct

from .raster import MOODS, durations, extract
from .sleep import GLYPHS, SLEEP_SIGNS, SLEEP_COLOR

DEFAULT = 0x01000000


# Duas linhas de terminal reservadas acima da imagem, sem redimensionar o cão.
SLEEP_ROWS = 2


def cells(grid, mood=None, frame=0, sleep_signs=SLEEP_SIGNS):
    columns = len(grid[0])
    pixels = [[None] * columns for _ in range(2 * SLEEP_ROWS)]
    for row in grid:
        pixels.append([top for top, bottom in row])
        pixels.append([bottom for top, bottom in row])
    sign = sleep_signs[frame % len(sleep_signs)] if mood == 'sleeping' else None
    if sign:
        text, drift, row = sign
        # Mesmo bitmap do GIF, com tamanho mínimo legível no terminal.
        # Em painéis pequenos cabe uma letra; em 24+ colunas cabe a sequência.
        if columns < 24:
            text = text[-1]
        advance = 4
        x = max(1, min(columns - len(text) * advance, columns // 2 + round(drift * columns * 12 / 256)))
        first_ink = next(i for i, row in enumerate(pixels) if any(row))
        height = min(5, first_ink - 1)
        y = max(0, first_ink - height - 1 - (1 - row))
        for letter, char in enumerate(text):
            glyph = GLYPHS[char]
            # Sprites altos também conservam seus pixels: a letra ocupa só a folga.
            for dy in range(height):
                bits = glyph[round(dy * 4 / (height - 1))]
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


def build(assets_dir, output, size=48, sleep_signs=SLEEP_SIGNS, rendering=None):
    rendering = rendering or {}
    profile = rendering.get('profile', 'outlined')
    sizes = rendering.get('sizes', [8, 16, 24, 32, 40, 48])
    frames = extract(assets_dir, size=size, preserve_edges=True, profile=profile)
    rows, columns = len(frames['happy'][0]) + SLEEP_ROWS, len(frames['happy'][0][0])
    out = ['// Gerado por tools/pets.py build. Não edite à mão.',
           "import type { Mood } from '../../../types'",
           f'export const COLUMNS = {columns}', f'export const ROWS = {rows}',
           'export const FRAMES: Record<Mood, readonly string[]> = {']
    for mood in MOODS:
        out.append(f'  {mood}: [')
        out.extend(f"    '{cells(grid, mood, i, sleep_signs)}'," for i, grid in enumerate(frames[mood]))
        out.append('  ],')
    out.append('}')
    out.append('/** Tempo de cada quadro em ms, lido do GIF. */')
    out.append('export const DURATIONS: Record<Mood, readonly number[]> = {')
    out.extend(f'  {mood}: {times},' for mood, times in durations(assets_dir).items())
    out.append('}')
    out.append('export type FrameSet = { columns: number; rows: number; frames: Record<Mood, readonly string[]> }')
    out.append('export const FRAME_SETS: Record<number, FrameSet> = {')
    out.append(f'  {columns}: {{ columns: COLUMNS, rows: ROWS, frames: FRAMES }},')
    output.parent.mkdir(parents=True, exist_ok=True)
    for small_size in sizes:
        if small_size >= size:
            continue
        small = extract(assets_dir, size=small_size, preserve_edges=True, profile=profile)
        stem = f'{output.stem}-{small_size}'
        out.insert(1, f"import {{ FRAMES as FRAMES_{small_size} }} from './{stem}'")
        out.append(f'  {small_size}: {{ columns: {small_size}, rows: {small_size // 2 + SLEEP_ROWS}, frames: FRAMES_{small_size} }},')
        module = ['// Gerado por tools/pets.py build. Não edite à mão.',
                  "import type { Mood } from '../../../types'",
                  'export const FRAMES: Record<Mood, readonly string[]> = {']
        for mood in MOODS:
            module.append(f'  {mood}: [')
            module.extend(f"    '{cells(grid, mood, i, sleep_signs)}'," for i, grid in enumerate(small[mood]))
            module.append('  ],')
        module.append('}')
        output.with_name(stem + '.ts').write_text('\n'.join(module) + '\n')
    out.append('}')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(out) + '\n')
    print(f'{output}: {columns} x {rows} células; {sum(len(v) for v in frames.values())} quadros')
