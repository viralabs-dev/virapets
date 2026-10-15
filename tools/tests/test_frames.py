"""Verificações do redimensionamento e dos pixels do sono. PYTHONPATH=tools python3 -m unittest discover -s tools/tests"""
import base64
import struct
import unittest

from PIL import Image, ImageSequence
from virapets.frames import cells, DEFAULT
from virapets.raster import MOODS, ROOT, durations, extract, gif_frames, reduce_sprite
from virapets.sleep import SLEEP_COLOR
from virapets.catalog import pets, validate_animations


def decode(encoded):
    data = base64.b64decode(encoded)
    words = struct.unpack('<' + 'I' * (len(data) // 4), data)
    pixels = []
    for ch, fg, bg in zip(words[::3], words[1::3], words[2::3]):
        assert ch in (32, 0x2580, 0x2584), 'ZzZ deve usar pixels, nunca letras da fonte'
        pixels.append((fg, bg) if ch == 0x2580 else (bg, fg) if ch == 0x2584 else (bg, bg))
    return pixels


class FramesTest(unittest.TestCase):
    def test_contorno_fino_nao_desaparece_na_reducao(self):
        source = Image.new('RGBA', (64, 64))
        for y in range(8, 56):
            for x in range(10, 54):
                source.putpixel((x, y), (0, 0, 0, 255) if x == 10 else (210, 130, 70, 255))
        nearest = source.resize((8, 8), Image.Resampling.NEAREST)
        reduced = reduce_sprite(source, 8)
        self.assertGreater(nearest.getpixel((1, 3))[0], 100)
        self.assertLess(max(reduced.getpixel((1, 3))[:3]), 20)
        self.assertEqual(reduced.getpixel((0, 3))[3], 0)

    def test_sono_bitmap_sem_sobrepor_cao_ou_deixar_rastros(self):
        for path, data in pets():
            for size in (8, 16, 24, 32, 40, 48):
                for i, grid in enumerate(extract(path / 'animations', size, preserve_edges=True)['sleeping']):
                    dog = decode(cells(grid))
                    composed = decode(cells(grid, 'sleeping', i, data['sleepSigns']))
                    changed = 0
                    for original, actual in zip(dog, composed):
                        for a, b in zip(original, actual):
                            if a != b:
                                self.assertEqual(a, DEFAULT, (size, i, 'sobreposição'))
                                self.assertEqual(b, 0xcdb7f6)
                                changed += 1
                    self.assertEqual(changed > 0, data['sleepSigns'][i] is not None, (size, i))
    def test_todos_pets_possuem_quatro_gifs_validos(self):
        for path, data in pets():
            validate_animations(path, data)

    def test_tempos_vem_de_cada_quadro_do_gif(self):
        for mood, times in durations(ROOT / 'assets/pets/jojo/animations').items():
            with Image.open(ROOT / 'assets/pets/jojo/animations' / f'{mood}.gif') as gif:
                self.assertEqual(times, [f.info['duration'] for f in ImageSequence.Iterator(gif)])
            self.assertEqual(len(times), len(gif_frames(ROOT / 'assets/pets/jojo/animations' / f'{mood}.gif')))

    def test_zzz_do_gif_tem_a_cor_exata_e_o_pelo_nunca_a_usa(self):
        zzz = tuple(int(SLEEP_COLOR[i:i + 2], 16) for i in (1, 3, 5))
        for mood in MOODS:
            with Image.open(ROOT / 'assets/pets/jojo/animations' / f'{mood}.gif') as gif:
                found = sum(1 for f in ImageSequence.Iterator(gif)
                            for p in f.convert('RGBA').get_flattened_data() if p[3] and p[:3] == zzz)
            self.assertEqual(found > 0, mood == 'sleeping', mood)
            for tile in gif_frames(ROOT / 'assets/pets/jojo/animations' / f'{mood}.gif'):
                self.assertNotIn(zzz, [p[:3] for p in tile.get_flattened_data() if p[3]], mood)


if __name__ == '__main__':
    unittest.main()
