import sys
from pathlib import Path
import tempfile
import unittest
import fitz
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from engine import protected_translate, translate_pdf

class PDFChecks(unittest.TestCase):
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
