"""Exporta um pacote .wastickers animado a partir dos quatro GIFs de um pet.

Não é um instalador: o pacote usa o mesmo esquema importável do Jojo aprovado.
O exportador não altera os GIFs nem outros pets. A seleção de pets pertence ao CLI.
"""
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

from PIL import Image, ImageChops, ImageSequence

from .raster import MOODS

MAX_BYTES = 500_000
MAX_CYCLE_MS = 10_000


def sticker_frames(source):
    """Preserva a composição inteira, inclusive o ZzZ, com margem transparente."""
    frames, durations = [], []
    with Image.open(source) as gif:
        if gif.info.get('loop') != 0:
            raise ValueError(f'{source}: a animação precisa repetir continuamente')
        for frame in ImageSequence.Iterator(gif):
            durations.append(frame.info.get('duration', 0))
            tile = frame.convert('RGBA')
            if tile.getchannel('A').getextrema()[0] != 0 or not tile.getchannel('A').getbbox():
                raise ValueError(f'{source}: quadro vazio ou sem transparência')
            scale = min(480 / tile.width, 480 / tile.height)
            tile = tile.resize((round(tile.width * scale), round(tile.height * scale)), Image.Resampling.NEAREST)
            canvas = Image.new('RGBA', (512, 512))
            canvas.alpha_composite(tile, ((512 - tile.width) // 2, (512 - tile.height) // 2))
            frames.append(canvas)
    if len(frames) < 2 or min(durations, default=0) < 8 or sum(durations) > MAX_CYCLE_MS:
        raise ValueError(f'{source}: use animação com 2+ quadros, durações >=8 ms e ciclo <=10 s')
    return frames, durations


def save_sticker(target, frames, durations):
    # Quadros completos evitam a otimização de deltas tornar o fundo opaco
    # em animações de poucas cores e dispensam acumulação entre poses.
    frames[0].save(target, format='WEBP', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, lossless=True, quality=100,
                   method=6, kmin=1, kmax=1, background=(0, 0, 0, 0))
    if target.stat().st_size > MAX_BYTES:
        raise ValueError(f'{target.name}: excede 500 KB; simplifique a arte sem reduzir os tempos')
    decoded_times = []
    with Image.open(target) as encoded:
        if encoded.size != (512, 512) or encoded.n_frames != len(frames) or encoded.info.get('loop') != 0:
            raise ValueError(f'{target.name}: dimensões, quadros ou loop alterados')
        for index, expected in enumerate(frames):
            encoded.seek(index)
            actual = encoded.convert('RGBA')
            decoded_times.append(encoded.info['duration'])
            if ImageChops.difference(actual.getchannel('A'), expected.getchannel('A')).getbbox():
                raise ValueError(f'{target.name}/{index}: transparência alterada')
            # WebP pode descartar RGB de pixels invisíveis; compara a imagem visível.
            for color in ('#ffffff', '#182229'):
                actual_bg = Image.new('RGBA', actual.size, color)
                expected_bg = actual_bg.copy()
                actual_bg.alpha_composite(actual)
                expected_bg.alpha_composite(expected)
                if ImageChops.difference(actual_bg.convert('RGB'), expected_bg.convert('RGB')).getbbox():
                    raise ValueError(f'{target.name}/{index}: pixels visíveis alterados')
        if decoded_times != durations:
            raise ValueError(f'{target.name}: tempos alterados')


def export_stickers(path, data, output_dir):
    """Retorna Path do pacote; grava também WebPs, capa e relatório de validação.

    path é a pasta do pet (com animations/). output_dir recebe somente esse pet.
    Nenhum resultado anterior é substituído se a conversão/validação falhar.
    """
    path, output_dir = Path(path), Path(output_dir)
    ident, name = data.get('id', ''), data.get('name', '')
    if not re.fullmatch(r'[a-z][a-z0-9-]*', ident) or not isinstance(name, str) or not name.strip():
        raise ValueError('id e nome do pet inválidos')
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f'{ident}-animado.wastickers'
    with tempfile.TemporaryDirectory(prefix='.stickers-', dir=output_dir) as directory:
        temporary = Path(directory)
        report = []
        for mood in MOODS:
            source = path / 'animations' / f'{mood}.gif'
            frames, durations = sticker_frames(source)
            target = temporary / f'{ident}-{mood}.webp'
            save_sticker(target, frames, durations)
            report.append({'file': target.name, 'bytes': target.stat().st_size,
                           'frames': len(frames), 'duration_ms': sum(durations),
                           'frame_durations_ms': durations, 'size': [512, 512],
                           'lossless': True, 'decoded_pixels_verified': True,
                           'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
            if mood == 'happy':
                frames[0].resize((96, 96), Image.Resampling.LANCZOS).save(temporary / 'cover.png')
        (temporary / 'validacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        with zipfile.ZipFile(temporary / archive_name, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('title.txt', f'{name} animado\n'.encode('utf-8'))
            archive.writestr('author.txt', b'ViraLabs\n')
            archive.write(temporary / 'cover.png', 'cover.png')
            for mood in MOODS:
                filename = f'{ident}-{mood}.webp'
                archive.write(temporary / filename, filename)
        with zipfile.ZipFile(temporary / archive_name) as archive:
            if archive.testzip() is not None or len(archive.namelist()) != 7:
                raise ValueError('Pacote incompleto ou corrompido')
        for source in temporary.iterdir():
            source.replace(output_dir / source.name)
    return output_dir / archive_name
