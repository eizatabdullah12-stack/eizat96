"""Dutch/French construction labels must not depend on general model guesses."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from offline import OfflineTranslator
from text_translation import TextSession
from directional import DirectionalTranslator
from glossary import EngineeringTranslator
from engine import protected_translate,translate_pdf

CASES={
 'nl':{'chape':'screed','chapes':'screeds','hourdis':'hollow-core slab',
       'welfsel':'hollow-core slab','welfsels':'hollow-core slabs',
       'betonwand':'concrete wall','betonnen muur':'concrete wall','betonmuur':'concrete wall',
       'muur in beton':'concrete wall','gewapende betonwand':'reinforced concrete wall',
       'prefab betonwand':'precast concrete wall','cementchape':'cement screed',
       'gewapende chape':'reinforced screed','zelfnivellerende chape':'self-levelling screed',
       'welfsels in voorgespannen beton':'prestressed hollow-core slabs',
       'predallen':'precast floor plates','betonnen vloerplaat':'concrete floor slab'},
 'fr':{'chape':'screed','chapes':'screeds','hourdis':'hollow-core slab',
       'mur béton':'concrete wall','mur en béton':'concrete wall','mur en béton armé':'reinforced concrete wall','voile BA':'reinforced concrete wall',
       'poutre BA':'reinforced concrete beam',
       'chape de compression':'structural topping','chape de compression en béton':'concrete structural topping',
       'chape ciment':'cement screed','chape armée':'reinforced screed',
       'chape autolissante':'self-levelling screed','hourdis en béton précontraint':'prestressed hollow-core slabs',
       'prédalles':'precast floor plates','poutrelle métallique':'steel beam',
       'poutre retroussée':'upstand beam','poutre en retombée':'downstand beam'}
}

class ConstructionBasicsTests(unittest.TestCase):
    def test_common_dutch_and_french_materials_are_recorded(self):
        examples={'nl':{'mortel':'mortar','cement':'cement','zand':'sand','snelbouw':'clay masonry block',
                        'fundering':'foundation','vloer':'floor','druklaag':'structural topping',
                        'waterkering':'water barrier','voeg':'joint','voegwerk':'pointing'},
                  'fr':{'mortier':'mortar','ciment':'cement','sable':'sand','bloc de terre cuite':'clay masonry block',
                        'fondation':'foundation','plancher':'floor','couche de compression':'structural topping',
                        'coupure de capillarité':'capillary break','joint':'joint','jointoiement':'pointing'}}
        with patch('offline.RawTranslator',side_effect=AssertionError('Known construction word loaded a model')):
            auto=DirectionalTranslator('auto','en')
            for code,rows in examples.items():
                tr=OfflineTranslator(code)
                for original,expected in rows.items():
                    with self.subTest(language=code,term=original):
                        self.assertEqual(tr(original),expected)
                        self.assertEqual(protected_translate(original,auto),expected)

    def test_dutch_and_french_labels_translate_before_loading_models(self):
        with patch('offline.RawTranslator',side_effect=AssertionError('Known technical label loaded a model')):
            for code,rows in CASES.items():
                tr=OfflineTranslator(code)
                for original,expected in rows.items():
                    with self.subTest(language=code,source=original):
                        self.assertEqual(protected_translate(original,tr),expected)
                self.assertIsNone(tr.raw)

    def test_engineering_text_mode_manual_dutch_french_and_auto(self):
        session=TextSession()
        with patch('offline.RawTranslator',side_effect=AssertionError('Known labels reached a model')):
            for source,value,expected in [
                ('nl','chape\nhourdis\nbetonnen muur','screed\nhollow-core slab\nconcrete wall'),
                ('fr','chape\nhourdis\nmur béton','screed\nhollow-core slab\nconcrete wall'),
                ('auto','Chape 60 mm. Hourdis 200 mm. Betonnen muur 200 mm.',
                 'Screed 60 mm. Hollow-core slab 200 mm. Concrete wall 200 mm.')]:
                result=session.translate(value,source=source,mode='engineering')
                self.assertEqual(result['text'],expected)

    def test_qualified_terms_and_other_ambiguous_labels_keep_their_meanings(self):
        tr=OfflineTranslator('fr')
        self.assertEqual(tr('chape de compression'),'structural topping')
        self.assertEqual(tr('hourdis'),'hollow-core slab')
        self.assertTrue(any('Belgian engineering default' in note for note in tr.review_notes('hourdis')))
        self.assertEqual(tr('semelle'),'semelle')
        self.assertEqual(tr('hourdis béton précontraint'),'prestressed hollow-core slabs')

    def test_model_is_loaded_only_for_unlisted_prose(self):
        with patch('offline.RawTranslator',return_value=lambda value:'translated prose') as load:
            tr=OfflineTranslator('nl')
            self.assertEqual(tr('chape'),'screed');load.assert_not_called()
            self.assertEqual(tr('qzxprose'),'translated prose')
            self.assertEqual(tr('qzxanother'),'translated prose');load.assert_called_once_with('nl','en')

    def test_english_concrete_wall_translates_to_dutch_and_french_without_model(self):
        with patch('offline.RawTranslator',side_effect=AssertionError('Known outbound label loaded a model')):
            for code,expected in [('nl','betonwand'),('fr','mur en béton')]:
                self.assertEqual(protected_translate('concrete wall',DirectionalTranslator('en',code)),expected)
            self.assertEqual(protected_translate('BA M12 200 mm',OfflineTranslator('fr')),'BA M12 200 mm')

    def test_saved_pdf_contains_translated_core_construction_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target=Path(directory)/'labels.pdf',Path(directory)/'translated.pdf'
            with fitz.open() as pdf:
                page=pdf.new_page()
                for i,label in enumerate(['chape 60 mm','hourdis 200 mm','betonnen muur 200 mm']):
                    page.insert_text((40,80+i*60),label,fontsize=10)
                pdf.save(source)
            with patch('offline.RawTranslator',side_effect=AssertionError('Known labels reached model')):
                result=translate_pdf(source,target,DirectionalTranslator('nl','en'))
            self.assertEqual(result['translated'],3)
            with fitz.open(target) as pdf:
                text=pdf[0].get_text()+'\n'+'\n'.join(a.info.get('content','') for a in (pdf[0].annots() or []))
            for expected in ['screed 60 mm','hollow-core slab 200 mm','concrete wall 200 mm']:
                self.assertIn(expected,' '.join(text.split()))

if __name__=='__main__': unittest.main()
