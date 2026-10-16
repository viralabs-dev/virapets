"""Standalone offline preview of every pet and mood, with embedded downloads."""
import base64
import io
import zipfile
from html import escape
from PIL import Image, ImageSequence
from .raster import MOODS


def gallery(all_pets, featured=None):
    all_pets = list(all_pets)
    if featured and not any(pet['id'] == featured for _, pet in all_pets):
        raise ValueError(f'{featured}: pet destacado ausente ou incompleto na galeria')
    order = list(dict.fromkeys(([featured] if featured else []) + ['jojo', 'mel', 'dara']))
    all_pets.sort(key=lambda item: (order.index(item[1]['id']) if item[1]['id'] in order else len(order), item[1]['id']))
    sections = []
    for path, pet in all_pets:
        cards = []
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as pack:
            for mood in MOODS:
                entry = zipfile.ZipInfo(f'{pet["id"]}-{mood}.gif', date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                pack.writestr(entry, (path/'animations'/f'{mood}.gif').read_bytes())
        zip_uri = 'data:application/zip;base64,' + base64.b64encode(archive.getvalue()).decode()
        zip_link = f'<a download="{pet["id"]}-gifs.zip" href="{zip_uri}">Baixar os 4 GIFs (ZIP)</a>'
        for mood in MOODS:
            source = path / 'animations' / f'{mood}.gif'
            with Image.open(source) as gif:
                count = gif.n_frames
                cycle = sum(f.info['duration'] for f in ImageSequence.Iterator(gif))
            uri = 'data:image/gif;base64,' + base64.b64encode(source.read_bytes()).decode()
            cards.append(f'<figure><h3>{mood.upper()}</h3><img src="{uri}" alt="{escape(pet["name"])} {mood}" width="256" height="280"><figcaption>{count} quadros · {cycle/1000:g} s</figcaption><a download="{pet["id"]}-{mood}.gif" href="{uri}">Baixar GIF</a></figure>')
        package = path / 'stickers' / f'{pet["id"]}-animado.wastickers'
        pack_link = '<span>Pacote de figurinhas ainda não exportado.</span>'
        if package.exists():
            uri = 'data:application/octet-stream;base64,' + base64.b64encode(package.read_bytes()).decode()
            pack_link = f'<a download="{package.name}" href="{uri}">Baixar pacote de 4 figurinhas para WhatsApp (.wastickers)</a>'
        badge = 'Primeira versão · em revisão visual' if pet['status'] == 'draft' else 'Arte aprovada'
        sections.append(f'<section data-pet="{pet["id"]}"><h2>{escape(pet["name"])} <small>{"Seu pet · " if pet["id"] == featured else ""}{badge}</small></h2><p class="downloads">{zip_link} {pack_link}</p><div class="grid">'+''.join(cards)+'</div></section>')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ViraPets · Animações</title><style>
*{box-sizing:border-box}body{background:#131820;color:#eee;font:16px system-ui;margin:0;padding:32px}main{max-width:1200px;margin:auto}h1{margin-bottom:6px}small{font-size:13px;color:#abb6c4;font-weight:400}p,figcaption{color:#abb6c4}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}figure{margin:0;padding:16px;text-align:center;background:#252525;border:1px solid #49505b;border-radius:12px}h3{font-size:14px;letter-spacing:.12em}img{max-width:100%;height:auto;image-rendering:pixelated}a{color:#c5abe9}button{padding:10px 16px;margin:12px 0;cursor:pointer}body.light figure{background:#f4f1eb;color:#242424}body.light figcaption{color:#555}body.light a{color:#704197}section{margin:24px 0 40px}.downloads{display:flex;gap:16px;flex-wrap:wrap}.downloads a{border:1px solid #66547e;border-radius:8px;padding:10px 14px}</style><main><h1>ViraPets</h1><p>Quatro animações por pet · fundo transparente · downloads incorporados para usar offline.</p><p>Para WhatsApp no Android: baixe o pacote e abra em um aplicativo compatível com .wastickers animados; depois use Adicionar ao WhatsApp. Esta página baixa o pacote, não instala figurinhas diretamente.</p><button onclick="document.body.classList.toggle('light')">Alternar fundo das animações</button>''' + ''.join(sections) + '</main></html>\n'
