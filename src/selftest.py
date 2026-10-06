"""Clean-process tests run against the compiled Windows executable."""
from pathlib import Path
import json
import tempfile
import tkinter as tk
import fitz
from offline import OfflineTranslator
from engine import translate_pdf, protected_translate
from glossary import TERMS

def run(report_path, app_factory):
    report = {'passed':False,'checks':[]}
    try:
        window = tk.Tk()
        window.withdraw()
        app=app_factory(window)
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
        for language, sample in (('fr','Bonjour le monde'),('nl','Goedemorgen'),('de','Guten Morgen')):
            translate = OfflineTranslator(language)
            output = translate(sample)
            expected = 'hello' if language == 'fr' else 'morning'
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
            report['checks'].append(f'{language} bundled architecture/design/fixing vocabulary passed')
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
                    pdf.save(source)
                before = source.read_bytes()
                result = translate_pdf(source,destination,translate,mode='notes')
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
        report['passed'] = True
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
