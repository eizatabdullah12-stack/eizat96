"""Whole-sentence offline translation and a four-language everyday phrasebook.

The phrasebook supplies reviewed equivalents, not model training or a claim of
unlimited grammar correction. Unlisted sentences use the bundled neural models.
"""
import csv
import re
import unicodedata
from pathlib import Path

from directional import DirectionalTranslator
from glossary import BRANDS

LANGS = ('en', 'fr', 'nl', 'de')


def key(value):
    normalized = unicodedata.normalize('NFKC', value).casefold().translate(
        str.maketrans({'’': "'", 'ʼ': "'", '‘': "'"}))
    return re.sub(r'\s+', ' ', normalized.strip(' \t\r\n.!?,:;…')).strip()


def load_phrases():
    with Path(__file__).with_name('conversation.psv').open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='|')
        if reader.fieldnames != ['category', *LANGS]:
            raise ValueError('Invalid conversation phrasebook header')
        rows = list(reader)
    index = {}
    for row in rows:
        if None in row or any(not row.get(c) for c in ('category', *LANGS)):
            raise ValueError('Incomplete conversation phrasebook row')
        for language in LANGS:
            for alias in row[language].split(';'):
                if not key(alias):
                    raise ValueError('Empty conversation alias')
                index.setdefault(key(alias), []).append((language, row))
    return rows, index


PHRASES, INDEX = load_phrases()


def normalize_input(value, language):
    """Only unambiguous common chat spellings/agreement errors; retain case."""
    replacements = {
        'en': [(r'\bi is\b', 'I am'), (r'\bi are\b', 'I am'),
               (r'\byou is\b', 'you are'), (r'\bwe is\b', 'we are'),
               (r'\bthey is\b', 'they are'), (r'\bhe are\b', 'he is'),
               (r'\bshe are\b', 'she is'), (r'\bim\b', "I'm"),
               (r'\bdont\b', "don't"), (r'\bcant\b', "can't"),
               (r'\bwont\b', "won't"), (r'\bdoesnt\b', "doesn't"),
               (r'\bi\b', 'I')],
        'fr': [(r'\bj ai\b', "j'ai"), (r'\bj aime\b', "j'aime"),
               (r'\bc est\b', "c'est")],
        'nl': [(r'\bik bent\b', 'ik ben'), (r'\bwij is\b', 'wij zijn'),
               (r'\bwe is\b', 'we zijn')],
        'de': [(r'\bich ist\b', 'ich bin'), (r'\bwir ist\b', 'wir sind'),
               (r'\bdu ist\b', 'du bist')],
    }
    for pattern, replacement in replacements.get(language, []):
        value = re.sub(pattern, replacement, value, flags=re.I)
    return value


def equivalent(value, source, target):
    rows = [row for language, row in INDEX.get(key(value), []) if language == source]
    outputs = {row[target].split(';')[0] for row in rows}
    # Bonjour is both "hello" and "good morning". Prefer the general greeting
    # instead of loading a neural model for an otherwise recorded greeting.
    if len(outputs) > 1 and all(row['category'] == 'Greetings' for row in rows):
        outputs = {rows[0][target].split(';')[0]}
    if len(outputs) != 1:
        return None
    result = outputs.pop()
    # Retain indentation, terminal punctuation, and deliberate all-caps speech.
    left = value[:len(value)-len(value.lstrip())]
    right = value[len(value.rstrip()):]
    ending = re.search(r'[.!?…]+$', value.strip())
    result = result.rstrip('.!?…') + (ending.group() if ending else '')
    if value.strip().isupper():
        result = result.upper()
    return left + result + right


class ConversationTranslator(DirectionalTranslator):
    """Use sentence context, without splitting around individual glossary words."""
    def __init__(self, source='auto', target='en', raw_factory=None):
        super().__init__(source, target)
        if raw_factory is None:
            from offline import RawTranslator
            raw_factory = RawTranslator
        self.raw_factory = raw_factory
        self.raw_models = {}
        self.terms.update({k: k for k in INDEX})
        self.brand_pattern = re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(name) for name in sorted((*BRANDS, 'Eizat'), key=len, reverse=True))+r')(?!\w)', re.I)

    def extra_protected_spans(self, value):
        return [(match.start(), match.end()) for match in self.brand_pattern.finditer(value)]

    def _detect(self, value, hint=None):
        if self.language != 'auto':
            return self.language, ''
        candidates = INDEX.get(key(value), [])
        languages = {language for language, row in candidates}
        if len(languages) == 1:
            return next(iter(languages)), ''
        if candidates:
            meanings = {key(row['en'].split(';')[0]) for language, row in candidates}
            if len(meanings) == 1:
                return hint if hint in languages else sorted(languages)[0], ''
            return 'und', 'This short word has different meanings in multiple languages. Choose the source language.'
        # Chat spellings can be recognized without guessing a language first.
        for code in LANGS:
            normalized = normalize_input(value, code)
            if normalized != value and equivalent(normalized, code, 'en') is not None:
                return code, ''
        return super()._detect(value, hint)

    def raw(self, source, target, value):
        pair = source, target
        if pair not in self.raw_models:
            self.raw_models[pair] = self.raw_factory(source, target)
        return self.raw_models[pair](value)

    def translate_segment(self, language, segment):
        if language == 'und':
            return segment
        normalized = normalize_input(segment, language)
        phrase = equivalent(normalized, language, self.target_language)
        if phrase is not None:
            return phrase
        if language == self.target_language:
            return normalized
        english = normalized if language == 'en' else self.raw(language, 'en', normalized)
        return english if self.target_language == 'en' else self.raw('en', self.target_language, english)

    def review_notes(self, text):
        return list(dict.fromkeys(reason for segment, language, reason in self._selected(text) if reason))
