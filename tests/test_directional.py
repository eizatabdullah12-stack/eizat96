from pathlib import Path
from string import Formatter
import sys
import tempfile
import unittest
from zipfile import ZipFile
import fitz

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from directional import DirectionalTranslator, output_terms
from glossary import EngineeringTranslator
from engine import protected_translate
from documents import translate_document
from office_samples import make_sample
from office import parse_xml, TEXT
from i18n import MESSAGES, LANGUAGE_NAMES, text, error_text


def no_model(value):
    raise AssertionError('Known glossary text reached an inference model: '+repr(value))


def session(source,target):
    return DirectionalTranslator(source,target,
        factory=lambda code:EngineeringTranslator(code,no_model),
        outbound_factory=lambda code:no_model)


class DirectionalTests(unittest.TestCase):
    def test_all_language_pairs_and_same_language_retention(self):
        labels={'en':'Adjustment plate','fr':'Plaque de réglage','nl':'Regelplaat','de':'Justierplatte'}
        for source,label in labels.items():
            for target,expected in labels.items():
                with self.subTest(source=source,target=target):
                    self.assertEqual(protected_translate(label,session(source,target)),expected)

    def test_automatic_mixed_languages_to_each_output(self):
        source='Plaque de réglage. Regelplaat. Justierplatte. Adjustment plate.'
        for target,label in {'en':'Adjustment plate','fr':'Plaque de réglage','nl':'Regelplaat','de':'Justierplatte'}.items():
            with self.subTest(target=target):
                self.assertEqual(protected_translate(source,session('auto',target)),'. '.join([label]*4)+'.')

    def test_reverse_glossary_codes_and_brand_names(self):
        for target,expected in [('fr','Plaque de réglage'),('nl','Regelplaat'),('de','Justierplatte')]:
            codes=' 200 mm - KORBO A.1 - M12 - SF800+ - C25/30'
            self.assertEqual(protected_translate('Adjustment plate'+codes,session('en',target)),expected+codes)
            self.assertGreater(len(output_terms(target)),1000)

    def test_target_language_in_files_metadata_and_reports(self):
        for target,label in [('fr','Plaque de réglage'),('nl','Regelplaat'),('de','Justierplatte')]:
            for extension in ('.pdf','.docx','.pptx'):
                with self.subTest(target=target,extension=extension),tempfile.TemporaryDirectory() as folder:
                    source,destination=Path(folder)/('source'+extension),Path(folder)/('translated'+extension)
                    if extension=='.pdf':
                        with fitz.open() as doc:
                            page=doc.new_page();page.insert_text((40,60),'Adjustment plate',fontsize=12);doc.save(source)
                    else:make_sample(source,'Adjustment plate')
                    before=source.read_bytes()
                    result=translate_document(source,destination,session('en',target))
                    self.assertEqual(before,source.read_bytes())
                    self.assertGreater(result['translated'],0)
                    target_name={'fr':'French','nl':'Dutch','de':'German'}[target]
                    self.assertIn('target: '+target_name,Path(result['report']).read_text())
                    if extension=='.pdf':
                        with fitz.open(destination) as doc:
                            rendered=doc[0].get_text()+'\n'.join(a.info.get('content','') for a in (doc[0].annots() or []))
                            self.assertIn('English to '+target_name,doc.metadata['creator'])
                    else:
                        member='word/document.xml' if extension=='.docx' else 'ppt/slides/slide1.xml'
                        with ZipFile(destination) as package:
                            root=parse_xml(package.read(member));rendered=''.join(n.text or '' for n in root.iter() if n.tag in TEXT)
                    self.assertIn(label,rendered)

    def test_interface_catalogues_complete_and_placeholders_match(self):
        self.assertGreater(len(MESSAGES),40)
        fields=lambda value:{key for _,key,_,_ in Formatter().parse(value) if key}
        for key,translations in MESSAGES.items():
            self.assertEqual(set(translations),set(LANGUAGE_NAMES))
            expected=fields(translations['en'])
            for language,value in translations.items():
                with self.subTest(key=key,language=language):
                    self.assertTrue(value)
                    self.assertEqual(expected,fields(value))
        self.assertEqual(text('fr','translate_save'),'Traduire et enregistrer…')
        self.assertEqual(text('nl','cancel'),'Annuleren')
        self.assertEqual(text('de','output_language'),'Zielsprache')
        self.assertIn('annulée',error_text('fr','Translation cancelled; no output was saved.'))


if __name__=='__main__':unittest.main()
