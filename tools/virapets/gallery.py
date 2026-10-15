"""Standalone offline preview of every pet and mood, with embedded downloads."""
import base64
from html import escape
from PIL import Image, ImageSequence
from .raster import MOODS


def gallery(all_pets):
    sections = []
    for path, pet in all_pets:
        cards = []
        for mood in MOODS:
            source = path / 'animations' / f'{mood}.gif'
            with Image.open(source) as gif:
                count = gif.n_frames
                cycle = sum(f.info['duration'] for f in ImageSequence.Iterator(gif))
            uri = 'data:image/gif;base64,' + base64.b64encode(source.read_bytes()).decode()
            cards.append(f'<figure><h3>{mood.upper()}</h3><img src="{uri}" alt="{escape(pet["name"])} {mood}" width="256" height="280"><figcaption>{count} quadros · {cycle/1000:g} s</figcaption><a download="{pet["id"]}-{mood}.gif" href="{uri}">Baixar GIF</a></figure>')
        package = path / 'stickers' / f'{pet["id"]}-animado.wastickers'
        pack_link = ''
        if package.exists():
            uri = 'data:application/octet-stream;base64,' + base64.b64encode(package.read_bytes()).decode()
            pack_link = f'<p><a download="{package.name}" href="{uri}">Baixar pacote de 4 figurinhas para Android</a></p>'
        badge = 'Primeira versão · em revisão visual' if pet['status'] == 'draft' else 'Arte aprovada'
        sections.append(f'<section><h2>{escape(pet["name"])} <small>{badge}</small></h2>{pack_link}<div class="grid">'+''.join(cards)+'</div></section>')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ViraPets · Animações</title><style>
*{box-sizing:border-box}body{background:#131820;color:#eee;font:16px system-ui;margin:0;padding:32px}main{max-width:1200px;margin:auto}h1{margin-bottom:6px}small{font-size:13px;color:#abb6c4;font-weight:400}p,figcaption{color:#abb6c4}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}figure{margin:0;padding:16px;text-align:center;background:#252525;border:1px solid #49505b;border-radius:12px}h3{font-size:14px;letter-spacing:.12em}img{max-width:100%;height:auto;image-rendering:pixelated}a{color:#c5abe9}button{padding:10px 16px;margin:12px 0;cursor:pointer}body.light figure{background:#f4f1eb;color:#242424}body.light figcaption{color:#555}body.light a{color:#704197}section{margin:24px 0 40px}</style><main><h1>ViraPets</h1><p>Quatro animações por pet · fundo transparente.</p><button onclick="document.body.classList.toggle('light')">Alternar fundo das animações</button>''' + ''.join(sections) + '</main></html>\n'
