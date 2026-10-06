"""Clean-process tests run against the compiled Windows executable."""
from pathlib import Path
import json
import tempfile
import tkinter as tk
import fitz
from offline import OfflineTranslator
from engine import translate_pdf

def run(report_path):
    report = {'passed':False,'checks':[]}
    try:
        window = tk.Tk()
        window.withdraw()
        window.update()
        window.destroy()
        report['checks'].append('Bundled desktop GUI loads')
        for language, sample in (('fr','Bonjour le monde'),('nl','Goedemorgen')):
            translate = OfflineTranslator(language)
            output = translate(sample)
            if not output.strip() or output.strip() == sample:
                raise RuntimeError(f'{language} translation did not change the source')
            report['checks'].append({'language':language,'sample':sample,'translation':output})
            with tempfile.TemporaryDirectory() as folder:
                source, destination = Path(folder)/'source.pdf', Path(folder)/'English.pdf'
                with fitz.open() as pdf:
                    page = pdf.new_page(width=595,height=420)
                    page.draw_line((20,180),(570,180))
                    page.insert_text((40,80),sample+' 200 mm - P1.42',fontsize=12)
                    pdf.save(source)
                before = source.read_bytes()
                result = translate_pdf(source,destination,translate,mode='notes')
                if result['translated'] < 1 or source.read_bytes() != before:
                    raise RuntimeError('PDF translation or source-preservation check failed')
                with fitz.open(destination) as pdf:
                    if '200 mm' not in pdf[0].get_text() or 'P1.42' not in pdf[0].get_text() or not list(pdf[0].annots()):
                        raise RuntimeError('PDF dimensions/codes/notes check failed')
                report['checks'].append(f'{language} PDF output and original preserved')
        report['passed'] = True
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        Path(report_path).write_text(json.dumps(report,indent=2),encoding='utf-8')
