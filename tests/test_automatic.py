from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from automatic import AutoTranslator
from glossary import EngineeringTranslator
from engine import protected_translate
from documents import translate_document
from office_samples import make_sample
from office import parse_xml, TEXT


def no_model(text):
    raise AssertionError('Known glossary text unexpectedly reached a model: '+repr(text))


class AutomaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = AutoTranslator(lambda code: EngineeringTranslator(code,no_model))

    def test_short_technical_labels_use_glossary_evidence(self):
        for label,language in [('Plaque de réglage','fr'),('Regelplaat','nl'),('Justierplatte','de')]:
            self.assertEqual(self.router.detect(label)[0],language)
            self.assertEqual(protected_translate(label,self.router),'Adjustment plate')

    def test_english_labels_and_prose_are_retained(self):
        for text in ('Concrete','Adjustment plate','This drawing is for information only.'):
            self.assertEqual(protected_translate(text,self.router),text)

    def test_same_paragraph_multiple_source_languages(self):
        text='Plaque de réglage. Regelplaat. Justierplatte. This drawing is for information only.'
        self.assertEqual(protected_translate(text,self.router),
                         'Adjustment plate. Adjustment plate. Adjustment plate. This drawing is for information only.')

    def test_unknown_or_unsupported_text_retained_for_review(self):
        text='Este documento está escrito en español y contiene instrucciones de instalación.'
        self.assertEqual(protected_translate(text,self.router),text)
        self.assertIn('unsupported',self.router.unchanged_reason(text))
        self.assertEqual(protected_translate('Qzxunfamiliar',self.router),'Qzxunfamiliar')
        self.assertTrue(self.router.review_notes('Qzxunfamiliar'))
        self.assertEqual(protected_translate('Semelle',self.router),'Semelle')
        self.assertIn('context',self.router.unchanged_reason('Semelle'))

    def test_dimensions_and_references_preserved(self):
        for source in ('Plaque de réglage','Regelplaat','Justierplatte'):
            codes=' 200 mm - KORBO A.1 - M12 - SF800+ - C25/30'
            self.assertEqual(protected_translate(source+codes,self.router),'Adjustment plate'+codes)

    def test_three_document_formats_and_detection_report(self):
        english='This drawing is for information only.'
        mixed='Plaque de réglage. Regelplaat. Justierplatte. '+english
        for extension in ('.pdf','.docx','.pptx'):
            router=AutoTranslator(lambda code:EngineeringTranslator(code,no_model))
            with self.subTest(extension=extension),tempfile.TemporaryDirectory() as folder:
                source,target=Path(folder)/('source'+extension),Path(folder)/('English'+extension)
                if extension=='.pdf':
                    with fitz.open() as pdf:
                        page=pdf.new_page()
                        for index,label in enumerate(('Plaque de réglage','Regelplaat','Justierplatte',english)):
                            page.insert_text((40,60+index*50),label,fontsize=12)
                        pdf.save(source)
                else:
                    make_sample(source,mixed)
                original=source.read_bytes()
                result=translate_document(source,target,router)
                self.assertEqual(source.read_bytes(),original)
                self.assertTrue({'French','Dutch','German','English'}.issubset(result['detection']['segments']))
                report=Path(result['report']).read_text()
                self.assertIn('Auto / mixed languages',report)
                self.assertIn('AUTO / MIXED LANGUAGE SUMMARY',report)
                if extension=='.pdf':
                    with fitz.open(target) as pdf:
                        text=pdf[0].get_text()+'\n'.join(a.info.get('content','') for a in (pdf[0].annots() or []))
                else:
                    part='word/document.xml' if extension=='.docx' else 'ppt/slides/slide1.xml'
                    with ZipFile(target) as package:
                        root=parse_xml(package.read(part))
                        text=''.join(n.text or '' for n in root.iter() if n.tag in TEXT)
                self.assertIn('Adjustment plate',text)
                self.assertIn(english,text)


if __name__=='__main__':
    unittest.main()
