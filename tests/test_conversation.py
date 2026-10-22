from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from conversation import PHRASES, INDEX, LANGS, key, equivalent, normalize_input, ConversationTranslator
from text_translation import TextSession
from engine import protected_translate
from branding import logo_png, CREATOR


class ConversationTests(unittest.TestCase):
    def test_phrasebook_all_unambiguous_equivalents_in_all_directions(self):
        self.assertGreaterEqual(len(PHRASES), 900)
        checked = 0
        for value, candidates in INDEX.items():
            for source in LANGS:
                rows = [row for language, row in candidates if language == source]
                for target in LANGS:
                    outputs = {row[target].split(';')[0].rstrip('.!?…') for row in rows}
                    if len(outputs) == 1:
                        self.assertEqual(equivalent(value, source, target), outputs.pop(), (value, source, target))
                        checked += 1
        self.assertGreater(checked, 15000)

    def test_accents_do_not_merge_different_french_words(self):
        self.assertNotEqual(key('mais'), key('maïs'))
        self.assertEqual(equivalent('mais', 'fr', 'en'), 'but')
        self.assertEqual(equivalent('maïs', 'fr', 'en'), 'corn')
        self.assertEqual(equivalent('OÙ?', 'fr', 'en'), 'WHERE?')

    def test_swear_words_are_uncensored_in_all_twelve_directions(self):
        row = next(r for r in PHRASES if r['en'] == 'Fuck off')
        for source in LANGS:
            for target in LANGS:
                if source != target:
                    self.assertEqual(equivalent(row[source].split(';')[0]+'!', source, target), row[target].split(';')[0]+'!')

    def test_sentence_model_receives_whole_sentence_not_glossary_fragments(self):
        received = []
        def factory(source, target):
            def translate(value):
                received.append((source, target, value))
                return "I'm going to the office tomorrow."
            return translate
        translator = ConversationTranslator('fr', 'en', raw_factory=factory)
        self.assertEqual(translator('Je vais au bureau demain.'), "I'm going to the office tomorrow.")
        self.assertEqual(received, [('fr', 'en', 'Je vais au bureau demain.')])

    def test_common_chat_spellings_and_agreement(self):
        for value, source, expected in [('i is tired', 'en', 'I am tired'),
            ('you is busy', 'en', 'you are busy'), ('j ai faim', 'fr', "j'ai faim"),
            ('ik bent moe', 'nl', 'ik ben moe'), ('ich ist müde', 'de', 'ich bin müde')]:
            self.assertEqual(normalize_input(value, source), expected)
        # Case, names, numbers and unknown grammar are not broadly rewritten.
        self.assertEqual(normalize_input('KORBO M12 200 mm', 'en'), 'KORBO M12 200 mm')
        self.assertEqual(normalize_input('je suis aller', 'fr'), 'je suis aller')

    def test_mixed_conversation_and_same_language_grammar(self):
        session = TextSession()
        result = session.translate('Bonjour!\nIk heb honger.\nIch bin müde.', mode='conversation')
        self.assertEqual(result['text'], "Hello!\nI'm hungry.\nI'm tired.")
        self.assertEqual(set(result['languages']), {'fr', 'nl', 'de'})
        self.assertEqual(session.translate('im tired', mode='conversation')['text'], "I'm tired")
        self.assertEqual(session.translate('i is tired', source='en', mode='conversation')['text'], "I'm tired")

    def test_conversation_keeps_protected_values(self):
        translator = ConversationTranslator('fr', 'en', raw_factory=lambda source,target:lambda text:'translated ')
        result = protected_translate('Vérifier KORBO M12 200 mm', translator)
        self.assertIn('KORBO M12 200 mm', result)

    def test_creator_and_generated_png(self):
        self.assertEqual(CREATOR, 'Eizat')
        self.assertTrue(logo_png(32).startswith(b'\x89PNG\r\n\x1a\n'))


if __name__ == '__main__':
    unittest.main()
