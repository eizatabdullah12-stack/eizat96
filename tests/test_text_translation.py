from pathlib import Path
import queue
import sys
import threading
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from directional import DirectionalTranslator
from glossary import EngineeringTranslator, TERMS
from text_translation import TextSession, TextWorker, MAX_TEXT_CHARS


def no_model(value):
    raise AssertionError('Known text unexpectedly reached model: '+repr(value))


def translator(source,target):
    return DirectionalTranslator(source,target,
        factory=lambda code:EngineeringTranslator(code,no_model),
        outbound_factory=lambda code:no_model)


class TextTranslationTests(unittest.TestCase):
    def test_mixed_text_keeps_paragraphs_codes_and_indentation(self):
        session=TextSession(translator)
        source='  Plaque de réglage 200 mm - KORBO M12.\r\n\nRegelplaat.\tJustierplatte.\nAdjustment plate.'
        result=session.translate(source)
        self.assertEqual(result['text'],'  Adjustment plate 200 mm - KORBO M12.\r\n\nAdjustment plate.\tAdjustment plate.\nAdjustment plate.')
        self.assertEqual(set(result['languages']),{'fr','nl','de','en'})

    def test_typed_text_supports_all_output_languages(self):
        session=TextSession(translator)
        for code,label in [('en','Adjustment plate'),('fr','Plaque de réglage'),('nl','Regelplaat'),('de','Justierplatte')]:
            self.assertEqual(session.translate('Plaque de réglage. Regelplaat. Justierplatte. Adjustment plate.',target=code)['text'],'. '.join([label]*4)+'.')

    def test_context_notes_and_unsupported_text_are_visible(self):
        session=TextSession(translator)
        source='Semelle.\nEste documento está escrito en español y contiene instrucciones de instalación.'
        result=session.translate(source)
        self.assertEqual(result['text'],source)
        self.assertTrue(any('semelle' in note.casefold() for note in result['reviews']))
        self.assertTrue(any('unsupported' in note for note in result['reviews']))

    def test_blank_text_limits_and_cancel_do_not_load_models(self):
        def forbidden(*args): raise AssertionError('Should not load a model')
        session=TextSession(forbidden)
        self.assertEqual(session.translate(' \n')['text'],' \n')
        with self.assertRaises(ValueError): session.translate('x'*(MAX_TEXT_CHARS+1))
        with self.assertRaises(InterruptedError): session.translate('Bonjour',cancel=lambda:True)

    def test_new_glossary_phrases_work_without_inference(self):
        self.assertGreaterEqual(sum(len(data.strip().splitlines()) for data in TERMS.values()),5000)
        cases={
            'fr':[('Merci pour votre aide','Thank you for your help'),('Presse plieuse','Press brake'),('Vérifier avant fabrication','Check before fabrication')],
            'nl':[('Bedankt voor uw hulp','Thank you for your help'),('Kantbank','Press brake'),('Controle van de doorbuiging','Deflection verification')],
            'de':[('Vielen Dank für Ihre Hilfe','Thank you for your help'),('Abkantpresse','Press brake'),('Bohrlochreinigung','Hole cleaning')]}
        session=TextSession(translator)
        for code,rows in cases.items():
            for source,expected in rows:
                with self.subTest(code=code,source=source):
                    self.assertEqual(session.translate(source,source=code)['text'],expected)

    def test_latest_edit_replaces_pending_work_and_discards_stale_result(self):
        started=threading.Event(); release=threading.Event(); messages=queue.Queue(); seen=[]
        class Session:
            def translate(self,value,source,target,cancel):
                seen.append(value)
                if value=='old':
                    started.set()
                    if not release.wait(3): raise RuntimeError('Test timed out')
                return {'text':value,'languages':{},'reviews':[]}
        worker=TextWorker(messages.put,session_factory=Session)
        try:
            worker.submit(1,'old','auto','en')
            self.assertTrue(started.wait(3))
            worker.submit(2,'intermediate','auto','en')
            worker.submit(3,'latest','auto','fr')
            release.set()
            kind,(generation,result,error)=messages.get(timeout=3)
            self.assertEqual((kind,generation,result['text'],error),('text_done',3,'latest',None))
            self.assertEqual(seen,['old','latest'])
            self.assertTrue(messages.empty())
        finally:
            release.set(); worker.close()


if __name__=='__main__':unittest.main()
