"""Discovery and validation: one manifest per pet, no pet-specific Python code."""
import json
import re
from pathlib import Path

from PIL import Image, ImageSequence
from .raster import ROOT, MOODS

PET_ROOT = ROOT / 'assets/pets'


def load_pet(path):
    data = json.loads((path / 'pet.json').read_text())
    ident = data.get('id', '')
    if not re.fullmatch(r'[a-z][a-z0-9-]*', ident) or ident != path.name:
        raise ValueError(f'{path}: id inválido ou diferente da pasta')
    if not isinstance(data.get('name'), str) or not data['name'].strip():
        raise ValueError(f'{ident}: name obrigatório')
    if data.get('status') not in ('ready', 'draft'):
        raise ValueError(f'{ident}: status deve ser ready ou draft')
    if 'author' in data and (not isinstance(data['author'], str) or not data['author'].strip()):
        raise ValueError(f'{ident}: author precisa ser texto não vazio')
    effects = data.get('effects', {})
    allowed = {'happy': 'sparkles', 'barking': 'bark'}
    if not isinstance(effects, dict) or any(k not in allowed or allowed[k] != v for k, v in effects.items()):
        raise ValueError(f'{ident}: effects aceita happy=sparkles e barking=bark')
    rendering = data.get('rendering', {})
    if not isinstance(rendering, dict) or set(rendering) - {'profile', 'sizes'} or rendering.get('profile', 'outlined') not in ('outlined', 'detailed'):
        raise ValueError(f'{ident}: rendering aceita profile outlined/detailed e sizes')
    sizes = rendering.get('sizes', [8, 16, 24, 32, 40, 48])
    if (not isinstance(sizes, list) or not sizes
        or any(type(n) is not int or n < 8 or n > 48 or n % 2 for n in sizes)
        or sizes != sorted(set(sizes)) or sizes[-1] != 48):
        raise ValueError(f'{ident}: sizes exige tamanhos pares ordenados de 8 a 48, terminando em 48')
    for mood in MOODS:
        times = data.get('timings', {}).get(mood)
        if not isinstance(times, list) or not times or any(type(t) is not int or t < 20 for t in times):
            raise ValueError(f'{ident}/{mood}: timings deve conter durações >= 20 ms')
    signs = data.get('sleepSigns')
    if not isinstance(signs, list) or len(signs) != len(data['timings']['sleeping']):
        raise ValueError(f'{ident}: sleepSigns precisa acompanhar todos os quadros sleeping')
    for sign in signs:
        if sign is not None and (not isinstance(sign, list) or len(sign) != 3
             or not isinstance(sign[0], str) or not 1 <= len(sign[0]) <= 3
             or any(c not in 'zZ' for c in sign[0]) or type(sign[1]) is not int
             or sign[2] not in (0, 1)):
            raise ValueError(f'{ident}: sinal de sono inválido: {sign}')
    return data


def pets(root=PET_ROOT):
    return [(p, load_pet(p)) for p in sorted(root.iterdir()) if p.is_dir() and (p / 'pet.json').exists()]


def validate_animations(path, data):
    shape = None
    for mood in MOODS:
        source = path / 'animations' / f'{mood}.gif'
        with Image.open(source) as gif:
            if gif.width < 48 or gif.height < gif.width or gif.info.get('loop') != 0:
                raise ValueError(f'{source}: tamanho ou loop inválido')
            if shape is not None and gif.size != shape:
                raise ValueError(f'{source}: os estados precisam ter as mesmas dimensões')
            shape = gif.size
            if gif.n_frames != len(data['timings'][mood]):
                raise ValueError(f'{source}: número de quadros diferente de pet.json')
            for n, frame in enumerate(ImageSequence.Iterator(gif)):
                if frame.info.get('duration', 0) < 20:
                    raise ValueError(f'{source}/{n}: duração inválida')
                alpha = frame.convert('RGBA').getchannel('A')
                if not alpha.getbbox() or alpha.getextrema()[0] != 0:
                    raise ValueError(f'{source}/{n}: quadro vazio ou sem transparência')


def write_runtime_catalog(all_pets):
    lines = ['// Gerado por tools/pets.py build. Não edite à mão.']
    for index, (path, data) in enumerate(all_pets):
        target = ROOT / 'generated/pets' / data['id'] / 'frames.ts'
        if not target.exists():
            raise ValueError(f'{data["id"]}: execute build para gerar os quadros de todos os pets')
        lines.append(f"import * as pet{index} from './pets/{data['id']}/frames'")
    lines.append('export const PETS = {')
    for index, (_, data) in enumerate(all_pets):
        lines.append(f'  {json.dumps(data["id"])}: {{ name: {json.dumps(data["name"])}, status: {json.dumps(data["status"])}, ...pet{index} }},')
    lines.append('} as const')
    (ROOT / 'generated/catalog.ts').write_text('\n'.join(lines) + '\n')
