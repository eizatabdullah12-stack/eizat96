"""One dispatch path for PDF, Word and PowerPoint documents."""
from pathlib import Path
from engine import translate_pdf
from office import translate_office

SUPPORTED = {'.pdf': 'PDF', '.docx': 'Word', '.pptx': 'PowerPoint'}


def translate_document(source, destination, translate, mode='replace',
                       progress=lambda *args: None, cancel=lambda: False):
    extension = Path(source).suffix.lower()
    if extension not in SUPPORTED:
        raise ValueError('Choose a PDF, Word (.docx) or PowerPoint (.pptx) file. Save older .doc/.ppt files in the newer format first.')
    if Path(destination).suffix.lower() != extension:
        raise ValueError(f'The output must use the same {extension} file extension as the source.')
    if extension == '.pdf':
        result = translate_pdf(source, destination, translate, mode, progress, cancel)
        result.update(format=extension, file_sha256=result['pdf_sha256'])
    else:
        result = translate_office(source, destination, translate, progress, cancel)
    if hasattr(translate, 'detection_summary'):
        result['detection'] = translate.detection_summary()
        summary = result['detection']
        with Path(result['report']).open('a', encoding='utf-8') as report:
            report.write('\nAUTO / MIXED LANGUAGE SUMMARY\n' +
                         '; '.join(f'{name}: {count} segments' for name,count in summary['segments'].items()) +
                         f"\nSegments needing language review: {summary['review_segments']}\n{summary['note']}\n")
    return result
