"""Builder only: download official Argos language-model archives."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
from urllib.parse import urlparse
import zipfile

root = Path(__file__).resolve().parent
models = root / 'src' / 'models'
models.mkdir(exist_ok=True)
index = json.load(urllib.request.urlopen('https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json', timeout=90))
manifest = []
for language, target_code in [('fr','en'),('nl','en'),('de','en'),('en','fr'),('en','nl'),('en','de')]:
    key = language if target_code == 'en' else language + '-' + target_code
    package = next(x for x in index if x['from_code'] == language and x['to_code'] == target_code)
    archive = models / (key + '.argosmodel')
    last = None
    links = list(package['links'])
    for link in package['links']:
        filename = Path(urlparse(link).path).name
        mirror = 'https://data.argosopentech.com/argospm/v1/' + filename
        if mirror not in links:
            links.append(mirror)
    for link in links:
        try:
            print(f'Downloading {language} to {target_code} model from official index...', flush=True)
            request = urllib.request.Request(link, headers={'User-Agent':'EngineeringPDFTranslator/1.0'})
            with urllib.request.urlopen(request, timeout=180) as response, archive.open('wb') as output:
                while chunk := response.read(1024*1024):
                    output.write(chunk)
            last = None
            break
        except Exception as exc:
            print(f'Download failed: {exc}; trying next publisher link.', flush=True)
            last = exc
    if last:
        raise RuntimeError(f'Model download failed for {language}: {last}')
    target = models / key
    target.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            dest = (target / entry.filename).resolve()
            if target.resolve() not in dest.parents and dest != target.resolve():
                raise ValueError('Unsafe path in model archive')
        z.extractall(target)
    manifest.append({'from':language,'to':target_code,'version':package.get('package_version'),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'download_url':link,'links':links})
    archive.unlink()
(models/'build-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
sys.path.insert(0,str(root/'src'))
from offline import OfflineTranslator
for language, sample in (('fr','Bonjour le monde'),('nl','Goedemorgen'),('de','Guten Morgen')):
    output = OfflineTranslator(language)(sample)
    expected = 'hello' if language == 'fr' else 'morning'
    if expected not in output.lower() or '\u2581' in output:
        raise RuntimeError(f'{language} translation smoke check failed')
    print(f'{language} inference smoke check: {output}',flush=True)

from offline import RawTranslator
for target, word in [('fr','chat'),('nl','kat'),('de','katze')]:
    output = RawTranslator('en',target)('The cat sleeps on the sofa.')
    if word not in output.casefold():
        raise RuntimeError(f'English to {target} inference check failed: {output}')
    print(f'en to {target} inference smoke check: {output}',flush=True)
