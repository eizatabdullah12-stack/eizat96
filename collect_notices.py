"""Builder only: retain notices from the installed dependency distributions."""
import importlib.metadata
from pathlib import Path
import shutil
import sys

target = Path(__file__).resolve().parent / 'licenses'
target.mkdir(exist_ok=True)
for distribution in importlib.metadata.distributions():
    name = distribution.metadata.get('Name', 'unknown')
    for entry in distribution.files or ():
        if any(word in str(entry).lower() for word in ('license', 'copying', 'notice')):
            source = Path(distribution.locate_file(entry))
            if source.is_file() and source.suffix.lower() not in ('.py', '.pyc', '.pyd'):
                destination = target / name / Path(str(entry))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
for name in ('LICENSE.txt', 'LICENSE'):
    source = Path(sys.base_prefix) / name
    if source.is_file():
        shutil.copyfile(source, target / ('Python-' + name))
