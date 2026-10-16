"""Entrega validada de um único pet sem reexportar os modelos da galeria."""
from pathlib import Path
import shutil
import tempfile

from .catalog import validate_animations
from .gallery import gallery
from .gifs import export_gifs
from .stickers import export_stickers


def deliver(path, data, all_pets, output):
    # A validação de GIF/WebP/HTML acontece antes de trocar a entrega anterior.
    output = Path(output)
    with tempfile.TemporaryDirectory(prefix='.delivery-', dir=path.parent) as folder:
        temporary = Path(folder)
        shutil.copytree(path/'sprites', temporary/'sprites')
        export_gifs(temporary, data)
        validate_animations(temporary, data)
        export_stickers(temporary, data, temporary/'stickers')
        complete = [(temporary if p == path else p, d) for p, d in all_pets
                    if p == path or all((p/'animations'/f'{m}.gif').exists()
                                       for m in ('happy', 'barking', 'waiting', 'sleeping'))]
        html = gallery(complete, featured=data['id'])
        output.parent.mkdir(parents=True, exist_ok=True)
        for name in ('animations', 'stickers'):
            (path/name).mkdir(exist_ok=True)
            for source in (temporary/name).iterdir():
                source.replace(path/name/source.name)
        output.write_text(html)
    return output
