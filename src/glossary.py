"""Deterministic drawing terminology before general machine translation.

This is a terminology layer, not a drawing/geometry interpreter. Phrases are
matched longest first, on word boundaries, with accent/case normalization.
Ambiguous labels are retained or flagged instead of assigning a material or
structural function that the label does not actually specify.
"""
import re
import unicodedata
import csv
from pathlib import Path


TERMS = {
    'fr': '''
le bureau d'études|the engineering office
du bureau d'études|of the engineering office
l'entrepreneur|the contractor
l'assise des fondations|the foundation bearing stratum
le plan de pose|the installation layout
la pose du ferraillage|the placement of reinforcement
du fabricant|of the manufacturer
sous réserve du dimensionnement|subject to design by
pour tout élément préfabriqué|for any precast component
recouvrement des bandes|sheet overlaps
hydrofuge|water-resistant
asselets|padstones
asselet|padstone
listing asselets|padstone schedule
poutrain entrevous|beam-and-block floor
poutrains-entrevous|beam-and-block floors
pieux|piles
micropieux|micropiles
faux-puits|concrete-filled foundation shafts
socles|plinths
semelles|semelles
grugeage|notching
assemblage|connection
cotation|dimensions
mailles complètes|complete mesh openings
aciers pour béton armé|reinforcing steel
aciers profilés|structural steel sections
chape de compression|structural topping
plan de pose|installation layout
bureau d'études|engineering office
maître de l'ouvrage|client
terrassement|earthworks
bétons de fondations|foundation concrete
seront coulés|will be cast
assise des fondations|foundation bearing stratum
recouvrement des armatures|reinforcement lap splices
décoffrage|formwork removal
délavage du béton|washout of concrete
radiers|raft foundations
béton hydrofuge|water-resistant concrete
entrepreneur|contractor
note de calcul|design calculation
chargé d'affaires|project manager
auteur de projet|designer
objet du plan|drawing title
indice|revision
révision|revision
éch|scale
première diffusion|first issue
poutres béton armé|reinforced concrete beams
colonnes béton armé|reinforced concrete columns
colonne béton armé|reinforced concrete column
colonnes|columns
colonne|column
cloisons|partitions
béton de propreté|blinding concrete
béton non-armé|plain concrete
béton non armé|plain concrete
béton fibré|fibre-reinforced concrete
maçonneries non-portantes|non-load-bearing masonry
maçonneries portantes|load-bearing masonry
maçonneries silico-calcaire|calcium silicate masonry
maçonneries béton|concrete masonry
silico-calcaire|calcium silicate
linteaux préfabriqués|precast lintels
linteau préfabriqué|precast lintel
poutres de fondation|foundation beams
poutre de fondation|foundation beam
voiles béton armé|reinforced concrete walls
voiles|structural walls
radier|raft foundation
prédalle|precast floor plate
dalle coulée sur place|cast-in-place slab
armatures dépassantes|projecting reinforcement
coupure thermique|thermal break
treillis soudés|welded reinforcement meshes
recouvrement des barres|bar lap splice
recouvrement des treillis|reinforcement mesh overlap
recouvrement des TS|reinforcement mesh overlap
alvéoles ouvertes|open cores
bois massif|solid timber
lamellé-collé|glued laminated timber
hourdis béton précontraint|prestressed concrete floor units
hourdis béton armé|reinforced concrete floor units
balcon architectonique préfabriqué|precast architectural concrete balcony
couvrant RDC|floor over ground floor (RDC)
légende|legend
abréviations|abbreviations
vue en plan|plan view
nuage de révision d'indice|revision cloud
poutre en béton armé|reinforced concrete beam
poutre béton armé|reinforced concrete beam
poutre en béton|concrete beam
poutre en acier|steel beam
poutre métallique|steel beam
poutres métalliques|steel beams
poutre de rive|edge beam
poutre-voile|deep beam
poutres|beams
poutre|beam
dalle en béton armé|reinforced concrete slab
dalle béton armé|reinforced concrete slab
dalle en béton|concrete slab
dalle de balcon|balcony slab
dalle de toiture|roof slab
dalle de compression|structural topping slab
dalles|slabs
dalle|slab
poteau en béton armé|reinforced concrete column
poteau métallique|steel column
poteaux|columns
poteau|column
béton armé|reinforced concrete
béton précontraint|prestressed concrete
béton préfabriqué|precast concrete
béton coulé en place|cast-in-place concrete
béton|concrete
acier inoxydable|stainless steel
acier galvanisé à chaud|hot-dip galvanized steel
acier galvanisé|galvanized steel
acier|steel
inox|stainless steel
maçonnerie de parement|facing masonry
maçonnerie de façade|facing masonry
maçonnerie portante|load-bearing masonry
support de maçonnerie|masonry support
supports de maçonnerie|masonry supports
maçonnerie|masonry
mur porteur|load-bearing wall
mur de soutènement|retaining wall
mur d'allège|wall below window
mur creux|cavity wall
mur en béton|concrete wall
voile en béton|concrete wall
voile béton|concrete wall
voile|structural wall
murs|walls
mur|wall
linteaux|lintels
linteau|lintel
cornières|angles
cornière|angle
consoles de support|support brackets
console de support|support bracket
consoles|brackets
console|bracket
porte-à-faux|cantilever
en porte à faux|cantilevered
armatures longitudinales|longitudinal reinforcement
armatures transversales|transverse reinforcement
armatures|reinforcement
armature|reinforcement
ferraillage|reinforcement
enrobage des armatures|reinforcement cover
enrobage|concrete cover
étriers|stirrups
étrier|stirrup
treillis soudé|welded reinforcement mesh
rail d'ancrage|anchor channel
rails d'ancrage|anchor channels
boulon à tête marteau|hammer-head bolt
boulon tête marteau|hammer-head bolt
tige filetée|threaded rod
boulons|bolts
boulon|bolt
ancrage chimique|chemical anchorage
ancrages|anchors
ancrage|anchorage
longueur d'ancrage|anchorage length
longueur d'appui|bearing length
appui de linteau|lintel bearing
appui|support
joint de dilatation|expansion joint
joint de mouvement|movement joint
joint horizontal|horizontal joint
joint vertical|vertical joint
lame d'air|air gap
vide d'air|air gap
largeur de la cavité|cavity width
isolation thermique|thermal insulation
isolant|insulation
isolation|insulation
pont thermique|thermal bridge
charge permanente|permanent load
charges permanentes|permanent loads
charge d'exploitation|imposed load
charges d'exploitation|imposed loads
poids propre|self-weight
charge de vent|wind load
effort tranchant|shear force
moment fléchissant|bending moment
effort normal|axial force
traction|tension
compression|compression
flèche admissible|allowable deflection
flèche|deflection
excentricité|eccentricity
portée|span
entraxe|centre-to-centre spacing
épaisseur|thickness
hauteur|height
largeur|width
longueur|length
diamètre|diameter
coupe|section
façade|elevation
plans de stabilité|structural drawings
plan de stabilité|structural drawing
rez-de-chaussée|ground floor
rez de chaussée|ground floor
RDC|ground floor (RDC)
rez|ground floor
sous-sol|basement
niveau fini|finished level
niveau brut|structural level
sous-face|underside
acrotère|parapet
semelle filante|strip footing
semelle isolée|pad footing
semelle de poutre|beam flange
semelle|semelle
allège|wall below window
hourdis|hourdis
BA|BA
''',
    'nl': '''
gewapende betonbalk|reinforced concrete beam
gewapend betonnen balk|reinforced concrete beam
balk in gewapend beton|reinforced concrete beam
betonnen balk|concrete beam
betonbalk|concrete beam
stalen ligger|steel beam
stalen balk|steel beam
randbalk|edge beam
balken|beams
balk|beam
liggers|beams
ligger|beam
gewapende betonplaat|reinforced concrete slab
gewapend betonnen vloerplaat|reinforced concrete floor slab
vloerplaat|floor slab
betonplaat|concrete slab
balkonplaat|balcony slab
dakplaat|roof slab
gewapend beton|reinforced concrete
voorgespannen beton|prestressed concrete
prefab beton|precast concrete
ter plaatse gestort beton|cast-in-place concrete
beton|concrete
wapening|reinforcement
wapeningsstaven|reinforcing bars
betondekking|concrete cover
langswapening|longitudinal reinforcement
dwarswapening|transverse reinforcement
staalplaat|steel plate
roestvast staal|stainless steel
roestvrij staal|stainless steel
thermisch verzinkt staal|hot-dip galvanized steel
verzinkt staal|galvanized steel
staal|steel
RVS|stainless steel (RVS)
gevelmetselwerk|facing masonry
parementmetselwerk|facing masonry
dragend metselwerk|load-bearing masonry
metselwerkondersteuningen|masonry supports
metselwerkondersteuning|masonry support
metselwerk|masonry
geveldrager|masonry support
draagmuur|load-bearing wall
dragende muur|load-bearing wall
spouwmuur|cavity wall
betonwand|concrete wall
wand|wall
muur|wall
kolommen|columns
kolom|column
betonlatei|concrete lintel
lateien|lintels
latei|lintel
draagconsole|support bracket
ondersteuningsconsole|support bracket
consoles|brackets
console|bracket
hoekprofielen|angle sections
hoekprofiel|angle section
hoeklijn|angle
overkraging|cantilever
uitkraging|cantilever
ankerrail|anchor channel
ankrorail|Ankrorail
ankerrails|anchor channels
verankeringsrails|anchor channels
hamerkopbout|hammer-head bolt
draadstang|threaded rod
chemische verankering|chemical anchorage
verankering|anchorage
verankeringslengte|anchorage length
ankers|anchors
anker|anchor
bouten|bolts
bout|bolt
opleglengte|bearing length
oplegging|bearing
spouwankers|wall ties
spouwanker|wall tie
dilatatievoeg|expansion joint
bewegingsvoeg|movement joint
horizontale voeg|horizontal joint
verticale voeg|vertical joint
luchtspouw|air gap
geventileerde spouw|ventilated cavity
verluchte spouw|ventilated cavity
spouwbreedte|cavity width
spouw|cavity
isolatie|insulation
koudebrug|thermal bridge
thermische brug|thermal bridge
permanente belasting|permanent load
veranderlijke belasting|variable load
eigen gewicht|self-weight
eigengewicht|self-weight
windbelasting|wind load
schuifkracht|shear force
dwarskracht|shear force
buigmoment|bending moment
normaalkracht|axial force
trekkracht|tensile force
druk|druk
doorbuiging|deflection
excentriciteit|eccentricity
overspanning|span
hart-op-hart afstand|centre-to-centre spacing
hart op hart afstand|centre-to-centre spacing
dikte|thickness
hoogte|height
breedte|width
lengte|length
diameter|diameter
doorsnede|section
stabiliteitsplan|structural drawing
begane grond|ground floor
gelijkvloers|ground floor
kelder|basement
afgewerkt vloerpeil|finished floor level
onderzijde|underside
bovenzijde|top surface
plaat|plaat
vloer|vloer
''',
    'de': '''
Stahlbetonträger|reinforced concrete beam
Stahlbetonbalken|reinforced concrete beam
Betonträger|concrete beam
Stahlträger|steel beam
Stahlbalken|steel beam
Randträger|edge beam
Unterzug|downstand beam
Träger|beam
Balken|beam
Stahlbetondecke|reinforced concrete slab
Stahlbetonplatte|reinforced concrete slab
Geschossdecke|floor slab
Deckenplatte|floor slab
Balkonplatte|balcony slab
Dachplatte|roof slab
Stahlbetonstütze|reinforced concrete column
Stahlstütze|steel column
Stützen|columns
Stütze|column
Stahlbeton|reinforced concrete
Spannbeton|prestressed concrete
Betonfertigteil|precast concrete element
Ortbeton|cast-in-place concrete
Beton|concrete
Betonstahl|reinforcing steel
nichtrostender Stahl|stainless steel
rostfreier Stahl|stainless steel
feuerverzinkter Stahl|hot-dip galvanized steel
verzinkter Stahl|galvanized steel
Stahl|steel
Verblendmauerwerk|facing masonry
Vormauerwerk|facing masonry
tragendes Mauerwerk|load-bearing masonry
Mauerwerksabfangung|masonry support
Mauerwerk|masonry
tragende Wand|load-bearing wall
Stützwand|retaining wall
Stahlbetonwand|reinforced concrete wall
Betonwand|concrete wall
Wände|walls
Wand|wall
Stürze|lintels
Sturz|lintel
Konsole|bracket
Konsolen|brackets
Konsolanker|support bracket anchor
Winkelprofil|angle section
Auskragung|cantilever
Bewehrungsstäbe|reinforcing bars
Längsbewehrung|longitudinal reinforcement
Querbewehrung|transverse reinforcement
Bewehrung|reinforcement
Betondeckung|concrete cover
Bügelbewehrung|stirrup reinforcement
Ankerschiene|anchor channel
Ankerschienen|anchor channels
Hammerkopfschraube|hammer-head bolt
Gewindestange|threaded rod
Verankerungslänge|anchorage length
Verankerung|anchorage
Auflagerlänge|bearing length
Auflager|support
Luftschichtanker|wall tie
Luftschicht|air gap
Hohlschicht|cavity
Wärmedämmung|thermal insulation
Dämmstoff|insulation
Dämmung|insulation
Wärmebrücke|thermal bridge
Dehnungsfuge|expansion joint
Bewegungsfuge|movement joint
Lagerfuge|bed joint
Stoßfuge|vertical joint
ständige Last|permanent load
ständige Einwirkung|permanent action
veränderliche Einwirkung|variable action
Eigengewicht|self-weight
Nutzlast|imposed load
Windlast|wind load
Schneelast|snow load
Querkraft|shear force
Biegemoment|bending moment
Normalkraft|axial force
Zugkraft|tensile force
Druckkraft|compressive force
Durchbiegung|deflection
Exzentrizität|eccentricity
Spannweite|span
Achsabstand|centre-to-centre spacing
Dicke|thickness
Höhe|height
Breite|width
Länge|length
Durchmesser|diameter
Schnitt|section
Querschnitt|cross-section
Grundriss|plan
Ansicht|view
Erdgeschoss|ground floor
Kellergeschoss|basement
Oberkante Fertigfußboden|finished floor level
Unterkante Decke|underside of slab
Oberkante|top edge
Unterkante|bottom edge
Attika|parapet
Streifenfundament|strip footing
Einzelfundament|pad footing
Platte|Platte
Decke|Decke
''',
}

AMBIGUOUS = {
    'fr': {
        'console': 'Bracket is the default; confirm whether the detail instead shows a cantilever structural member.',
        'consoles': 'Brackets is the default; confirm the structural detail.',
        'appui': 'Support is the default; check whether this label refers to a bearing, bearing length or window sill.',
        'semelle': 'Source retained: semelle may mean a footing or a beam flange; check the detail.',
        'semelles': 'Source retained: semelles may mean footings or beam flanges; check the legend/detail.',
        'grugeage': 'Notching is the default; confirm the steel connection detail.',
        'allège': 'Wall below window is the default; check the actual element and window detail.',
        'hourdis': 'Source retained: Belgian hourdis may refer to floor units; other contexts use infill blocks.',
        'BA': 'Abbreviation retained; expand only using the project legend (often reinforced concrete).',
    },
    'nl': {
        'console': 'Bracket is the default; confirm whether the detail instead shows a cantilever structural member.',
        'consoles': 'Brackets is the default; confirm the structural detail.',
        'plaat': 'Source retained: plaat can refer to a plate or a slab; check material and element.',
        'vloer': 'Source retained: vloer can mean a floor, structural slab or floor finish; check the detail.',
        'oplegging': 'Bearing is the default; confirm the support condition in the detail.',
        'druk': 'Source retained: druk can mean compression or pressure; check the loading context.',
    },
    'de': {
        'Konsole': 'Bracket is the default; confirm whether the detail instead shows a concrete corbel or cantilever member.',
        'Konsolen': 'Brackets is the default; confirm the structural detail.',
        'Platte': 'Source retained: Platte can refer to a plate or slab; check material and element.',
        'Decke': 'Source retained: Decke can mean a structural floor slab or a ceiling; check the detail.',
        'Auflager': 'Support is the default; confirm the bearing/support condition in the detail.',
    },
}

BRANDS = ('Korbo', 'Sumo', 'Halfen', 'Ancon', 'Leviat', 'Ankrochim', 'KorboFlex', 'Thermoshim', 'Stepoc', 'ISOTEC')


def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold())
                   if not unicodedata.combining(c)).replace('’', "'").replace('–', '-').replace('‑', '-')


TERM_CATEGORIES = {language: {} for language in TERMS}
EXTENDED_ROWS = []


def load_extended_terms():
    """Load the bundled, categorized glossary; preserve existing interpretations."""
    path = Path(__file__).with_name('engineering_terms.psv')
    with path.open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source, delimiter='|')
        if reader.fieldnames != ['category','fr','nl','de','en','review']:
            raise ValueError('Bundled terminology file has an invalid header')
        rows = list(reader)
    known = {lang: {fold(row.split('|',1)[0]) for row in data.strip().splitlines()}
             for lang, data in TERMS.items()}
    for row in rows:
        if None in row or any(not row.get(key) for key in ('category','fr','nl','de','en')):
            raise ValueError('Bundled terminology contains an incomplete entry')
        EXTENDED_ROWS.append(row)
        for language in TERMS:
            for term in row[language].split(';'):
                term = term.strip()
                if not term:
                    raise ValueError('Bundled terminology contains an empty alias')
                key = fold(term)
                TERM_CATEGORIES[language].setdefault(key, row['category'])
                if key in known[language]:
                    # A general addition must not erase a qualified existing
                    # meaning or replace a retained ambiguous source label.
                    continue
                known[language].add(key)
                TERMS[language] = TERMS[language].rstrip() + '\n' + term + '|' + row['en'] + '\n'
                if row['review']:
                    AMBIGUOUS[language][term] = row['review']


load_extended_terms()


class EngineeringTranslator:
    """Protect terminology from the general translator without placeholders."""
    def __init__(self, language, general_translate):
        if language not in TERMS:
            raise ValueError('Unsupported source language')
        self.language = language
        self.general_translate = general_translate
        self.cache = {}
        self.terms = {}
        for line in TERMS[language].strip().splitlines():
            source, english = line.split('|', 1)
            key = fold(source)
            if key in self.terms:
                raise ValueError('Duplicate glossary term: ' + source)
            self.terms[key] = english
            if language == 'de':
                ascii_spelling = source.casefold().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
                self.terms.setdefault(fold(ascii_spelling), english)
        self.terms.update({fold(name): name for name in BRANDS})
        self.ambiguous = {fold(k): v for k, v in AMBIGUOUS[language].items()}
        patterns = [re.escape(k).replace(r'\ ', r'\s+') for k in sorted(self.terms, key=len, reverse=True)]
        self.pattern = re.compile(r'(?<!\w)(?:' + '|'.join(patterns) + r')(?!\w)')

    def _matches(self, text):
        normalized, offsets = [], []
        for index, char in enumerate(text):
            for folded in fold(char):
                normalized.append(folded)
                offsets.append(index)
        for match in self.pattern.finditer(''.join(normalized)):
            start, end = offsets[match.start()], offsets[match.end()-1] + 1
            while end < len(text) and unicodedata.combining(text[end]):
                end += 1
            key = re.sub(r'\s+', ' ', match.group())
            yield start, end, key

    def glossary_matches(self, text):
        return [{'source':text[a:b], 'english':self.terms[k]} for a,b,k in self._matches(text)
                if fold(text[a:b]) != fold(self.terms[k])]

    def review_notes(self, text):
        return [f'{text[a:b]}: {self.ambiguous[k]}' for a,b,k in self._matches(text) if k in self.ambiguous]

    def _general(self, fragment):
        return self.general_translate(fragment) if re.search(r'[^\W\d_]', fragment) else fragment

    def __call__(self, text):
        if text in self.cache:
            return self.cache[text]
        parts, cursor = [], 0
        for start, end, key in self._matches(text):
            parts.append(self._general(text[cursor:start]))
            original, english = text[start:end], self.terms[key]
            if original.casefold() == english.casefold():
                english = original
            elif original.isupper():
                english = english.upper()
            elif original[0].isupper():
                english = english[0].upper() + english[1:]
            parts.append(english)
            cursor = end
        parts.append(self._general(text[cursor:]))
        self.cache[text] = ''.join(parts)
        return self.cache[text]
