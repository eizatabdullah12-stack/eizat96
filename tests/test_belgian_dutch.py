"""Generic Belgian drawing labels; no customer drawing or project data is stored."""
from pathlib import Path
import sys
import tempfile
import unittest
import fitz
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from glossary import EngineeringTranslator
from directional import DirectionalTranslator
from engine import protected_translate, translate_pdf, coalesce_glossary_lines


def no_model(value):
    raise AssertionError('Recorded drawing label reached model: '+repr(value))


def automatic():
    return DirectionalTranslator('auto','en',factory=lambda code:EngineeringTranslator(code,no_model))


class BelgianDutchTests(unittest.TestCase):
    def test_flemish_labels_and_abbreviations_are_detected_with_dimensions(self):
        tr=automatic()
        cases={
            'vloerpas -0.90':'floor level -0.90',
            'onderz fund -1.43':'underside of foundation -1.43',
            'maaiveld':'ground level',
            'oorspronkelijk maaiveld':'existing ground level',
            'polierbeton 120mm':'power-floated concrete 120mm',
            'hellingschape gemiddeld 100mm':'screed to falls, average thickness 100mm',
            'potten en balken 200mm':'beam-and-block floor 200mm',
            'snelbouwsteen 14cm':'clay masonry block 14cm',
            'parementsteen 6,5cm':'facing brick 6,5cm',
            'SNEDES':'SECTIONS',
            'RAAMBORDEREL':'WINDOW SCHEDULE',
            'raamgeheel':'window assembly',
            'kleur cfr. raamprofielen':'colour to match window profiles',
        }
        for original,expected in cases.items():
            with self.subTest(original=original):
                self.assertEqual(tr.detect(original)[0],'nl')
                self.assertEqual(protected_translate(original,tr),expected)

    def test_joinery_compounds_override_structural_kip_without_changing_it(self):
        tr=EngineeringTranslator('nl',no_model)
        for source in ('draai-kip raam','draai-kipraam','draaikipraam','draaikiepraam','draai kip raam','draai-kiepraam'):
            self.assertEqual(tr(source),'tilt-and-turn window')
        self.assertEqual(tr('kip'),'lateral torsional buckling')
        self.assertEqual(tr('onzichtbare scharnieren'),'concealed hinges')
        self.assertEqual(tr('onzicbtbare scharnieren'),'concealed hinges')
        self.assertTrue(tr.review_notes('onzicbtbare scharnieren'))

    def test_generic_drawing_labels_are_verified_in_saved_pdf(self):
        labels={'vloerpas -0.90':'floor level -0.90',
                'polierbeton 120mm':'power-floated concrete 120mm',
                'draai-kip raam':'tilt-and-turn window',
                'raamborderel':'window schedule'}
        with tempfile.TemporaryDirectory() as directory:
            source,target=Path(directory)/'drawing.pdf',Path(directory)/'english.pdf'
            with fitz.open() as document:
                page=document.new_page(width=800,height=600)
                for i,value in enumerate(labels):
                    page.insert_text((40,80+i*70),value,fontsize=10)
                document.save(source)
            original=source.read_bytes()
            result=translate_pdf(source,target,automatic())
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(result['translated'],len(labels))
            with fitz.open(target) as document:
                rendered='\n'.join(p.get_text()+'\n'+'\n'.join(a.info.get('content','') for a in (p.annots() or [])) for p in document)
            for expected in labels.values():
                self.assertIn(expected,rendered)

    def test_wrapped_known_phrase_translates_in_saved_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target=Path(directory)/'wrapped.pdf',Path(directory)/'english.pdf'
            with fitz.open() as document:
                page=document.new_page()
                page.insert_text((40,80),'vrije\nhoogte 246cm',fontsize=10)
                document.save(source)
            result=translate_pdf(source,target,automatic())
            self.assertEqual(result['translated'],1)
            with fitz.open(target) as document:
                text=document[0].get_text()+'\n'+'\n'.join(a.info.get('content','') for a in (document[0].annots() or []))
            self.assertIn('clear height 246cm',' '.join(text.split()))
            self.assertNotIn('vrije',text)

    def test_wrapped_join_does_not_cross_distant_columns(self):
        def line(value,x,y):
            return {'bbox':(x,y,x+90,y+10),'dir':(1,0),'spans':[{'text':value,'font':'Arial','size':10}]}
        tr=EngineeringTranslator('nl',no_model)
        nearby=[line('vrije',40,40),line('hoogte',40,52)]
        self.assertEqual(len(coalesce_glossary_lines(nearby,tr)),1)
        distant=[line('vrije',40,40),line('hoogte',300,52)]
        self.assertEqual(len(coalesce_glossary_lines(distant,tr)),2)


if __name__=='__main__':
    unittest.main()
