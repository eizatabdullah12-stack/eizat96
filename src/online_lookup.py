"""Optional term-only MyMemory lookup. No requests during offline translation."""
import html
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = 'https://api.mymemory.translated.net/get'
PROVIDER = 'https://mymemory.translated.net/'


def lookup(term, source, target, opener=urlopen):
    if source not in ('en', 'fr', 'nl', 'de') or target not in ('en', 'fr', 'nl', 'de') or source == target:
        raise ValueError('Choose two different supported languages.')
    term = term.strip()
    if not term or len(term.encode('utf-8')) > 500:
        raise ValueError('Online lookup accepts a term of at most 500 UTF-8 bytes.')
    request = Request(API + '?' + urlencode({'q': term, 'langpair': source+'|'+target}),
                      headers={'User-Agent': 'EizatEngineeringTranslator/1.14'})
    with opener(request, timeout=15) as response:
        raw = response.read(1024*1024+1)
    if len(raw) > 1024*1024:
        raise ValueError('Online lookup response is too large.')
    data = json.loads(raw)
    if str(data.get('responseStatus')) != '200' or data.get('quotaFinished'):
        raise ValueError(str(data.get('responseDetails') or 'Online service unavailable or daily limit reached.'))
    candidates = []
    main = data.get('responseData', {}).get('translatedText', '')
    if isinstance(main, str) and main.strip():
        candidates.append(html.unescape(main).strip())
    for match in data.get('matches', []):
        if not isinstance(match, dict):
            continue
        value = match.get('translation', '')
        if isinstance(value, str) and value.strip():
            candidates.append(html.unescape(value).strip())
    result = list(dict.fromkeys(value for value in candidates if len(value) <= 1000))[:8]
    if not result:
        raise ValueError('No online translation found. Enter a translation manually.')
    return result


def search_url(term, source, target, context=''):
    names = {'en': 'English', 'fr': 'French', 'nl': 'Dutch', 'de': 'German'}
    if source not in names or target not in names or not term.strip():
        raise ValueError('Enter a term and choose its languages.')
    return 'https://www.google.com/search?' + urlencode({'q': f'"{term.strip()}" {names[source]} {names[target]} construction translation {context.strip()}'})
