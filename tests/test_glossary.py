import sys
from pathlib import Path
import tempfile
import unicodedata
import unittest
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from glossary import EngineeringTranslator, EXTENDED_ROWS, TERMS, TERM_CATEGORIES, fold
from engine import protected_translate, translate_pdf


def no_model(text):
    raise AssertionError('Known terminology was sent to the general model: ' + repr(text))


class EngineeringChecks(unittest.TestCase):
    def test_expanded_catalogue_without_model_fallback(self):
        # Exercise every new alias in all languages, using the established
        # core interpretation where an entry intentionally overlaps it.
        for language in TERMS:
            expected = {fold(a):b for a,b in (line.split('|',1) for line in TERMS[language].strip().splitlines())}
            translator=EngineeringTranslator(language,no_model)
            for row in EXTENDED_ROWS:
                for source in row[language].split(';'):
                    with self.subTest(language=language,source=source):
                        self.assertEqual(translator(source).casefold(),expected[fold(source)].casefold())
                        self.assertIn(fold(source),TERM_CATEGORIES[language])

    def test_architecture_and_material_distinctions(self):
        samples={
            'fr':[('pare-vapeur','vapour barrier'),('frein-vapeur','vapour retarder'),('appui de fenêtre','window sill'),('seuil de porte','door threshold'),('chape','screed'),('dalle pleine','solid slab'),('pierre bleue','Belgian blue limestone'),('géotextile','geotextile')],
            'nl':[('dampscherm','vapour barrier'),('damprem','vapour retarder'),('vensterbank','window sill'),('deurdorpel','door threshold'),('dekvloer','screed'),('massieve betonplaat','solid slab'),('rotswol','stone wool'),('glaswol','glass wool')],
            'de':[('Dampfsperre','vapour barrier'),('Dampfbremse','vapour retarder'),('Fensterbank','window sill'),('Türschwelle','door threshold'),('Estrich','screed'),('Vollplatte','solid slab'),('Steinwolle','stone wool'),('Glaswolle','glass wool')],
        }
        for language,terms in samples.items():
            translator=EngineeringTranslator(language,no_model)
            for source,expected in terms:
                self.assertEqual(translator(source).casefold(),expected.casefold())

    def test_expanded_qualified_phrases_and_context(self):
        for language,standalone,qualified in [('fr','seuil','seuil de porte'),('nl','dorpel','deurdorpel'),('de','Schwelle','Türschwelle')]:
            translator=EngineeringTranslator(language,no_model)
            self.assertTrue(translator.review_notes(standalone))
            self.assertEqual(translator.review_notes(qualified),[])
            self.assertEqual(translator(qualified).casefold(),'door threshold')
        for language,label in [('fr','MUR-RIDEAU'),('nl','VLIESGEVEL'),('de','VORHANGFASSADE')]:
            self.assertEqual(EngineeringTranslator(language,no_model)(label),'CURTAIN WALL')

    def test_architecture_pdf_rotated_with_protected_values(self):
        from engine import LABEL_FONT, LABEL_FONT_NAME
        for language,label in [('fr','Seuil de porte'),('nl','Deurdorpel'),('de','Türschwelle')]:
            with tempfile.TemporaryDirectory() as folder:
                source,destination=Path(folder)/'source.pdf',Path(folder)/'English.pdf'
                with fitz.open() as doc:
                    page=doc.new_page(width=420,height=595);page.set_rotation(270)
                    page.insert_font(fontname=LABEL_FONT_NAME,fontbuffer=LABEL_FONT.buffer)
                    page.insert_text((100,80),label+' 200 mm - Ø16',fontsize=9,rotate=270,fontname=LABEL_FONT_NAME)
                    doc.save(source)
                result=translate_pdf(source,destination,EngineeringTranslator(language,no_model))
                self.assertEqual(result['replaced'],1)
                with fitz.open(destination) as doc:
                    self.assertIn('Door threshold 200 mm - Ø16',doc[0].get_text())
                    self.assertEqual(doc[0].rotation,270)

    def test_phrases_and_materials(self):
        examples = {
            'fr': [('poutre en béton armé','reinforced concrete beam'),('poutre','beam'),('béton','concrete'),('acier','steel')],
            'nl': [('gewapende betonbalk','reinforced concrete beam'),('balk','beam'),('beton','concrete'),('staal','steel')],
            'de': [('stahlbetonträger','reinforced concrete beam'),('träger','beam'),('beton','concrete'),('stahl','steel')],
        }
        for language, samples in examples.items():
            translator = EngineeringTranslator(language, no_model)
            for source, expected in samples:
                with self.subTest(language=language, source=source):
                    self.assertEqual(translator(source), expected)

    def test_accents_case_whitespace_and_apostrophes(self):
        french = EngineeringTranslator('fr', no_model)
        self.assertEqual(french('POUTRE EN BETON ARME'), 'REINFORCED CONCRETE BEAM')
        self.assertEqual(french('Poutre en\u00a0béton   armé'), 'Reinforced concrete beam')
        self.assertEqual(french(unicodedata.normalize('NFD','béton armé')), 'reinforced concrete')
        self.assertEqual(french('LAME D’AIR'), 'AIR GAP')
        german = EngineeringTranslator('de', no_model)
        self.assertEqual(german('Stahlbetontraeger'), 'Reinforced concrete beam')
        self.assertEqual(german('Oberkante Fertigfußboden'), 'Finished floor level')

    def test_only_unknown_fragments_reach_model(self):
        calls = []
        def general(text):
            calls.append(text)
            return text.replace('Bonjour', 'Hello')
        translator = EngineeringTranslator('fr', general)
        self.assertEqual(translator('Bonjour, poutre!'), 'Hello, beam!')
        self.assertEqual(calls, ['Bonjour, '])
        self.assertEqual(translator('Bonjour, poutre!'), 'Hello, beam!')
        self.assertEqual(len(calls), 1)
        # Partial words and product identifiers must not be substituted.
        self.assertEqual(translator('betonXYZ'), 'betonXYZ')
        self.assertEqual(calls[-1], 'betonXYZ')
        self.assertEqual(translator('KORBO / SUMO'), 'KORBO / SUMO')

    def test_context_flags_and_specific_phrases(self):
        for language, ambiguous in [('fr','Semelle'),('nl','Plaat'),('de','Platte')]:
            translator = EngineeringTranslator(language, no_model)
            self.assertEqual(translator(ambiguous), ambiguous)
            self.assertTrue(translator.review_notes(ambiguous))
        translator = EngineeringTranslator('fr', no_model)
        self.assertEqual(translator('Semelle filante'), 'Strip footing')
        self.assertEqual(translator.review_notes('Semelle filante'), [])
        self.assertEqual(translator('Poutre'), 'Beam')
        self.assertEqual(translator.review_notes('Poutre'), [])

    def test_values_codes_and_symbols(self):
        for language, label in [('fr','Poutre'),('nl','Balk'),('de','Träger')]:
            translator = EngineeringTranslator(language, no_model)
            codes = ' 200 mm - P1.42 - C25/30 - HEA200 - Ø16 - B500B - S235JR - HEA 200 - RHS 100x50x4 - REZ+1'
            self.assertEqual(protected_translate(label + codes, translator), 'Beam' + codes)

    def test_glossary_pdf_and_review_report(self):
        for language, label, ambiguous in [('fr','Poutre en beton arme','Semelle'),('nl','Gewapende betonbalk','Plaat'),('de','Stahlbetonbalken','Platte')]:
            for mode in ('replace','notes'):
                with self.subTest(language=language, mode=mode), tempfile.TemporaryDirectory() as folder:
                    source, destination = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
                    with fitz.open() as pdf:
                        page = pdf.new_page(width=595, height=420)
                        page.draw_line((20,180),(570,180))
                        page.insert_text((40,80),label+' 200 mm - P1.42 - HEA200',fontsize=12)
                        page.insert_text((40,120),ambiguous,fontsize=12)
                        pdf.save(source)
                    before = source.read_bytes()
                    result = translate_pdf(source,destination,EngineeringTranslator(language,no_model),mode=mode)
                    self.assertEqual(source.read_bytes(), before)
                    self.assertEqual(result['review_labels'],1)
                    self.assertGreaterEqual(result['glossary_terms'],1)
                    report = Path(result['report']).read_text(encoding='utf-8')
                    self.assertIn('REVIEW CONTEXT',report)
                    with fitz.open(destination) as pdf:
                        page = pdf[0]
                        rendered = page.get_text() + '\n'.join(a.info['content'] for a in (page.annots() or []))
                        self.assertIn('reinforced concrete beam',rendered.lower())
                        for value in ('200 mm','P1.42','HEA200',ambiguous):
                            self.assertIn(value,page.get_text())


if __name__ == '__main__':
    unittest.main()
