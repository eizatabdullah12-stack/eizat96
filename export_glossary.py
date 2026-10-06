"""Builder only: export bundled terminology for user review."""
import csv
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))
from glossary import TERMS, AMBIGUOUS, TERM_CATEGORIES, fold

target = root / 'dist' / 'EngineeringGlossary.tsv'
target.parent.mkdir(exist_ok=True)
with target.open('w', newline='', encoding='utf-8-sig') as output:
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(['Language', 'Category', 'Source term', 'English terminology', 'Context review'])
    for language, entries in TERMS.items():
        for row in entries.strip().splitlines():
            source, english = row.split('|',1)
            notes = {fold(k):v for k,v in AMBIGUOUS[language].items()}
            writer.writerow([language, TERM_CATEGORIES[language].get(fold(source),'Core engineering'), source, english, notes.get(fold(source),'')])
