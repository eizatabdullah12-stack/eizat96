"""User-approved terminology, persisted outside the installation directory."""
import json
import os
from pathlib import Path
import re
import tempfile
import shutil
from datetime import datetime
from glossary import fold

LANGUAGES = ('en', 'fr', 'nl', 'de')
SCOPES = ('engineering', 'conversation', 'both')
MAX_BYTES = 8 * 1024 * 1024


def default_path():
    override = os.environ.get('EIZAT_GLOSSARY_PATH')
    if override:
        return Path(override)
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local' / 'share'))) / 'EngineeringDocumentTranslator' / 'personal-glossary.json'


def normalized(value):
    return re.sub(r'\s+', ' ', fold(value)).strip()


def entry_key(row):
    return row['source'], row['target'], row['scope'], normalized(row['term'])


def validate(data):
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Invalid personal glossary format (expected version 1).')
    if len(data['entries']) > 10000:
        raise ValueError('Personal glossary exceeds 10,000 entries.')
    rows, seen = [], set()
    for item in data['entries']:
        if not isinstance(item, dict):
            raise ValueError('Invalid glossary entry.')
        row = {key: item.get(key, '') for key in ('source', 'target', 'scope', 'term', 'translation', 'context', 'url')}
        if (row['source'] not in LANGUAGES or row['target'] not in LANGUAGES or
                row['source'] == row['target'] or row['scope'] not in SCOPES):
            raise ValueError('Choose two different supported languages and a valid usage mode.')
        for key, limit in [('term', 500), ('translation', 1000), ('context', 1000), ('url', 2000)]:
            if not isinstance(row[key], str) or len(row[key]) > limit or any(ord(c) < 32 and c not in '\t\n\r' for c in row[key]):
                raise ValueError('Glossary field is invalid or too long: ' + key)
            row[key] = re.sub(r'\s+', ' ', row[key]).strip()
        if not any(c.isalpha() for c in row['term']) or not row['translation']:
            raise ValueError('Enter a source term and its translation.')
        if row['url'] and not row['url'].startswith(('https://', 'http://')):
            raise ValueError('Source link must use http or https.')
        key = entry_key(row)
        if key in seen:
            raise ValueError('Duplicate language pair, term and usage mode in glossary.')
        seen.add(key)
        rows.append(row)
    return rows


class PersonalStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_path()

    def read(self, path=None):
        path = Path(path) if path is not None else self.path
        if not path.exists() and path == self.path:
            return []
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('Personal glossary file is too large.')
        try:
            return validate(json.loads(path.read_text(encoding='utf-8-sig')))
        except (ValueError, UnicodeError) as exc:
            raise ValueError('Cannot read glossary. Keep the file and restore a valid backup. ' + str(exc)) from exc

    def write(self, rows, path=None):
        rows = validate({'version': 1, 'entries': rows})
        destination = Path(path) if path is not None else self.path
        payload = json.dumps({'version': 1, 'entries': rows}, ensure_ascii=False, indent=2) + '\n'
        if len(payload.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Personal glossary file is too large.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=destination.parent, delete=False) as f:
                temporary = Path(f.name)
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return rows

    def upsert(self, row, old_key=None):
        row = validate({'version': 1, 'entries': [row]})[0]
        rows = self.read()
        rows = [r for r in rows if entry_key(r) not in (old_key, entry_key(row))]
        rows.append(row)
        self.write(rows)

    def delete(self, key):
        self.write([r for r in self.read() if entry_key(r) != key])

    def export(self, path):
        if Path(path).resolve() == self.path.resolve():
            raise ValueError('Choose a separate backup filename.')
        self.write(self.read(), path)

    def restore_backup(self, path):
        incoming = self.read(path)
        if self.path.exists():
            backup = self.path.with_name(self.path.name + '.unreadable-' + datetime.now().strftime('%Y%m%d%H%M%S%f'))
            shutil.copy2(self.path, backup)
        self.write(incoming)
        return len(incoming)

    def import_backup(self, path):
        # Validate the entire import before changing anything. Existing local
        # corrections win collisions; imports add missing pair/scope/term keys.
        incoming = self.read(path)
        rows = self.read()
        known = {entry_key(r) for r in rows}
        added = [r for r in incoming if entry_key(r) not in known]
        self.write(rows + added)
        return len(added)


class PersonalTranslator:
    """Apply a frozen glossary snapshot before neural/built-in translation.

    Context is a visible reminder, not automatic disambiguation. Mode-specific
    entries beat 'both'. Conflicting auto-source meanings are left to a manual
    source selection instead of guessing which correction to apply.
    """
    def __init__(self, delegate, rows, mode='engineering'):
        self.delegate = delegate
        self.language = delegate.language
        self.target_language = delegate.target_language
        eligible = [r for r in rows if r['target'] == self.target_language and
                    r['scope'] in (mode, 'both') and
                    (self.language == 'auto' or r['source'] == self.language)]
        self.by_term = {}
        for row in sorted(eligible, key=lambda r: r['scope'] != 'both'):
            self.by_term.setdefault(normalized(row['term']), {})[row['source']] = row
        self.terms = dict(delegate.terms)
        self.terms.update({key: next(iter(rows.values()))['translation'] for key, rows in self.by_term.items()})
        patterns = [re.escape(k).replace(r'\ ', r'\s+') for k in sorted(self.by_term, key=len, reverse=True)]
        self.pattern = re.compile(r'(?<!\w)(?:' + '|'.join(patterns) + r')(?!\w)') if patterns else None

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def matches(self, text):
        if not self.pattern:
            return
        value, offsets = [], []
        for index, char in enumerate(text):
            for c in fold(char):
                value.append(c)
                offsets.append(index)
        for match in self.pattern.finditer(''.join(value)):
            a, b = offsets[match.start()], offsets[match.end()-1] + 1
            import unicodedata
            while b < len(text) and unicodedata.combining(text[b]):
                b += 1
            options = self.by_term[normalized(match.group())]
            if self.language == 'auto':
                detected, _ = self.delegate.detect(text)
                if detected == self.target_language:
                    continue
                row = options.get(detected)
                if row is None:
                    if len({r['translation'] for r in options.values()}) != 1:
                        continue
                    row = next(iter(options.values()))
            else:
                row = options[self.language]
            yield a, b, row

    def __call__(self, text):
        result, cursor = [], 0
        for a, b, row in self.matches(text):
            result.append(self.delegate(text[cursor:a]) if any(c.isalpha() for c in text[cursor:a]) else text[cursor:a])
            translation = row['translation']
            if text[a:b].isupper():
                translation = translation.upper()
            elif text[a:b][0].isupper():
                translation = translation[0].upper() + translation[1:]
            result.append(translation)
            cursor = b
        tail = text[cursor:]
        result.append(self.delegate(tail) if any(c.isalpha() for c in tail) else tail)
        return ''.join(result)

    def detect(self, text, hint=None):
        matches = list(self.matches(text))
        if matches and normalized(text) == normalized(text[matches[0][0]:matches[0][1]]):
            return matches[0][2]['source'], ''
        return self.delegate.detect(text, hint)

    def glossary_spans(self, text):
        return sorted(set(self.delegate.glossary_spans(text) + [(a, b) for a,b,_ in self.matches(text)]))

    def glossary_matches(self, text):
        own = list(self.matches(text))
        built = [m for m in self.delegate.glossary_matches(text)
                 if not any(normalized(m['source']) in normalized(text[a:b]) for a,b,_ in own)]
        return built + [{'source': text[a:b], 'english': row['translation']} for a,b,row in own]

    def review_notes(self, text):
        return list(dict.fromkeys(self.delegate.review_notes(text) +
                    [f"{text[a:b]}: {row['context']}" for a,b,row in self.matches(text) if row['context']]))

    def segments(self, text):
        phrases = self.glossary_spans(text)
        cursor = 0
        for boundary in re.finditer(r'(?<=[.!?;])\s+|[\r\n]+', text):
            if any(a < boundary.start() < b for a,b in phrases):
                continue
            if boundary.start() > cursor:
                yield text[cursor:boundary.start()], False
            yield boundary.group(), True
            cursor = boundary.end()
        if cursor < len(text):
            yield text[cursor:], False


def with_personal(delegate, rows=None, mode='engineering'):
    rows = PersonalStore().read() if rows is None else rows
    return PersonalTranslator(delegate, rows, mode) if rows else delegate
