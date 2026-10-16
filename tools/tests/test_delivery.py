"""Executa o fluxo de um novo pet e verifica downloads reais, ordem e preservação."""
import base64
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image, ImageDraw
import pets as cli
from virapets import catalog
from virapets.gifs import export_gifs
from virapets.raster import MOODS, ROOT


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.order, self.downloads, self.images = [], {}, []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section': self.order.append(attrs['data-pet'])
        if tag == 'img': self.images.append(attrs['src'])
        if tag == 'a' and 'download' in attrs:
            self.downloads[attrs['download']] = base64.b64decode(attrs['href'].split(',', 1)[1])


def digest(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class DeliveryTest(unittest.TestCase):
    def test_new_pet_delivery_preserves_models_and_embeds_valid_downloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pet_root = root/'assets/pets'
            # Modelos reais são incorporados, sem nova conversão ou mudança de pixels.
            for ident in ('jojo', 'mel', 'dara'):
                source = ROOT/'assets/pets'/ident
                target = pet_root/ident
                target.mkdir(parents=True)
                shutil.copy2(source/'pet.json', target/'pet.json')
                shutil.copytree(source/'animations', target/'animations')
                shutil.copytree(source/'stickers', target/'stickers')
            before = digest(pet_root)
            def command(*args):
                with patch.object(cli, 'PET_ROOT', pet_root), patch.object(cli, 'ROOT', root), patch.object(catalog, 'ROOT', root), \
                     patch.object(cli, 'pets', lambda: catalog.pets(pet_root)), \
                     patch('sys.argv', ['pets.py', *args]):
                    cli.main()
            command('new', '--pet', 'teste', '--name', 'Teste <Pet>', '--author', 'Autor do teste')
            pet = pet_root/'teste'
            for mood in MOODS:
                strip = Image.new('RGBA', (8*64, 64))
                draw = ImageDraw.Draw(strip)
                for i in range(8):
                    draw.ellipse((i*64+16, 25+i%3, i*64+46, 58), fill=(170+i*8, 100, 55, 255), outline='black', width=2)
                strip.save(pet/'sprites'/f'{mood}.png')
            out = root/'outputs/teste/animation-teste.html'
            command('deliver', '--pet', 'teste', '--output', str(out))
            command('validate', '--pet', 'teste')
            page = Page(out.read_text())
            self.assertEqual(page.order, ['teste', 'jojo', 'mel', 'dara'])
            self.assertEqual(len(page.images), 16)
            self.assertIn('Teste &lt;Pet&gt;', out.read_text())
            for ident in page.order:
                with zipfile.ZipFile(io.BytesIO(page.downloads[f'{ident}-gifs.zip'])) as archive:
                    self.assertEqual(set(archive.namelist()), {f'{ident}-{m}.gif' for m in MOODS})
                    for mood in MOODS:
                        raw = (pet_root/ident/'animations'/f'{mood}.gif').read_bytes()
                        self.assertEqual(raw, archive.read(f'{ident}-{mood}.gif'))
                        self.assertEqual(raw, page.downloads[f'{ident}-{mood}.gif'])
                self.assertEqual(page.downloads[f'{ident}-animado.wastickers'],
                    (pet_root/ident/'stickers'/f'{ident}-animado.wastickers').read_bytes())
            with zipfile.ZipFile(pet/'stickers/teste-animado.wastickers') as pack:
                self.assertEqual(pack.read('author.txt'), b'Autor do teste\n')
                self.assertEqual(len(pack.namelist()), 7)
            after = digest(pet_root)
            for name, value in before.items(): self.assertEqual(after[name], value, name)
            # A segunda execução precisa de intenção explícita de substituir o pacote.
            saved = out.read_bytes()
            with self.assertRaises(SystemExit): command('deliver', '--pet', 'teste', '--output', str(out))
            self.assertEqual(saved, out.read_bytes())
            # Falha posterior na conversão de figurinhas também preserva GIFs/HTML.
            old_delivery = digest(pet/'animations')
            with patch('virapets.stickers.MAX_BYTES', 1):
                with self.assertRaisesRegex(ValueError, '500 KB'):
                    command('deliver', '--pet', 'teste', '--force', '--output', str(out))
            self.assertEqual(old_delivery, digest(pet/'animations'))
            self.assertEqual(saved, out.read_bytes())
            # O mesmo pet entra no catálogo do painel sem edição manual de hooks.
            command('build', '--pet', 'teste', '--featured', 'teste', '--output', str(out))
            self.assertTrue((root/'generated/pets/teste/frames.ts').exists())
            self.assertIn('"teste"', (root/'generated/catalog.ts').read_text())
            # Entrada opaca falha antes de sobrescrever qualquer GIF aprovado.
            old_gifs = digest(pet/'animations')
            Image.new('RGB', (512, 64), 'white').save(pet/'sprites/sleeping.png')
            with self.assertRaisesRegex(ValueError, 'transparência'):
                export_gifs(pet, catalog.load_pet(pet))
            self.assertEqual(old_gifs, digest(pet/'animations'))

    def test_featured_must_exist(self):
        from virapets.gallery import gallery
        with self.assertRaisesRegex(ValueError, 'ausente'):
            gallery([], featured='missing')


if __name__ == '__main__':
    unittest.main()
