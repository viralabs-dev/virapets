#!/usr/bin/env python3
"""ViraPets: list, validate, gifs, build, gallery, stickers e new. Requer Pillow."""
import argparse
import json
import re
from pathlib import Path
from PIL import Image

from virapets.catalog import PET_ROOT, pets, validate_animations, write_runtime_catalog
from virapets.frames import build
from virapets.gallery import gallery
from virapets.gifs import TIMINGS, compose, timings, indexed_frames, save_and_verify
from virapets.raster import ROOT, MOODS
from virapets.sleep import SLEEP_SIGNS
from virapets.stickers import export_stickers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('list', 'validate', 'gifs', 'build', 'gallery', 'stickers', 'new'))
    parser.add_argument('--pet', help='id do pet; omitido processa todos os pets completos (validate inclui incompletos)')
    parser.add_argument('--name', help='nome de exibição para new')
    parser.add_argument('--output', type=Path, default=ROOT/'assets/animation-virapets.html', help='destino da galeria')
    parser.add_argument('--force', action='store_true', help='reexporta um pacote de figurinhas existente')
    args = parser.parse_args()
    if args.command == 'new':
        if not args.pet or not re.fullmatch(r'[a-z][a-z0-9-]*', args.pet) or not args.name:
            parser.error('new exige --pet id-em-minusculas e --name Nome')
        path = PET_ROOT / args.pet
        if path.exists():
            parser.error(f'{args.pet} já existe; nenhum arquivo alterado')
        path.mkdir(parents=True)
        for folder in ('sprites', 'animations', 'references'):
            (path/folder).mkdir()
        (path/'pet.json').write_text(json.dumps({'id':args.pet,'name':args.name,'description':'','status':'draft','timings':TIMINGS,'sleepSigns':SLEEP_SIGNS},ensure_ascii=False,indent=2)+'\n')
        print(f'{path}: adicione as quatro faixas PNG e execute gifs --pet {args.pet}, depois build')
        return
    all_pets = pets()
    selected = [(p,d) for p,d in all_pets if args.pet is None or d['id'] == args.pet]
    if not selected:
        parser.error('pet desconhecido; use list')
    if args.command == 'list':
        for _, data in selected:
            print(f'{data["id"]}: {data["name"]} ({data["status"]})')
        return
    if args.command == 'stickers':
        for path, data in selected:
            destination = path/'stickers'
            package = destination/f'{data["id"]}-animado.wastickers'
            if package.exists() and not args.force:
                print(f'{package}: preservado; use --force para reexportar')
            else:
                validate_animations(path, data)
                print(export_stickers(path, data, destination))
        return
    if args.command == 'gifs':
        for path, data in selected:
            manifest = {'loop':0,'transparent':True,'gifTimeResolutionMs':10,'animations':{}}
            destination = path/'animations'
            destination.mkdir(exist_ok=True)
            for mood in MOODS:
                with Image.open(path/'sprites'/f'{mood}.png') as source:
                    frames, headroom = compose(source.convert('RGBA'), mood, data['sleepSigns'])
                original, rounded = timings(mood, len(frames), data['timings'])
                save_and_verify(destination/f'{mood}.gif', indexed_frames(frames), rounded)
                manifest['animations'][mood] = {'file':f'{mood}.gif','width':frames[0].width,'height':frames[0].height,'frameCount':len(frames),'headroomPixels':headroom,'sourceDurationsMs':original,'durationsMs':rounded,'cycleMs':sum(rounded)}
            (destination/'animations.json').write_text(json.dumps(manifest,indent=2)+'\n')
            print(f'{data["id"]}: GIFs exportados e decodificados sem rastros')
    if args.command in ('build', 'gallery') and args.pet is None:
        selected = [(p, d) for p, d in selected if d['status'] != 'draft' or all((p/'animations'/f'{m}.gif').exists() for m in MOODS)]
    for path, data in selected:
        validate_animations(path,data)
        if args.command == 'build':
            build(path/'animations', ROOT/'generated/pets'/data['id']/'frames.ts', sleep_signs=data['sleepSigns'])
        print(f'{data["id"]}: validado')
    if args.command == 'build':
        runtime_pets = [(p, d) for p, d in all_pets if (ROOT/'generated/pets'/d['id']/'frames.ts').exists()]
        write_runtime_catalog(runtime_pets)
    if args.command in ('gallery','build'):
        args.output.parent.mkdir(parents=True,exist_ok=True)
        complete_pets = [(p, d) for p, d in all_pets if all((p/'animations'/f'{m}.gif').exists() for m in MOODS)]
        gallery_pets = [(p, d) for p, d in complete_pets if args.command != 'gallery' or args.pet is None or d['id'] == args.pet]
        args.output.write_text(gallery(gallery_pets))
        print(args.output)


if __name__ == '__main__':
    main()
