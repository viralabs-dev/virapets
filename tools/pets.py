#!/usr/bin/env python3
"""ViraPets: list, validate, gifs, build, gallery, stickers, deliver e new. Requer Pillow."""
import argparse
import json
import re
from pathlib import Path

from virapets.catalog import PET_ROOT, pets, validate_animations, write_runtime_catalog
from virapets.delivery import deliver
from virapets.frames import build
from virapets.gallery import gallery
from virapets.gifs import TIMINGS, export_gifs
from virapets.raster import ROOT, MOODS
from virapets.sleep import SLEEP_SIGNS
from virapets.stickers import export_stickers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('list', 'validate', 'gifs', 'build', 'gallery', 'stickers', 'deliver', 'new'))
    parser.add_argument('--pet', help='id do pet; omitido processa todos os pets completos (validate inclui incompletos)')
    parser.add_argument('--featured', help='pet em primeiro lugar na galeria, seguido de Jojo, Mel e Dara')
    parser.add_argument('--author', default='Comunidade ViraPets', help='autor do pacote criado por new')
    parser.add_argument('--name', help='nome de exibição para new')
    parser.add_argument('--output', type=Path, default=ROOT/'assets/animation-virapets.html', help='destino da galeria')
    parser.add_argument('--force', action='store_true', help='reexporta um pacote de figurinhas existente')
    args = parser.parse_args()
    if args.command == 'new':
        if not args.pet or not re.fullmatch(r'[a-z][a-z0-9-]*', args.pet) or not args.name or not args.name.strip() or not args.author.strip():
            parser.error('new exige --pet id-em-minusculas, --name Nome e autor não vazio')
        path = PET_ROOT / args.pet
        if path.exists():
            parser.error(f'{args.pet} já existe; nenhum arquivo alterado')
        path.mkdir(parents=True)
        for folder in ('sprites', 'animations', 'references'):
            (path/folder).mkdir()
        (path/'pet.json').write_text(json.dumps({'id':args.pet,'name':args.name,'description':'','author':args.author,'status':'draft','timings':TIMINGS,'sleepSigns':SLEEP_SIGNS},ensure_ascii=False,indent=2)+'\n')
        print(f'{path}: adicione as quatro faixas PNG e execute deliver --pet {args.pet}; build é opcional para o painel')
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
    if args.command == 'deliver':
        if not args.pet:
            parser.error('deliver exige --pet para não reexportar os modelos ViraLabs')
        path, data = selected[0]
        if (path/'stickers'/f'{data["id"]}-animado.wastickers').exists() and not args.force:
            parser.error('pacote existente; use --force para regenerar a entrega deste pet')
        print(deliver(path, data, all_pets, args.output))
        return
    if args.command == 'gifs':
        for path, data in selected:
            export_gifs(path, data)
            print(f'{data["id"]}: GIFs exportados e decodificados sem rastros')
    if args.command in ('build', 'gallery') and args.pet is None:
        selected = [(p, d) for p, d in selected if d['status'] != 'draft' or all((p/'animations'/f'{m}.gif').exists() for m in MOODS)]
    for path, data in selected:
        validate_animations(path,data)
        if args.command == 'build':
            build(path/'animations', ROOT/'generated/pets'/data['id']/'frames.ts', sleep_signs=data['sleepSigns'], rendering=data.get('rendering'))
        print(f'{data["id"]}: validado')
    if args.command == 'build':
        runtime_pets = [(p, d) for p, d in all_pets if (ROOT/'generated/pets'/d['id']/'frames.ts').exists()]
        write_runtime_catalog(runtime_pets)
    if args.command in ('gallery','build'):
        args.output.parent.mkdir(parents=True,exist_ok=True)
        complete_pets = [(p, d) for p, d in all_pets if all((p/'animations'/f'{m}.gif').exists() for m in MOODS)]
        gallery_pets = [(p, d) for p, d in complete_pets if args.command != 'gallery' or args.pet is None or d['id'] == args.pet]
        args.output.write_text(gallery(gallery_pets, featured=args.featured))
        print(args.output)


if __name__ == '__main__':
    main()
