"""Recorta os 12 quadros da folha de sprites na grade da própria pixel art.

Uso: python3 tools/slice_frames.py [saída.json]   (precisa do Pillow)

A folha é pixel art ampliada: cada pixel da arte ocupa ~10,2 px da imagem. Em vez de
reduzir por média (que borra), o recorte acha a fase da grade em cada quadro e lê o
centro de cada pixel da arte (mediana de 9 pontos, contra o ruído do JPEG). O fundo
quadriculado vira transparente, e as bordas vazias comuns aos 12 quadros saem.
"""
import json
import sys
from pathlib import Path
from statistics import median

from PIL import Image

SRC = Path(__file__).resolve().parent.parent / 'assets' / 'jojo-sprites.jpeg'
PITCH = 10.2  # px da imagem por pixel da arte (medido)
BANDS = {'happy': 153, 'barking': 850, 'waiting': 1567}  # topo de cada linha da folha
XS = [61, 573, 1065, 1577]  # esquerda de cada quadro
SIDE = 442  # lado do recorte de cada quadro, em px da imagem
CELLS = int(SIDE / PITCH)


def is_bg(p):
    mx, mn = max(p), min(p)
    return mn > 185 and (mx - mn) < 28  # quadriculado branco e cinza-claro


def phase(px, x0, y0):
    """A fase da grade neste quadro: a que menos varia dentro de cada pixel da arte."""
    best = None
    for ox in range(11):
        for oy in range(11):
            cost = 0
            for j in range(4, CELLS - 4, 2):
                for i in range(4, CELLS - 4, 2):
                    cx, cy = x0 + ox + (i + 0.5) * PITCH, y0 + oy + (j + 0.5) * PITCH
                    a = px[int(cx), int(cy)]
                    for d in (-0.3, 0.3):
                        b = px[int(cx + d * PITCH), int(cy + d * PITCH)]
                        cost += sum(abs(u - v) for u, v in zip(a, b))
            if best is None or cost < best[0]:
                best = (cost, ox, oy)
    return best[1], best[2]


def sample(px, cx, cy):
    pts = [px[int(cx + dx), int(cy + dy)] for dx in (-2, 0, 2) for dy in (-2, 0, 2)]
    dog = [p for p in pts if not is_bg(p)]
    if len(dog) < 5:
        return ''
    return '#%02x%02x%02x' % tuple(round(median(p[i] for p in dog)) for i in range(3))


im = Image.open(SRC).convert('RGB')
px = im.load()
grids = {}
for name, y0 in BANDS.items():
    grids[name] = []
    for x0 in XS:
        ox0, oy0 = x0 - 12, y0 - 12
        ox, oy = phase(px, ox0, oy0)
        grids[name].append([[sample(px, ox0 + ox + (i + 0.5) * PITCH, oy0 + oy + (j + 0.5) * PITCH)
                             for i in range(CELLS)] for j in range(CELLS)])

# Bordas vazias comuns aos 12 quadros.
every = [g for frames in grids.values() for g in frames]
used_rows = [j for j in range(CELLS) if any(g[j][i] for g in every for i in range(CELLS))]
used_cols = [i for i in range(CELLS) if any(g[j][i] for g in every for j in range(CELLS))]
top, bottom = used_rows[0], used_rows[-1] + 1
left, right = used_cols[0], used_cols[-1] + 1
if (bottom - top) % 2:
    bottom += 1  # altura par: duas linhas da arte por célula do terminal


def cell(g, j, i):
    return g[j][i] if j < CELLS and i < CELLS else ''


result = {name: [[[[cell(g, j, i), cell(g, j + 1, i)] for i in range(left, right)]
                  for j in range(top, bottom, 2)] for g in frames]
          for name, frames in grids.items()}
json.dump(result, open(sys.argv[1] if len(sys.argv) > 1 else '/dev/stdout', 'w'))
