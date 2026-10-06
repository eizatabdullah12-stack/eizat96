"""Builder only: export bundled terminology for user review."""
import csv
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))
from glossary import TERMS, AMBIGUOUS

target = root / 'dist' / 'EngineeringGlossary.tsv'
target.parent.mkdir(exist_ok=True)
with target.open('w', newline='', encoding='utf-8-sig') as output:
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(['Language', 'Source term', 'English terminology', 'Context review'])
    for language, entries in TERMS.items():
        for row in entries.strip().splitlines():
            source, english = row.split('|',1)
            writer.writerow([language, source, english, AMBIGUOUS[language].get(source,'')])
