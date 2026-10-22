"""Generate the exact same scalable logo for Windows Setup, EXE, and the UI."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent/'src'))
from branding import write_icon, logo_png
from version import VERSION

directory = Path(__file__).parent/'assets'
directory.mkdir(exist_ok=True)
write_icon(directory/'app.ico')
(directory/'logo.png').write_bytes(logo_png(256))
major, minor = map(int, VERSION.split('.'))
(directory/'version_info.txt').write_text(f'''VSVersionInfo(
  ffi=FixedFileInfo(filevers=({major}, {minor}, 0, 0), prodvers=({major}, {minor}, 0, 0),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'Eizat'),
    StringStruct('FileDescription', 'Eizat Offline Translator'),
    StringStruct('FileVersion', '{VERSION}'),
    StringStruct('ProductName', 'Engineering Document Translator'),
    StringStruct('ProductVersion', '{VERSION}'),
    StringStruct('LegalCopyright', 'Created by Eizat. GNU AGPL v3.')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])])
''', encoding='utf-8')
print('Generated app icon and Eizat version metadata')
