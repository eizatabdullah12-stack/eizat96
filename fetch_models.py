"""Builder only: download official Argos language-model archives."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
import zipfile

root = Path(__file__).resolve().parent
models = root / 'src' / 'models'
models.mkdir(exist_ok=True)
index = json.load(urllib.request.urlopen('https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json', timeout=90))
manifest = []
for language in ('fr','nl'):
    package = next(x for x in index if x['from_code'] == language and x['to_code'] == 'en')
    archive = models / (language + '.argosmodel')
    last = None
    for link in package['links']:
        try:
            print(f'Downloading {language} model from official index...', flush=True)
            with urllib.request.urlopen(link, timeout=180) as response, archive.open('wb') as output:
                while chunk := response.read(1024*1024):
                    output.write(chunk)
            last = None
            break
        except Exception as exc:
            last = exc
    if last:
        raise RuntimeError(f'Model download failed for {language}: {last}')
    target = models / language
    target.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            dest = (target / entry.filename).resolve()
            if target.resolve() not in dest.parents and dest != target.resolve():
                raise ValueError('Unsafe path in model archive')
        z.extractall(target)
    manifest.append({'from':language,'to':'en','version':package.get('package_version'),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'links':package['links']})
    archive.unlink()
(models/'build-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
sys.path.insert(0,str(root/'src'))
from offline import OfflineTranslator
for language, sample in (('fr','Bonjour le monde'),('nl','Goedemorgen')):
    output = OfflineTranslator(language)(sample)
    if not output.strip() or output.strip() == sample:
        raise RuntimeError(f'{language} translation smoke check failed')
    print(f'{language} inference smoke check: {output}',flush=True)
