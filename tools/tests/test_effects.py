"""Efeitos precisam aparecer no terminal, preservar o pet e limpar entre pulsos."""
import unittest
from PIL import Image, ImageChops
from virapets.raster import ROOT, reduce_sprite
from virapets.gifs import compose, indexed_frames
from virapets.effects import GOLD


class EffectsTest(unittest.TestCase):
    def test_effects_preserve_pet_and_margins_and_survive_terminal_reduction(self):
        for pet in ('mel', 'dara'):
            for mood, effect, active in [('happy', 'sparkles', {2, 4, 5}), ('barking', 'bark', {2, 4})]:
                with Image.open(ROOT/f'assets/pets/{pet}/sprites/{mood}.png') as source:
                    strip = source.convert('RGBA')
                original, headroom = compose(strip, mood)
                result, _ = compose(strip, mood, effects={mood: effect})
                for i, (before, after) in enumerate(zip(original, result)):
                    changed = ImageChops.difference(before, after).getchannel('A')
                    self.assertEqual(changed.getbbox() is not None, i in active)
                    self.assertIsNone(ImageChops.multiply(changed, before.getchannel('A')).getbbox())
                    self.assertIsNone(ImageChops.difference(before, after).convert('RGB').getbbox() if i not in active else None)
                    self.assertEqual(after.getchannel('A').crop((after.width-4,0,after.width,after.height)).getbbox(), None)
                    if i in active:
                        tile = after.crop((0,headroom,strip.height,after.height))
                        small = reduce_sprite(tile,48)
                        self.assertTrue(any(a and r>180 and g>140 and b<120 for r,g,b,a in small.get_flattened_data()))

    def test_gold_is_not_quantized_to_fur_color(self):
        with Image.open(ROOT/'assets/pets/mel/sprites/happy.png') as source:
            frames, _ = compose(source.convert('RGBA'), 'happy', effects={'happy':'sparkles'})
        encoded = indexed_frames(frames)
        for i, frame in enumerate(encoded):
            colors = {p[:3] for p in frame.convert('RGBA').get_flattened_data() if p[3]}
            self.assertEqual(GOLD in colors, i in {2,4,5})
