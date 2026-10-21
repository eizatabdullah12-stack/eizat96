from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from glossary import EngineeringTranslator, TERMS, BRANDS
from engine import protected_translate, translate_pdf
from documents import translate_document
from office_samples import make_sample
from office import parse_xml, TEXT


def no_model(text):
    raise AssertionError('Known phrase reached model: '+repr(text))


class ExpansionTests(unittest.TestCase):
    def test_vocabulary_size_and_representative_gaps(self):
        self.assertGreater(sum(len(x.strip().splitlines()) for x in TERMS.values()), 4000)
        cases = {
            'fr': [('Livraison','delivery'),('Chantier','construction site'),('Devis','quotation'),
                   ('Plaque de réglage','adjustment plate'),('Boulon de fixation','fixing bolt'),
                   ('Vis de fixation','fixing screw'),('Cornière de support','support angle'),
                   ('Boîte d’attente','reinforcement continuity box'),('Goujon pour efforts tranchants','shear load connector'),
                   ('Non vérifié','not checked'),('Non conforme','not satisfied')],
            'nl': [('Levering','delivery'),('Offerte','quotation'),('Regelplaat','adjustment plate'),
                   ('Bevestigingsbout','fixing bolt'),('Bevestigingsschroef','fixing screw'),
                   ('Wachtdoos','reinforcement continuity box'),('Dwarskrachtdeuvel','shear load connector'),
                   ('Niet gecontroleerd','not checked'),('Niet aangetoond','not demonstrated')],
            'de': [('Lieferung','delivery'),('Angebot','quotation'),('Justierplatte','adjustment plate'),
                   ('Höhenverstellung','height adjustment'),('Befestigungsbolzen','fixing bolt'),
                   ('Befestigungsschraube','fixing screw'),('Rückbiegeanschluss','reinforcement continuity box'),
                   ('Querkraftdorn','shear load connector'),('Nicht geprüft','not checked')],
        }
        for language, samples in cases.items():
            translator=EngineeringTranslator(language,no_model)
            for source, english in samples:
                with self.subTest(language=language, source=source):
                    self.assertEqual(protected_translate(source,translator).casefold(),english)

    def test_uppercase_short_labels_are_not_mistaken_for_codes(self):
        for language,source,expected in [('fr','VUE','VIEW'),('fr','NOM','NAME'),
                                         ('fr','DATE','DATE'),('nl','WERF','CONSTRUCTION SITE'),
                                         ('nl','NAAM','NAME'),('de','NAME','NAME')]:
            self.assertEqual(protected_translate(source,EngineeringTranslator(language,no_model)),expected)

    def test_glossary_phrases_with_acronyms(self):
        translator=EngineeringTranslator('nl',no_model)
        self.assertEqual(protected_translate('RVS hoeklijn',translator),'Stainless steel angle')
        self.assertEqual(protected_translate('RAL-kleur',translator),'RAL colour')

    def test_typography_and_discretionary_hyphen(self):
        translator=EngineeringTranslator('fr',no_model)
        self.assertEqual(translator('Bavette dʼétanchéité autocollante'),'Self-adhesive flashing')
        self.assertEqual(translator('Réglage en pro\u00adfondeur'),'Depth adjustment')
        self.assertEqual(EngineeringTranslator('de',no_model)('Hoehenverstellung'),'Height adjustment')
        self.assertEqual(EngineeringTranslator('de',no_model)('Waermeleitfaehigkeit'),'Thermal conductivity')

    def test_product_names_and_codes_survive(self):
        for language in ('fr','nl','de'):
            translator=EngineeringTranslator(language,no_model)
            for name in BRANDS:
                self.assertEqual(protected_translate(name,translator),name)
            label={'fr':'Plaque de réglage','nl':'Regelplaat','de':'Justierplatte'}[language]
            codes=' - KORBO A.1 - M12 - FSA - SF800+ - 316L - 200 mm - C25/30'
            self.assertEqual(protected_translate(label+codes,translator),'Adjustment plate'+codes)

    def test_unchanged_results_explain_ambiguity_or_model_result(self):
        translator=EngineeringTranslator('fr',lambda s:s)
        self.assertIn('context review',translator.unchanged_reason('Semelle'))
        self.assertIn('product name',translator.unchanged_reason('KORBO'))
        self.assertIn('offline model',translator.unchanged_reason('qzxunknownword'))

    def test_product_hardware_terms_in_all_three_formats(self):
        for language,label in [('fr','Plaque de réglage'),('nl','Regelplaat'),('de','Justierplatte')]:
            translator=EngineeringTranslator(language,no_model)
            with tempfile.TemporaryDirectory() as folder:
                for extension in ('.pdf','.docx','.pptx'):
                    source,target=Path(folder)/('source'+extension),Path(folder)/('English'+extension)
                    if extension=='.pdf':
                        with fitz.open() as document:
                            page=document.new_page()
                            page.insert_text((40,60),label+' 200 mm',fontsize=12)
                            document.save(source)
                    else:
                        make_sample(source,label)
                    result=translate_document(source,target,translator)
                    self.assertGreater(result['translated'],0)
                    if extension=='.pdf':
                        with fitz.open(target) as document:
                            text=document[0].get_text()+'\n'.join(a.info.get('content','') for a in (document[0].annots() or []))
                    else:
                        member='word/document.xml' if extension=='.docx' else 'ppt/slides/slide1.xml'
                        with ZipFile(target) as package:
                            root=parse_xml(package.read(member))
                            text=''.join(n.text or '' for n in root.iter() if n.tag in TEXT)
                    self.assertIn('Adjustment plate 200 mm',text)


if __name__=='__main__':
    unittest.main()
