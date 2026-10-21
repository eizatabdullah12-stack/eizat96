import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from lxml import etree
from documents import translate_document
from glossary import EngineeringTranslator
from office import parse_xml, text_groups, replace_group, verify_office_output, translate_office, W, A, WS, AS
from office_samples import make_sample


def text_of(path, member):
    with ZipFile(path) as package:
        root = parse_xml(package.read(member))
    return ''.join(n.text or '' for n in root.iter() if n.tag in {f'{{{W}}}t', f'{{{A}}}t'})


class OfficeTests(unittest.TestCase):
    def test_native_formats_glossary_tables_notes_and_source_preserved(self):
        for extension, member in (('.docx', 'word/document.xml'), ('.pptx', 'ppt/slides/slide1.xml')):
            with self.subTest(extension=extension), tempfile.TemporaryDirectory() as folder:
                source, target = Path(folder)/('source'+extension), Path(folder)/('English'+extension)
                media = ('word' if extension == '.docx' else 'ppt') + '/media/image1.png'
                make_sample(source, 'Poutre en béton armé', {media: b'opaque image bytes'})
                before = source.read_bytes()
                progress = []
                result = translate_document(source, target, EngineeringTranslator('fr', lambda s: s), progress=lambda a,b: progress.append((a,b)))
                self.assertEqual(before, source.read_bytes())
                self.assertIn('Reinforced concrete beam 200 mm - HEA200 - B500B', text_of(target, member))
                self.assertEqual(result['translated'], 4 if extension == '.docx' else 2)
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), result['file_sha256'])
                self.assertEqual(progress[-1][0], progress[-1][1])
                with ZipFile(source) as original, ZipFile(target) as saved:
                    self.assertEqual(original.namelist(), saved.namelist())
                    self.assertEqual(original.read(media), saved.read(media))
                    for name in original.namelist():
                        if not name.endswith('.xml') or name == '[Content_Types].xml':
                            self.assertEqual(original.read(name), saved.read(name))
                    root = parse_xml(saved.read(member))
                    ns = W if extension == '.docx' else A
                    bold = root.find(f'.//{{{ns}}}b') if extension == '.docx' else root.find(f'.//{{{ns}}}rPr')
                    self.assertIsNotNone(bold)
                report = Path(result['report']).read_text()
                self.assertIn('File SHA256: '+result['file_sha256'], report)
                self.assertGreater(result['glossary_terms'], 0)

    def test_paragraph_translation_crosses_style_runs(self):
        root = parse_xml(f'<w:p xmlns:w="{W}"><w:r><w:rPr><w:b/></w:rPr><w:t>Poutre en </w:t></w:r><w:r><w:rPr><w:i/></w:rPr><w:t>béton armé</w:t></w:r></w:p>'.encode())
        nodes = list(text_groups(root))[0]
        translated = EngineeringTranslator('fr', lambda s:s)(''.join(n.text for n in nodes))
        replace_group(nodes, translated)
        self.assertEqual(''.join(n.text for n in nodes), 'Reinforced concrete beam')
        self.assertEqual(len(root), 2)
        self.assertIsNotNone(root.find(f'.//{{{W}}}b'))
        self.assertIsNotNone(root.find(f'.//{{{W}}}i'))

    def test_fields_formulas_breaks_and_nested_textboxes(self):
        xml = f'''<w:document xmlns:w="{W}" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body>
        <w:p><w:r><w:t>Beton</w:t><w:tab/><w:t>Träger</w:t><w:br/><w:t>Ansicht</w:t></w:r>
        <w:fldSimple w:instr="PAGE"><w:r><w:t>DO NOT TOUCH</w:t></w:r></w:fldSimple>
        <m:oMath><m:r><m:t>Beton</m:t></m:r></m:oMath>
        <w:r><w:drawing><w:txbxContent><w:p><w:r><w:t>Platte</w:t></w:r></w:p></w:txbxContent></w:drawing></w:r></w:p>
        <w:p><w:r><w:fldChar w:fldCharType="begin"/><w:instrText>REF section</w:instrText><w:fldChar w:fldCharType="separate"/><w:t>Beton field</w:t></w:r></w:p>
        <w:p><w:r><w:t>Beton field continues</w:t><w:fldChar w:fldCharType="end"/><w:t>Beton</w:t></w:r></w:p>
        </w:body></w:document>'''
        root = parse_xml(xml.encode())
        groups = [''.join(n.text or '' for n in group) for group in text_groups(root)]
        self.assertEqual(groups, ['Beton', 'Träger', 'Ansicht', 'Platte', 'Beton'])

    def test_powerpoint_fields_are_retained(self):
        root = parse_xml(f'<a:p xmlns:a="{A}"><a:r><a:t>Beton</a:t></a:r><a:fld type="slidenum"><a:t>3</a:t></a:fld><a:r><a:t>Träger</a:t></a:r></a:p>'.encode())
        self.assertEqual([''.join(n.text for n in g) for g in text_groups(root)], ['Beton', 'Träger'])

    def test_strict_namespaces_supported(self):
        for ns in (WS, AS):
            root = parse_xml(f'<p xmlns="{ns}"><r><t>Beton</t></r></p>'.encode())
            self.assertEqual(len(list(text_groups(root))), 1)

    def test_cancellation_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder)/'source.docx', Path(folder)/'English.docx'
            make_sample(source, 'Beton')
            target.write_bytes(b'previous file')
            with self.assertRaises(InterruptedError):
                translate_office(source, target, lambda s:s.replace('Beton','Concrete'), cancel=lambda:True)
            self.assertEqual(target.read_bytes(), b'previous file')
            self.assertFalse(target.with_suffix('.translations.txt').exists())

    def test_failed_verification_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder)/'source.pptx', Path(folder)/'English.pptx'
            make_sample(source, 'Beton')
            target.write_bytes(b'previous file')
            with patch('office.verify_office_output', side_effect=RuntimeError('verification failed')):
                with self.assertRaisesRegex(RuntimeError, 'verification failed'):
                    translate_office(source, target, lambda s:s.replace('Beton','Concrete'))
            self.assertEqual(target.read_bytes(), b'previous file')
            self.assertFalse(target.with_suffix('.translations.txt').exists())
            self.assertEqual(len(list(Path(folder).iterdir())), 2)

    def test_saved_verifier_rejects_changed_media_or_missing_text(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder)/'source.docx'
            make_sample(sample, 'Beton')
            with ZipFile(sample) as package:
                originals = {n:package.read(n) for n in package.namelist()}
            wrong = originals.copy()
            wrong['word/document.xml'] = b'missing text'
            with self.assertRaisesRegex(RuntimeError, 'changed text is missing'):
                verify_office_output(sample, originals, {'word/document.xml':(b'wrong',[])})
            with self.assertRaisesRegex(RuntimeError, 'unexpected change'):
                verify_office_output(sample, wrong, {})

    def test_extension_original_hardlink_and_invalid_package_checks(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'source.docx'
            make_sample(source, 'Beton')
            with self.assertRaisesRegex(ValueError, 'original'):
                translate_office(source, source, lambda s:s)
            link = Path(folder)/'link.docx'
            os.link(source, link)
            with self.assertRaisesRegex(ValueError, 'original'):
                translate_office(source, link, lambda s:s)
            with self.assertRaisesRegex(ValueError, 'same .docx'):
                translate_document(source, Path(folder)/'bad.pptx', lambda s:s)
            for extension in ('.doc','.ppt','.xlsx'):
                with self.assertRaisesRegex(ValueError, 'newer format'):
                    translate_document(source.with_suffix(extension), Path(folder)/'bad', lambda s:s)
            source.write_bytes(b'not a zip')
            with self.assertRaisesRegex(ValueError, 'unlocked'):
                translate_office(source, Path(folder)/'out.docx', lambda s:s)

    def test_empty_translation_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder)/'source.docx', Path(folder)/'English.docx'
            make_sample(source, 'Beton')
            with self.assertRaisesRegex(RuntimeError, 'empty text'):
                translate_office(source, target, lambda s:'')
            self.assertFalse(target.exists())

    def test_doctype_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'type declaration'):
            parse_xml(b'<!DOCTYPE doc [<!ENTITY a SYSTEM "file:///etc/passwd">]><doc>&a;</doc>')

    def test_review_terms_and_unchanged_report(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder)/'source.docx', Path(folder)/'English.docx'
            make_sample(source, 'Semelle')
            result = translate_office(source, target, EngineeringTranslator('fr', lambda s:s))
            self.assertGreater(result['review_labels'], 0)
            self.assertIn('REVIEW CONTEXT', Path(result['report']).read_text())


if __name__ == '__main__':
    unittest.main()
