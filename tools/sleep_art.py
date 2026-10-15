"""Desenho e sequência compartilhados pelo GIF e pelo Raster do terminal."""

SLEEP_SIGNS = (('z', -2, 1), ('zZ', -1, 1), ('ZzZ', 0, 0),
               ('ZzZ', 1, 0), None, None, ('z', -2, 1), ('Zz', -1, 1))
GLYPHS = {
    'Z': ('111', '001', '010', '100', '111'),
    'z': ('000', '000', '111', '010', '111'),
}
SLEEP_COLOR = '#cdb7f6'
