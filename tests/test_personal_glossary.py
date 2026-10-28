import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from personal_glossary import PersonalStore, with_personal, entry_key
from directional import DirectionalTranslator
from glossary import EngineeringTranslator
from text_translation import TextSession
from engine import protected_translate
from documents import translate_document
from office_samples import make_sample
from office import TEXT, parse_xml
from zipfile import ZipFile
from online_lookup import lookup, search_url


def row(term='chape', translation='floor screed', source='nl', target='en', scope='engineering'):
    return dict(source=source,target=target,term=term,translation=translation,scope=scope,context='',url='')


def translator(source='nl', target='en'):
    def fail(*args): raise AssertionError('Known personal term must not load a model')
    return DirectionalTranslator(source,target,factory=lambda language: EngineeringTranslator(language,fail),outbound_factory=fail)


class PersonalGlossaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'user'/'terms.json'; self.store=PersonalStore(self.path)
        self.env=patch.dict(os.environ,{'EIZAT_GLOSSARY_PATH':str(self.path)})
        self.env.start(); self.addCleanup(self.env.stop)

    def test_save_restart_edit_delete_and_import_preserves_corrections(self):
        self.store.upsert(row()); self.assertEqual(PersonalStore(self.path).read()[0]['translation'],'floor screed')
        backup=Path(self.temp.name)/'backup.json'; self.store.export(backup)
        old=self.store.read()[0]; self.store.upsert(row(translation='cement screed'),entry_key(old))
        self.assertEqual(self.store.import_backup(backup),0)
        self.assertEqual(self.store.read()[0]['translation'],'cement screed')
        self.store.delete(entry_key(old)); self.assertEqual(self.store.read(),[])
        self.assertEqual(self.store.import_backup(backup),1)
        self.assertEqual(self.store.read()[0]['translation'],'floor screed')

    def test_invalid_import_and_failed_disk_replace_do_not_lose_saved_terms(self):
        self.store.upsert(row()); before=self.path.read_bytes()
        bad=Path(self.temp.name)/'bad.json'; bad.write_text('{"version":1,"entries":[{}]}')
        with self.assertRaises(ValueError): self.store.import_backup(bad)
        self.assertEqual(self.path.read_bytes(),before)
        with patch('personal_glossary.os.replace',side_effect=OSError('disk error')):
            with self.assertRaises(OSError): self.store.upsert(row(translation='wrong'))
        self.assertEqual(self.path.read_bytes(),before)
        self.path.write_text('broken')
        with self.assertRaises(ValueError): self.store.upsert(row())
        self.assertEqual(self.path.read_text(),'broken')
        good=Path(self.temp.name)/'good.json'; good.write_bytes(before)
        self.store.restore_backup(good)
        self.assertEqual(self.store.read()[0]['translation'],'floor screed')
        preserved=list(self.path.parent.glob('*.unreadable-*'))
        self.assertEqual(len(preserved),1); self.assertEqual(preserved[0].read_text(),'broken')

    def test_saved_terms_override_builtins_and_mode_specific_beats_both(self):
        rows=[row(translation='general screed',scope='both'),row(translation='cement screed')]
        self.assertEqual(protected_translate('chape 200 mm - KORBO M12',with_personal(translator(),rows)), 'cement screed 200 mm - KORBO M12')
        self.assertEqual(with_personal(translator(),rows,'conversation')('chape'),'general screed')
        self.assertEqual(with_personal(translator(),[])('chape'),'screed')

    def test_all_language_pairs_longest_whole_phrase_unicode_and_wrapping(self):
        for source in ('en','nl','fr','de'):
            for target in ('en','nl','fr','de'):
                if source==target: continue
                rows=[row('terme spécial','custom translation',source,target),row('terme','short',source,target)]
                t=with_personal(translator(source,target),rows)
                self.assertEqual(protected_translate('terme spécial 200 mm',t),'custom translation 200 mm')
        t=with_personal(translator('fr'),[row('paroi spéciale','custom wall','fr')])
        self.assertEqual(t('PAROI SPÉCIALE'),'CUSTOM WALL')
        self.assertEqual(t('paroi spe\u0301ciale'),'custom wall')
        self.assertEqual(t('paroi\nspéciale'),'custom wall')
        self.assertEqual(list(t.matches('murparoi spéciale')),[])

    def test_auto_language_and_target_language_retention(self):
        rows=[row('chape','floor screed'),row('mur béton','custom concrete wall','fr')]
        t=with_personal(translator('auto'),rows)
        self.assertEqual(protected_translate('chape\nmur béton',t),'floor screed\ncustom concrete wall')
        self.assertEqual(t('concrete wall'),'concrete wall')
        self.assertEqual(with_personal(translator('nl','nl'),rows)('chape'),'chape')

    def test_text_session_refreshes_after_save_in_both_modes_and_delete(self):
        session=TextSession(factory=translator,conversation_factory=translator)
        self.store.upsert(row()); self.assertEqual(session.translate('chape','nl','en')['text'],'floor screed')
        self.store.upsert(row(translation='custom screed'))
        self.assertEqual(session.translate('chape','nl','en')['text'],'custom screed')
        self.store.upsert(row(translation='conversation screed',scope='conversation'))
        self.assertEqual(session.translate('chape','nl','en',mode='conversation')['text'],'conversation screed')
        self.store.delete(entry_key(row())); self.assertEqual(session.translate('chape','nl','en')['text'],'screed')

    def test_personal_glossary_applies_to_pdf_word_and_powerpoint(self):
        import fitz
        rows=[row('chape spéciale','custom floor screed','fr')]
        for ext in ('.pdf','.docx','.pptx'):
            source=Path(self.temp.name)/('source'+ext); target=source.with_name('translated'+ext)
            if ext=='.pdf':
                with fitz.open() as pdf:
                    pdf.new_page().insert_text((40,60),'chape spéciale 200 mm - M12',fontsize=10); pdf.save(source)
            else: make_sample(source,'chape spéciale 200 mm - M12')
            before=source.read_bytes(); result=translate_document(source,target,with_personal(translator('fr'),rows))
            if ext=='.pdf':
                with fitz.open(target) as pdf:
                    output=pdf[0].get_text()+'\n'+'\n'.join(a.info.get('content','') for a in (pdf[0].annots() or []))
            else:
                with ZipFile(target) as package:
                    member='word/document.xml' if ext=='.docx' else 'ppt/slides/slide1.xml'
                    output=''.join(n.text or '' for n in parse_xml(package.read(member)).iter() if n.tag in TEXT)
            self.assertIn('custom floor screed',output); self.assertIn('200 mm - M12',output)
            self.assertGreater(result['translated'],0); self.assertEqual(source.read_bytes(),before)

    def test_long_personal_abbreviation_phrase_not_split(self):
        t=with_personal(translator('nl'),[row('kleur cfr. monster','colour as sample')])
        self.assertEqual(list(t.segments('kleur cfr. monster')), [('kleur cfr. monster',False)])
        self.assertEqual(protected_translate('kleur cfr. monster',t),'colour as sample')

    def test_online_response_requires_review_and_never_writes_glossary(self):
        seen=[]
        def open_request(request,timeout):
            seen.append((request.full_url,timeout))
            return io.BytesIO(json.dumps({'responseStatus':200,'responseData':{'translatedText':'floor &amp; screed'},'matches':[{'translation':'floor screed'}]}).encode())
        self.assertEqual(lookup('chape','nl','en',open_request),['floor & screed','floor screed'])
        self.assertIn('q=chape&langpair=nl%7Cen',seen[0][0]); self.assertEqual(seen[0][1],15)
        self.assertFalse(self.path.exists())
        with self.assertRaises(ValueError): lookup('é'*251,'fr','en',open_request)
        self.assertEqual(len(seen),1)
        with self.assertRaises(ValueError): lookup('chape','nl','en',lambda *a,**k:io.BytesIO(b'{"responseStatus":429,"responseDetails":"daily limit"}'))
        self.assertIn('%22chape%22',search_url('chape','nl','en','floor'))


if __name__=='__main__': unittest.main()
