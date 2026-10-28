"""Four output languages using the bundled English-pivot model pairs."""
from automatic import AutoTranslator, NAMES
from glossary import EngineeringTranslator, TERMS, fold

LANGUAGES = {'en':'English', 'fr':'French', 'nl':'Dutch', 'de':'German'}


def output_terms(target):
    terms = {}
    for line in TERMS[target].strip().splitlines():
        source, english = line.split('|',1)
        if fold(source) != fold(english):
            terms.setdefault(fold(english), source)
    return terms


class DirectionalTranslator(AutoTranslator):
    def __init__(self, source='auto', target='en', factory=None, outbound_factory=None):
        if source not in ('auto', *LANGUAGES) or target not in LANGUAGES:
            raise ValueError('Choose English, French, Dutch or German.')
        super().__init__(factory=factory)
        self.language = source
        self.target_language = target
        self.outbound_factory = outbound_factory
        self.outbound = None
        if target != 'en':
            self.reverse_terms = output_terms(target)
            self.terms.update({fold(key):value for key,value in self.reverse_terms.items()})
        else:
            self.reverse_terms = {}

    def _detect(self, text, hint=None):
        if self.language != 'auto':
            return self.language, ''
        return super()._detect(text, hint)

    def target_translator(self):
        if self.outbound is None:
            if self.outbound_factory is None:
                from offline import LazyRawTranslator
                raw = LazyRawTranslator('en', self.target_language)
            else:
                raw = self.outbound_factory(self.target_language)
            self.outbound = EngineeringTranslator(self.target_language, raw, terms_override=self.reverse_terms)
        return self.outbound

    def translate_segment(self, language, segment):
        if language == self.target_language or language == 'und':
            return segment
        if language == 'en':
            english = segment
        else:
            english = super().translate_segment(language, segment)
        if self.target_language == 'en':
            return english
        return self.target_translator()(english)

    def review_notes(self, text):
        return [note for segment,language,reason in self._selected(text)
                if language != self.target_language
                for note in ([reason] if reason else []) +
                (self.glossaries[language].review_notes(segment) if language in self.glossaries else [])]

    def unchanged_reason(self, text):
        language, _ = self.detect(text)
        if language == self.target_language:
            return f'Already {LANGUAGES[language]}; retained.'
        return super().unchanged_reason(text)

    def detection_summary(self):
        result = super().detection_summary()
        result['note'] = (f'Output language: {LANGUAGES[self.target_language]}. '
                          'Source languages: English, French, Dutch and German. '
                          'Text already in the selected output language is retained. '
                          'Uncertain or unsupported text is retained for review. '
                          'Languages other than English use English as an intermediate when needed; review engineering context.')
        return result
