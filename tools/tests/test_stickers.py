"""Valida composição e tempos das figurinhas e o formato do pacote importável."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image, ImageDraw, ImageSequence
from virapets.raster import MOODS
from virapets.stickers import export_stickers, sticker_frames


class StickersTest(unittest.TestCase):
    def sources(self, root, duration=(100, 240, 300)):
        animation = root / 'animations'
        animation.mkdir()
        for mood in MOODS:
            frames = []
            for index in range(3):
                frame = Image.new('RGBA', (64, 80))
                draw = ImageDraw.Draw(frame)
                draw.rectangle((12, 30, 50, 70), fill=(160 + 20 * index, 90, 45, 255))
                if mood == 'sleeping' and index != 1:
                    draw.rectangle((40 + index * 2, 8, 45 + index * 2, 12), fill=(205, 183, 246, 255))
                frames.append(frame)
            frames[0].save(animation / f'{mood}.gif', save_all=True, append_images=frames[1:],
                           duration=list(duration), loop=0, disposal=2)

    def test_pack_has_four_animated_stickers_and_matches_pixels_timing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.sources(root)
            out = root / 'stickers'
            result = export_stickers(root, {'id': 'example', 'name': 'Exemplo'}, out)
            report = json.loads((out / 'validacao.json').read_text())
            self.assertEqual(len(report), 4)
            self.assertTrue(all(item['bytes'] <= 500_000 and item['decoded_pixels_verified'] for item in report))
            with zipfile.ZipFile(result) as pack:
                self.assertEqual(set(pack.namelist()), {'title.txt', 'author.txt', 'cover.png', *[f'example-{m}.webp' for m in MOODS]})
                self.assertEqual(pack.read('title.txt'), b'Exemplo animado\n')
                with Image.open(io.BytesIO(pack.read('cover.png'))) as cover:
                    self.assertEqual(cover.size, (96, 96))
                for mood in MOODS:
                    with Image.open(io.BytesIO(pack.read(f'example-{mood}.webp'))) as webp:
                        self.assertEqual(webp.size, (512, 512))
                        frames = [frame.convert('RGBA') for frame in ImageSequence.Iterator(webp)]
                        times = []
                        signs = []
                        for index in range(webp.n_frames):
                            webp.seek(index)
                            webp.load()
                            times.append(webp.info['duration'])
                            pixels = frames[index].get_flattened_data() if hasattr(frames[index], 'get_flattened_data') else frames[index].getdata()
                            signs.append(any(p[:3] == (205, 183, 246) and p[3] for p in pixels))
                        self.assertEqual(times, [100, 240, 300])
                        self.assertEqual(signs, [True, False, True] if mood == 'sleeping' else [False] * 3)

    def test_failed_export_preserves_existing_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.sources(root)
            out = root / 'stickers'
            out.mkdir()
            existing = out / 'example-animado.wastickers'
            existing.write_bytes(b'previous-approved-pack')
            with patch('virapets.stickers.MAX_BYTES', 1):
                with self.assertRaisesRegex(ValueError, '500 KB'):
                    export_stickers(root, {'id': 'example', 'name': 'Example'}, out)
            self.assertEqual(existing.read_bytes(), b'previous-approved-pack')
            self.assertEqual(list(out.iterdir()), [existing])

    def test_rejects_animation_over_ten_seconds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.sources(root, duration=(5000, 5000, 100))
            with self.assertRaisesRegex(ValueError, '<=10 s'):
                sticker_frames(root / 'animations/sleeping.gif')


if __name__ == '__main__':
    unittest.main()
