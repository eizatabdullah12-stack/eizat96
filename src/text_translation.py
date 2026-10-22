"""Offline plain-text translation and a worker that keeps only the newest edit."""
from collections import Counter
import threading

from directional import DirectionalTranslator
from conversation import ConversationTranslator
from engine import protected_translate

MAX_TEXT_CHARS = 50000
LIVE_TEXT_CHARS = 4000


class TextSession:
    def __init__(self, factory=DirectionalTranslator, conversation_factory=ConversationTranslator):
        self.factory = factory
        self.conversation_factory = conversation_factory
        self.pair = self.translator = None

    def translate(self, value, source='auto', target='en', cancel=lambda: False, mode='engineering'):
        if len(value) > MAX_TEXT_CHARS:
            raise ValueError('Text exceeds the 50,000 character limit.')
        if cancel():
            raise InterruptedError('Text translation cancelled.')
        if not value.strip():
            return {'text': value, 'languages': {}, 'reviews': []}
        if mode not in ('engineering', 'conversation'):
            raise ValueError('Unknown text translation mode')
        pair = (source, target, mode)
        if self.pair != pair:
            # Drop the previous pair before loading another set of models.
            self.translator = None
            factory = self.conversation_factory if mode == 'conversation' else self.factory
            self.translator = factory(source, target)
            self.pair = pair
        translator = self.translator
        pieces, languages, reviews = [], Counter(), []
        for segment, separator in translator.segments(value):
            if cancel():
                raise InterruptedError('Text translation cancelled.')
            if separator or not any(c.isalpha() for c in segment):
                pieces.append(segment)
                continue
            language, reason = translator.detect(segment)
            languages[language] += 1
            pieces.append(protected_translate(segment, translator))
            reviews.extend(translator.review_notes(segment))
        if cancel():
            raise InterruptedError('Text translation cancelled.')
        return {'text': ''.join(pieces), 'languages': dict(languages),
                'reviews': list(dict.fromkeys(reviews))}


class TextWorker:
    """One inference thread. New edits cancel obsolete work and replace pending work."""
    def __init__(self, emit, lock=None, session_factory=TextSession):
        self.emit = emit
        self.lock = lock or threading.Lock()
        self.session_factory = session_factory
        self.condition = threading.Condition()
        self.pending = None
        self.token = None
        self.closed = False
        self.thread = None

    def cancel(self):
        with self.condition:
            if self.token:
                self.token.set()
            self.pending = None

    def submit(self, generation, value, source, target, mode='engineering'):
        with self.condition:
            if self.closed:
                return
            if self.token:
                self.token.set()
            self.token = threading.Event()
            self.pending = (generation, value, source, target, self.token, mode)
            if self.thread is None:
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
            self.condition.notify()

    def close(self):
        with self.condition:
            self.closed = True
            if self.token:
                self.token.set()
            self.pending = None
            self.condition.notify()

    def _run(self):
        session = self.session_factory()
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.closed or self.pending is not None)
                if self.closed:
                    return
                generation, value, source, target, token, mode = self.pending
                self.pending = None
            result = error = None
            try:
                with self.lock:
                    result = session.translate(value, source, target, token.is_set, mode=mode)
            except InterruptedError:
                continue
            except Exception as exc:
                error = str(exc)
            if not token.is_set():
                self.emit(('text_done', (generation, result, error)))
