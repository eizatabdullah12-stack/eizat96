"""Shared UI checks for source tests and the compiled Windows app."""
import os
from pathlib import Path
import tempfile
from i18n import LANGUAGE_NAMES
from personal_glossary import PersonalStore, entry_key


def exercise(app):
    previous=os.environ.get('EIZAT_GLOSSARY_PATH')
    try:
        with tempfile.TemporaryDirectory() as folder:
            os.environ['EIZAT_GLOSSARY_PATH']=str(Path(folder)/'personal.json')
            for locale in ('en','fr','nl','de'):
                app.apply_interface(locale)
                editor=app.show_personal_glossary(); editor.window.withdraw()
                app.root.update()
                if editor.buttons['personal_save'].cget('text')!=app.T('personal_save'):
                    raise RuntimeError('Personal glossary localization failed')
                editor.window.destroy()
            app.apply_interface('en')
            editor=app.show_personal_glossary(); editor.window.withdraw()
            editor.fields['source'].set(LANGUAGE_NAMES['nl'])
            editor.fields['target'].set(LANGUAGE_NAMES['en'])
            editor.fields['term'].set('chape')
            editor.fields['translation'].set('my approved screed')
            editor.buttons['personal_save'].invoke(); app.root.update()
            store=PersonalStore()
            if store.read()[0]['translation']!='my approved screed':
                raise RuntimeError('Personal glossary Save button failed')
            editor.window.destroy()
            editor=app.show_personal_glossary(); editor.window.withdraw()
            item=editor.table.get_children()[0]; editor.table.selection_set(item); editor.select()
            if editor.fields['translation'].get()!='my approved screed':
                raise RuntimeError('Personal glossary did not survive reopen')
            editor.fields['translation'].set('my corrected screed')
            editor.buttons['personal_save'].invoke(); app.root.update()
            backup=Path(folder)/'export.json'; store.export(backup)
            if PersonalStore(backup).read()[0]['translation']!='my corrected screed':
                raise RuntimeError('Personal glossary backup failed')
            # Deliver a service result without making a network request. Choosing
            # it must only fill the form; it must not persist until Save.
            editor.lookup_events.put((editor.lookup_generation,['online candidate'],None)); editor.poll()
            editor.candidates.selection_set(0); editor.choose_candidate()
            if editor.fields['translation'].get()!='online candidate' or store.read()[0]['translation']!='my corrected screed':
                raise RuntimeError('Online suggestions must require explicit approval')
            stale=editor.lookup_generation
            editor.fields['term'].set('hourdis')
            editor.lookup_events.put((stale,['obsolete candidate'],None)); editor.poll()
            if editor.candidates.size():
                raise RuntimeError('Stale online results were accepted for another term')
            editor.window.destroy()
            from text_translation import TextSession
            result=TextSession().translate('chape','nl','en',mode='engineering')
            if result['text']!='my corrected screed':
                raise RuntimeError('Saved glossary is not active in actual TextSession')
            store.delete(entry_key(store.read()[0])); store.import_backup(backup)
            if store.read()[0]['translation']!='my corrected screed':
                raise RuntimeError('Personal glossary delete/import failed')
    finally:
        if previous is None: os.environ.pop('EIZAT_GLOSSARY_PATH',None)
        else: os.environ['EIZAT_GLOSSARY_PATH']=previous
        app.apply_interface('en')
