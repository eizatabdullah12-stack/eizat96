"""Offline per-sentence/label language routing with conservative short-text handling."""
from collections import Counter
import re

from glossary import EngineeringTranslator, TERMS, fold

NAMES = {'fr': 'French', 'nl': 'Dutch', 'de': 'German', 'en': 'English',
         'und': 'Uncertain'}


class AutoTranslator:
    language = 'auto'

    def __init__(self, factory=None):
        if factory is None:
            from offline import OfflineTranslator
            factory = OfflineTranslator
        self.factory = factory
        self.models = {}
        self.glossaries = {language: EngineeringTranslator(language, lambda s:s)
                           for language in ('fr', 'nl', 'de')}
        self.terms = {key:value for g in self.glossaries.values() for key,value in g.terms.items()}
        self.english = {fold(english).strip() for data in TERMS.values()
                        for line in data.strip().splitlines()
                        for source,english in [line.split('|',1)] if fold(source) != fold(english)}
        from langid.langid import LanguageIdentifier, model
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        self.context = None
        self.counts = Counter()
        self.review_count = 0
        self.cache = {}
        self.detection_cache = {}

    def detect(self, text, hint=None):
        key = (text, hint)
        if key not in self.detection_cache:
            if len(self.detection_cache) >= 8192:
                self.detection_cache.clear()
            self.detection_cache[key] = self._detect(text, hint)
        return self.detection_cache[key]

    def _detect(self, text, hint=None):
        clean = text.strip(' \t\r\n.,:;!?()[]')
        normalized = fold(clean)
        letters = sum(c.isalpha() for c in clean)
        if not letters:
            return 'und', 'No language-bearing text.'
        ambiguous = [language for language,g in self.glossaries.items()
                     if normalized in g.ambiguous and normalized in g.terms]
        if len(ambiguous) == 1:
            return ambiguous[0], 'Ambiguous glossary label; check the context review note.'
        if normalized in self.english:
            return 'en', ''
        scores = {}
        for language, glossary in self.glossaries.items():
            spans = glossary.glossary_spans(clean)
            scores[language] = sum(sum(c.isalpha() for c in clean[a:b]) for a,b in spans) / letters
        best = max(scores, key=scores.get)
        leaders = [lang for lang, score in scores.items() if score >= max(.65, scores[best] - .05)]
        if scores[best] >= .75 and len(leaders) == 1:
            return best, ''
        if len(leaders) > 1:
            outputs = {self.glossaries[lang](clean).casefold() for lang in leaders}
            if len(outputs) == 1:
                return hint if hint in leaders else best, 'Shared glossary spelling; language is ambiguous, but the recorded English term agrees.'
        if hint in self.glossaries and len(re.findall(r'[^\W\d_]+', clean)) < 4:
            return hint, ''
        language, confidence = self.identifier.classify(clean)
        if language == 'en' and (confidence >= .8 or letters >= 30):
            return 'en', ''
        if language in self.glossaries and confidence >= .8 and letters >= 8:
            return language, ''
        if language not in NAMES and confidence >= .9 and letters >= 20:
            return 'und', f'Detected unsupported language ({language}); original retained.'
        return 'und', 'Language uncertain for this short or ambiguous text; original retained. Use a manual source language if needed.'

    def prepare_text(self, text):
        language, reason = self.detect(text)
        self.context = language if language in self.glossaries else None

    def segments(self, text):
        # Only split sentence-ending punctuation followed by whitespace, or hard
        # breaks. Product-code dots and decimal points stay within a segment.
        boundaries = list(re.finditer(r'(?<=[.!?;])\s+|[\r\n]+', text))
        cursor = 0
        for boundary in boundaries:
            if boundary.start() > cursor:
                yield text[cursor:boundary.start()], False
            yield boundary.group(), True
            cursor = boundary.end()
        if cursor < len(text):
            yield text[cursor:], False

    def __call__(self, text):
        key = (text, self.context)
        if key in self.cache:
            return self.cache[key]
        parts = []
        for segment, separator in self.segments(text):
            if separator or not any(c.isalpha() for c in segment):
                parts.append(segment)
                continue
            language, reason = self.detect(segment, self.context)
            self.counts[language] += 1
            self.review_count += bool(reason)
            if language not in self.glossaries:
                parts.append(segment)
                continue
            if language not in self.models:
                self.models[language] = self.factory(language)
            parts.append(self.models[language](segment))
        self.cache[key] = ''.join(parts)
        return self.cache[key]

    def _selected(self, text):
        for segment, separator in self.segments(text):
            if not separator:
                language, reason = self.detect(segment)
                yield segment, language, reason

    def glossary_matches(self, text):
        return [match for segment,language,_ in self._selected(text)
                if language in self.glossaries
                for match in self.glossaries[language].glossary_matches(segment)]

    def glossary_spans(self, text):
        # Used only to avoid treating known phrase acronyms as unknown codes.
        return sorted({span for g in self.glossaries.values() for span in g.glossary_spans(text)})

    def review_notes(self, text):
        notes = []
        for segment, language, reason in self._selected(text):
            if reason:
                notes.append(reason)
            if language in self.glossaries:
                notes.extend(self.glossaries[language].review_notes(segment))
        return list(dict.fromkeys(notes))

    def unchanged_reason(self, text):
        notes = self.review_notes(text)
        if notes:
            return ' | '.join(notes)
        language, _ = self.detect(text)
        if language == 'en':
            return 'Already English; retained.'
        if language in self.glossaries:
            return self.glossaries[language].unchanged_reason(text)
        return 'Language uncertain; original retained. Choose a manual source language to retry.'

    def detection_summary(self):
        counts = {NAMES.get(code,code): count for code,count in sorted(self.counts.items())}
        return {'segments': counts, 'review_segments': self.review_count,
                'note': 'Automatic routing works per label or sentence for French, Dutch and German. English is retained. Uncertain or unsupported text is retained for review; language switches within a sentence may require manual translation.'}
