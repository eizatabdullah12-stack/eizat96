"""Clean-process tests run against the compiled Windows executable."""
from pathlib import Path
import json
import tempfile
import tkinter as tk
import fitz
from offline import OfflineTranslator
from engine import translate_pdf, protected_translate
from glossary import TERMS
from documents import translate_document
from office_samples import make_sample
from office import parse_xml, TEXT
from zipfile import ZipFile

def run(report_path, app_factory):
    report = {'passed':False,'checks':[]}
    try:
        window = tk.Tk()
        window.withdraw()
        app=app_factory(window)
        from i18n import text, LANGUAGE_NAMES
        if app.ui_code != 'en' or app.target_code() != 'en':
            raise RuntimeError('English is not the default interface/output language')
        app.output_language.set(LANGUAGE_NAMES['fr'])
        for interface in ('fr','nl','de','en'):
            app.apply_interface(interface)
            window.update()
            if app.start.cget('text') != text(interface,'translate_save') or app.target_code() != 'fr':
                raise RuntimeError('Interface localization or independent output setting failed')
        app.output_language.set(LANGUAGE_NAMES['en'])
        report['checks'].append('Four interface languages load; English defaults and independent output choice passed')
        glossary_window,glossary_table=app.show_glossary()
        window.update()
        if len(glossary_table.get_children()) < 500:
            raise RuntimeError('Expanded terminology browser is incomplete')
        glossary_window.destroy()
        report['checks'].append('Searchable built-in terminology browser loads')
        window.update()
        window.destroy()
        report['checks'].append('Bundled desktop GUI loads')
        report['glossary_counts'] = {lang:len(data.strip().splitlines()) for lang,data in TERMS.items()}
        for language, sample in (('fr','Le chat dort sur le canapé'),
                                 ('nl','De kat slaapt op de bank'),
                                 ('de','Die Katze schläft auf dem Sofa')):
            translate = OfflineTranslator(language)
            output = translate(sample)
            expected = 'cat'
            if expected not in output.lower() or '\u2581' in output:
                raise RuntimeError(f'{language} translation did not change the source')
            report['checks'].append({'language':language,'sample':sample,'translation':output})
            engineering_sample, engineering_expected = {
                'fr': ('Poutre en béton armé', 'reinforced concrete beam'),
                'nl': ('Gewapende betonbalk', 'reinforced concrete beam'),
                'de': ('Stahlbetonträger', 'reinforced concrete beam'),
            }[language]
            engineering_output = translate(engineering_sample)
            if engineering_output.lower() != engineering_expected:
                raise RuntimeError(f'{language} engineering glossary check failed')
            report['checks'].append({'language':language,'engineering_source':engineering_sample,'translation':engineering_output})
            # These terms exist only in the separately bundled vocabulary file.
            # Passing inside the EXE verifies that the expanded catalogue ships.
            expanded = {
                'fr': [('pare-vapeur','vapour barrier'),('seuil de porte','door threshold'),('soudure d\'angle','fillet weld'),('état limite ultime','ultimate limit state')],
                'nl': [('dampscherm','vapour barrier'),('deurdorpel','door threshold'),('hoeklas','fillet weld'),('uiterste grenstoestand','ultimate limit state')],
                'de': [('Dampfsperre','vapour barrier'),('Türschwelle','door threshold'),('Kehlnaht','fillet weld'),('Grenzzustand der Tragfähigkeit','ultimate limit state')],
            }[language]
            for term, expected_term in expanded:
                if translate(term).casefold() != expected_term:
                    raise RuntimeError(f'{language} expanded terminology missing: {term}')
            hardware = {'fr': 'plaque de réglage', 'nl': 'regelplaat', 'de': 'Justierplatte'}[language]
            if translate(hardware).casefold() != 'adjustment plate':
                raise RuntimeError(f'{language} KORBO hardware glossary missing')
            report['checks'].append(f'{language} bundled architecture/design/fixing vocabulary passed')
            # Real models, XML parser and dispatch inside the packaged EXE.
            for extension, member in (('.docx', 'word/document.xml'), ('.pptx', 'ppt/slides/slide1.xml')):
                with tempfile.TemporaryDirectory() as office_folder:
                    office_source = Path(office_folder) / ('source' + extension)
                    office_target = Path(office_folder) / ('English' + extension)
                    make_sample(office_source, engineering_sample)
                    original_bytes = office_source.read_bytes()
                    office_result = translate_document(office_source, office_target, translate)
                    with ZipFile(office_target) as package:
                        xml = parse_xml(package.read(member))
                        translated_text = ''.join(n.text or '' for n in xml.iter() if n.tag in TEXT)
                    if (engineering_expected not in translated_text.lower() or
                            '200 mm - HEA200 - B500B' not in translated_text or
                            office_result['verified_groups'] < 2 or office_source.read_bytes() != original_bytes):
                        raise RuntimeError(f'{language} native {extension} translation check failed')
                    report['checks'].append(f'{language} native {extension} translation and package verification passed')
            label = {'fr':'Poutre','nl':'Balk','de':'Träger'}[language]
            protected = protected_translate(label+' ABC-VX42-3D_FV',translate)
            if 'ABC-VX42-3D_FV' not in protected or 'beam' not in protected.lower():
                raise RuntimeError('Complete product code protection failed')
            if language == 'de':
                for term, meaning in [('Teileliste','parts list'),('Pos.','item'),('Baugr.','assembly')]:
                    if translate(term).casefold() != meaning:
                        raise RuntimeError('German drawing table terminology failed')
            with tempfile.TemporaryDirectory() as folder:
                source, destination = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
                with fitz.open() as pdf:
                    page = pdf.new_page(width=595,height=420)
                    page.draw_line((20,180),(570,180))
                    page.insert_text((40,80),sample+' 200 mm - P1.42',fontsize=12)
                    # Use Latin-1-safe labels with the built-in PDF font.
                    label = {'fr':'Poutre en beton arme','nl':'Gewapende betonbalk','de':'Stahlbetonbalken'}[language]
                    page.insert_text((40,130), label+' 300 mm - HEA200 - B500B', fontsize=12)
                    ambiguous = {'fr':'Semelle','nl':'Plaat','de':'Platte'}[language]
                    page.insert_text((40,160), ambiguous, fontsize=12)
                    pdf.save(source,use_objstms=1,garbage=3)
                before = source.read_bytes()
                result = translate_pdf(source,destination,translate,mode='notes')
                if result['verified_notes'] != result['notes'] or result['verified_replaced'] != result['replaced']:
                    raise RuntimeError('Saved-file readback verification failed')
                if 'Source language:' not in Path(result['report']).read_text(encoding='utf-8'):
                    raise RuntimeError('Source-language report missing')
                if result['translated'] < 1 or source.read_bytes() != before:
                    raise RuntimeError('PDF translation or source-preservation check failed')
                with fitz.open(destination) as pdf:
                    if '200 mm' not in pdf[0].get_text() or 'P1.42' not in pdf[0].get_text() or not list(pdf[0].annots()):
                        raise RuntimeError('PDF dimensions/codes/notes check failed')
                report['checks'].append(f'{language} PDF output and original preserved')
                if result['glossary_terms'] < 1 or result['review_labels'] < 1 or 'REVIEW CONTEXT' not in Path(result['report']).read_text(encoding='utf-8'):
                    raise RuntimeError('Engineering glossary/report check failed')
                # Exercise the default replacement path with real inference.
                replace_destination = Path(folder)/'English-replaced.pdf'
                replaced = translate_pdf(source,replace_destination,translate,mode='replace')
                if replaced['verified_replaced'] != replaced['replaced'] or 'PDF SHA256:' not in Path(replaced['report']).read_text(encoding='utf-8'):
                    raise RuntimeError('Verified replacement PDF identity missing')
                with fitz.open(replace_destination) as pdf:
                    text = pdf[0].get_text()
                    notes = '\n'.join(a.info.get('content','') for a in (pdf[0].annots() or []))
                    if expected not in (text + notes).lower() or engineering_expected not in (text + notes).lower() or '200 mm' not in text or 'P1.42' not in text or 'HEA200' not in text or 'B500B' not in text:
                        raise RuntimeError('Translated PDF labels or protected values are missing')
                report['checks'].append(f'{language} default PDF replacement mode passed')
                # Reproduce a rotated CAD sheet with small legend text.
                rotated_source, rotated_target = Path(folder)/'rotated.pdf', Path(folder)/'rotated-English.pdf'
                with fitz.open() as pdf:
                    page = pdf.new_page(width=420,height=595)
                    page.set_rotation(270)
                    page.insert_text((100,80),label,fontsize=5.9,rotate=270)
                    pdf.save(rotated_source)
                result = translate_pdf(rotated_source,rotated_target,translate)
                with fitz.open(rotated_target) as pdf:
                    if result['replaced'] != 1 or pdf[0].rotation != 270 or engineering_expected not in pdf[0].get_text().lower():
                        raise RuntimeError('Rotated small CAD label was not replaced on drawing')
                report['checks'].append(f'{language} rotated small CAD label replacement passed')
        # Verify language detection, lazy model routing and native Office output
        # from a mixed French/Dutch/German/English paragraph inside the EXE.
        from automatic import AutoTranslator
        mixed = 'Plaque de réglage. Regelplaat. Justierplatte. This drawing is for information only.'
        auto = AutoTranslator()
        rendered = protected_translate(mixed, auto)
        if rendered != 'Adjustment plate. Adjustment plate. Adjustment plate. This drawing is for information only.':
            raise RuntimeError('Automatic mixed-language paragraph routing failed')
        for extension in ('.docx', '.pptx'):
            with tempfile.TemporaryDirectory() as folder:
                source, target = Path(folder)/('mixed'+extension), Path(folder)/('English'+extension)
                make_sample(source, mixed)
                result = translate_document(source,target,AutoTranslator())
                if not {'French','Dutch','German','English'}.issubset(result['detection']['segments']):
                    raise RuntimeError('Mixed-language file report is incomplete')
                report['checks'].append(f'Automatic mixed-language {extension} translation and English preservation passed')
        report['checks'].append('Bundled language detector and mixed-language routing passed')
        from directional import DirectionalTranslator
        for target,label in [('fr','Plaque de réglage'),('nl','Regelplaat'),('de','Justierplatte')]:
            translator=DirectionalTranslator('en',target)
            if protected_translate('Adjustment plate 200 mm - KORBO M12',translator) != label+' 200 mm - KORBO M12':
                raise RuntimeError('Target-language glossary or code protection failed')
            unknown=protected_translate('The cat sleeps on the sofa.',translator)
            if {'fr':'chat','nl':'kat','de':'katze'}[target] not in unknown.casefold():
                raise RuntimeError('Bundled outbound inference failed: '+target)
            with tempfile.TemporaryDirectory() as folder:
                source,destination=Path(folder)/'source.docx',Path(folder)/'translated.docx'
                make_sample(source,'Adjustment plate')
                result=translate_document(source,destination,translator)
                if result['translated'] < 1:
                    raise RuntimeError('Native target-language output failed')
            report['checks'].append(f'English to {target} real model, glossary, codes and native output passed')
        report['passed'] = True
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
