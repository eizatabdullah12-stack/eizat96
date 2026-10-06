"""Clean-process tests run against the compiled Windows executable."""
from pathlib import Path
import json
import tempfile
import tkinter as tk
import fitz
from offline import OfflineTranslator
from engine import translate_pdf

def run(report_path, app_factory):
    report = {'passed':False,'checks':[]}
    try:
        window = tk.Tk()
        window.withdraw()
        app_factory(window)
        window.update()
        window.destroy()
        report['checks'].append('Bundled desktop GUI loads')
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
        report['passed'] = True
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
