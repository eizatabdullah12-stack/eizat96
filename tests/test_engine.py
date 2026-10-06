import sys
from pathlib import Path
import tempfile
import unittest
import fitz
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from engine import protected_translate, translate_pdf, fit_text
from glossary import EngineeringTranslator

class PDFChecks(unittest.TestCase):
    def test_rotated_page_and_all_label_directions(self):
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
            with fitz.open() as doc:
                page = doc.new_page(width=420, height=595)
                page.set_rotation(270)
                page.draw_line((15,15),(400,580))
                for angle, point in ((0,(50,80)),(90,(150,220)),(180,(350,350)),(270,(300,420))):
                    page.insert_text(point, 'Poutres beton arme', fontsize=5.9, rotate=angle)
                page.insert_text((30,500),'NI : +260',fontsize=6,rotate=270)
                doc.save(src)
            before = src.read_bytes()
            result = translate_pdf(src,dst,EngineeringTranslator('fr',lambda s:s))
            self.assertEqual(result['replaced'],4)
            self.assertEqual(result['notes'],0)
            self.assertEqual(result['retained'],1)
            self.assertEqual(src.read_bytes(),before)
            with fitz.open(src) as source, fitz.open(dst) as output:
                self.assertEqual(output[0].rotation,270)
                self.assertEqual(output[0].rect,source[0].rect)
                self.assertEqual(output[0].get_drawings(),source[0].get_drawings())
                self.assertEqual(output[0].get_text().count('Reinforced concrete beams'),4)
                directions = {line['dir'] for block in output[0].get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] if 'Reinforced' in ''.join(s['text'] for s in line['spans'])}
                self.assertEqual(directions,{(1.,0.),(0.,-1.),(-1.,0.),(0.,1.)})
                self.assertIn('NI : +260',output[0].get_text())

    def test_small_cad_font_box(self):
        # A CAD font can report a box only 5.2pt high. Helvetica needs a
        # proportional reduction; the old fixed 5pt floor never fitted it.
        fs = fit_text(fitz.Rect(20,20,100,25.2),'Legend',5.2)
        self.assertIsNotNone(fs)
        self.assertLess(fs,5)

    def test_unchanged_and_note_reason_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
            self.fixture(src)
            result = translate_pdf(src,dst,lambda s:s.replace('Poutre','A very long translation '*30))
            report = Path(result['report']).read_text(encoding='utf-8')
            self.assertEqual(result['unchanged'],2)
            self.assertIn('Original: Beton 200 mm - P1.42',report)
            self.assertIn('UNCHANGED',report)
            self.assertIn('NOTE - translation exceeds label space',report)

    def test_identifier_preservation(self):
        from engine import reference_label
        for text in ('PD 6+16cm','BA 15x20cm','NI : +260','HBP 17+5cm','I.A','C 1.7','info@example.org','www.example.org','Fb = 15 N/mm²','L.DON','PC 3a','60xØ'):
            self.assertTrue(reference_label(text),text)
        for text in ('Poutres beton arme','Couvrant RDC','colonne','Légende'):
            self.assertFalse(reference_label(text),text)

    def test_engineering_unicode_symbols(self):
        from engine import LABEL_FONT, LABEL_FONT_NAME
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
            with fitz.open() as doc:
                page=doc.new_page()
                page.insert_font(fontname=LABEL_FONT_NAME,fontbuffer=LABEL_FONT.buffer)
                page.insert_text((30,60),'Beton 200 μm - Ø20',fontname=LABEL_FONT_NAME,fontsize=12)
                doc.save(src)
            result=translate_pdf(src,dst,lambda s:s.replace('Beton','Concrete'))
            self.assertEqual(result['replaced'],1)
            with fitz.open(dst) as doc:
                self.assertIn('Concrete 200 μm - Ø20',doc[0].get_text())

    def fixture(self, path):
        with fitz.open() as doc:
            p = doc.new_page(width=595, height=420)
            p.draw_rect(fitz.Rect(30, 30, 560, 370))
            p.draw_line((30,160), (560,160))
            p.insert_text((50,80), "Beton 200 mm - P1.42", fontsize=12)
            p.insert_text((50,130), "Poutre", fontsize=12)
            p.insert_text((50,220), "Long label", fontsize=12)
            doc.save(path)

    def test_codes(self):
        result = protected_translate("Beton 200 mm - P1.42", lambda s:s.replace("Beton", "Concrete"))
        self.assertEqual(result, "Concrete 200 mm - P1.42")

    def test_geometry_fallback_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/"source.pdf", Path(folder)/"English.pdf"
            self.fixture(src)
            before = src.read_bytes()
            result = translate_pdf(src, dst, lambda s:s.replace("Beton", "Concrete").replace("Poutre", "Beam").replace("Long label", "An extremely long translation "*20))
            self.assertEqual(src.read_bytes(), before)
            self.assertEqual(result["translated"], 3)
            self.assertGreaterEqual(result["notes"], 1)
            with fitz.open(src) as original, fitz.open(dst) as output:
                self.assertEqual(output[0].rect, original[0].rect)
                # Annotation icons add vector paths; original geometry must remain.
                retained = output[0].get_drawings()[:len(original[0].get_drawings())]
                self.assertEqual(retained, original[0].get_drawings())
                self.assertIn("200 mm", output[0].get_text())
                self.assertIn("P1.42", output[0].get_text())
                self.assertTrue(list(output[0].annots()))

    def test_scanned_and_cancel(self):
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/"source.pdf", Path(folder)/"English.pdf"
            with fitz.open() as doc:
                doc.new_page()
                doc.save(src)
            with self.assertRaises(ValueError):
                translate_pdf(src, dst, lambda s:s)
            self.assertFalse(dst.exists())
            self.fixture(src)
            with self.assertRaises(InterruptedError):
                translate_pdf(src, dst, lambda s:s, cancel=lambda:True)
            self.assertFalse(dst.exists())

    def test_notes_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            src, dst = Path(folder)/"source.pdf", Path(folder)/"English.pdf"
            self.fixture(src)
            translate_pdf(src, dst, lambda s:s.replace("Poutre", "Beam"), mode="notes")
            with fitz.open(src) as original, fitz.open(dst) as output:
                self.assertEqual(original[0].get_text(), output[0].get_text())

if __name__ == "__main__":
    unittest.main()
