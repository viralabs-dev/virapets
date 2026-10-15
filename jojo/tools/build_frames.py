"""Gera hooks/frames.ts a partir de assets/jojo-sprites.jpeg.

Uso: python3 tools/build_frames.py   (precisa do Pillow)
O tamanho vem da grade da pixel art (tools/slice_frames.py).
Cada célula do Raster é ▀ com a cor do pixel de cima na frente e a do de baixo no fundo;
fundo transparente vira a cor padrão do terminal.
"""
import base64, json, struct, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = 0x01000000
raw = subprocess.run([sys.executable, str(ROOT / 'tools/slice_frames.py'), '/dev/stdout'],
                     check=True, capture_output=True, text=True).stdout
frames = json.loads(raw)

def color(h):
    return int(h[1:], 16) if h else DEFAULT

def cells(grid):
    words = []
    for row in grid:
        for top, bottom in row:
            if top and bottom:
                words += [0x2580, color(top), color(bottom)]       # ▀
            elif top:
                words += [0x2580, color(top), DEFAULT]
            elif bottom:
                words += [0x2584, color(bottom), DEFAULT]           # ▄
            else:
                words += [0x20, DEFAULT, DEFAULT]
    return base64.b64encode(struct.pack('<%dI' % len(words), *words)).decode()

rows = len(frames['happy'][0])
COLS = len(frames['happy'][0][0])
out = ['// Gerado por tools/build_frames.py a partir de assets/jojo-sprites.jpeg. Não edite à mão.',
       "import type { Mood } from '../types'",
       f'export const COLUMNS = {COLS}',
       f'export const ROWS = {rows}',
       'export const FRAMES: Record<Mood, readonly string[]> = {']
for mood in ('happy', 'barking', 'waiting'):
    out.append(f'  {mood}: [')
    out += [f"    '{cells(g)}'," for g in frames[mood]]
    out.append('  ],')
out.append('}')
(ROOT / 'hooks/frames.ts').write_text('\n'.join(out) + '\n')
print('frames.ts:', COLS, 'x', rows, 'células,', sum(len(v) for v in frames.values()), 'quadros')
