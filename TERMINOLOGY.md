# Engineering, project and everyday terminology in version 1.10

French, Dutch and German terminology overrides general machine translation.
The bundled EngineeringGlossary.tsv lists the source labels, English terms
categories and context notes. This export is a reference, not an editable settings file.
Browse terminology inside the app provides a searchable view of the same entries.

| French | Dutch | German | English |
| --- | --- | --- | --- |
| béton | beton | Beton | concrete |
| béton armé | gewapend beton | Stahlbeton | reinforced concrete |
| poutre | balk / ligger | Träger / Balken | beam |
| linteau | latei | Sturz | lintel |
| armature | wapening | Bewehrung | reinforcement |
| maçonnerie | metselwerk | Mauerwerk | masonry |
| lame d'air | luchtspouw | Luftschicht | air gap |
| isolation | isolatie | Dämmung | insulation |
| joint de dilatation | dilatatievoeg | Dehnungsfuge | expansion joint |

Longer phrases take priority. Poutre en béton armé / gewapende betonbalk /
Stahlbetonträger become reinforced concrete beam. A plain poutre remains
beam: the translator does not infer concrete or steel from that label alone.
Capitalization, accents, curly apostrophes and extra whitespace are handled.
German umlauts and common ae/oe/ue spellings are recognized. Matches must
respect word boundaries; dimensions and ordinary drawing codes are protected
by the PDF engine. Product names such as Korbo, Sumo and Halfen are retained.

The translator interprets labels, not drawing geometry. Other words use the
offline models. A glossary cannot guarantee the meaning of an entire note,
an unfamiliar abbreviation, or a product-specific/project-specific convention.

## Version 1.10 expansion

5,100 explicit source entries: French 1,771, Dutch 1,696, German 1,633.
The 963 added source entries represent 353 submitted concepts and phrases;
existing meanings take priority when an alias already exists. The expansion
includes everyday conversation, correspondence, meetings, drawing instructions,
masonry/facade details, KORBO installation wording, PLAKA reinforcement joints,
anchorage, steel fabrication and design coordination. Both typed text and files
use the same glossary. New translations are practical equivalents; project and
regional usage may vary. Source/English reference notes remain in English.

Representative KORBO hardware and installation wording was checked against:
https://www.plaka-solutions.com/fileadmin/user_upload/02.01.01_p_multi_nl-fr-en_KORBO_plaatsingsvoorschriften-PrescriptionsDePose_V03_2026-05-01.pdf

Representative Stabox joint/component wording was checked against:
https://www.plaka-solutions.com/nl/product-catalogus/01-01-10-seismische-wachtdoos-stabox

These source checks cover selected product vocabulary. The overall glossary is
independently authored; it is not an official manufacturer translation catalogue.
No capacities, installation limits or design acceptance rules are encoded.

## Version 1.7 expansion

There are 4,137 explicit source entries: French 1,446, Dutch 1,372 and German
1,319, compared with 1,601 previously. Counts exclude additional automatic German
transliterations and retained product names. The catalogue includes 25 subjects
plus the original core vocabulary. Entries include both terms and explicit aliases.

The additional vocabulary covers general office/project language and quotation,
delivery, document status, schedules, site instructions, dimensions and tolerances,
structural calculations, masonry design, anchor installation/failure modes,
concrete/reinforcement details, steel fabrication and coatings.

KORBO terminology includes support angles, individual/corner/welded brackets,
adjustment plates and screws, packing/shim plates, thermal break pads, slotted
holes, bracket spacing, cavity widths, supported masonry, brick hangers, movement
joints, flashing and cavity closures. The vocabulary also covers components
associated with PLAKA continuity boxes, reinforcement couplers, shear connectors,
facade restraints, cast-in channels, chemical anchors, lifting and waterproofing.

Product names such as PLAKA, KORBO, KorboFlex, Korbo Dry, Thermoshim, Stabox,
Titan, Couplerbox, Stonefix, Solea-Fix, Ankrorail, Ankrochim and Murfor are retained.
The terminology does not establish which product is suitable for an application,
and does not encode capacities, dimensions or installation requirements.

Example mappings:

| French | Dutch | German | English |
| --- | --- | --- | --- |
| plaque de réglage | regelplaat | Justierplatte | adjustment plate |
| boulon de fixation | bevestigingsbout | Befestigungsbolzen | fixing bolt |
| vis de fixation | bevestigingsschroef | Befestigungsschraube | fixing screw |
| réglage en hauteur | hoogteverstelling | Höhenverstellung | height adjustment |
| boîte d'attente | wachtdoos | Rückbiegeanschluss | reinforcement continuity box |
| goujon pour efforts tranchants | dwarskrachtdeuvel | Querkraftdorn | shear load connector |
| livraison | levering | Lieferung | delivery |
| devis | offerte | Angebot | quotation |

The review list now explains whether unchanged text was retained for context,
is a known term/product name, or was returned unchanged by the offline model.
Ambiguous labels are not automatically assigned a structural meaning. More
qualified phrases translate when the text supplies the required distinction.
Additional apostrophes, hyphen forms and soft hyphens are normalized for lookup;
source offsets are retained for correct replacement. Known phrase acronyms can
participate in a glossary match while numeric dimensions and product codes stay
protected. These changes apply to PDF, Word and PowerPoint alike.

Representative product terminology was checked against current first-party pages:

- KORBO, French: https://www.plaka-solutions.com/catalogue-produit/02-01-01-korbo
- KORBO, Dutch: https://www.plaka-solutions.com/nl/product-catalogus/02-01-01-korbo
- KORBO, English: https://www.plaka-solutions.com/en/02-01-01-korbo
- PLAKA product index: https://www.plaka-solutions.com/en/sitemap
- Fixing-angle terminology: https://www.plaka-solutions.com/02-03-01-equerres-de-fixation

This is an independently authored practical glossary with representative source
checks, not an official Leviat dictionary or a certified translation database.

## Labels requiring context

Ambiguous standalone terms are marked REVIEW CONTEXT in the companion
.translations.txt file. For example, French semelle can mean a footing or a
beam flange. Dutch plaat and German Platte can mean a plate or a slab. These
labels are retained when there is insufficient information. Longer explicit
phrases such as semelle filante or Stahlbetonplatte use the specific term.
Console/Konsole defaults to bracket with a context flag; a structural member
or concrete corbel may need another interpretation. BA stays unchanged unless
the project legend establishes its meaning. Review the flagged entries against
the detail, material specification and drawing legend.

## References consulted for representative product terminology

These sources illustrate technical usage; they do not certify this app or
endorse all glossary entries.

- Leviat / Plaka Korbo, French:
  https://www.plaka-solutions.com/catalogue-produit/02-01-01-korbo
- Leviat / Plaka Korbo, Dutch:
  https://www.plaka-solutions.com/nl/product-catalogus/02-01-01-korbo
- Leviat / Plaka Korbo, English:
  https://www.plaka-solutions.com/en/02-01-01-korbo
- Halfen Luftschichtanker, German:
  https://www.halfen.com/de-DE/produkte/fassadenbefestigungen-verstaerkungen/verblendmauerwerk/luftschichtanker
- Ancon masonry reinforcement, German:
  https://www.anconbp.de/produkte/mauerwerksbewehrungen
- European Commission JRC, Aide-mémoire béton armé:
  https://eurocodes.jrc.ec.europa.eu/publications/aide-memoire-beton-arme


## CAD labels in version 1.2

Right-angle text is inserted in the original unrotated PDF coordinates, so
pages displayed at 270 degrees no longer send most labels to notes. Small CAD
fonts scale proportionally, and an embedded font preserves Greek unit symbols.
The report lists REPLACED, NOTE (with reason) and UNCHANGED labels separately.
ALL CAPS prose is normalized before inference and restored afterwards.

French additions cover padstones, beam-and-block floors, piles, precast floor
plates, blinding concrete, raft foundations and drawing titles. COUVRANT RDC
means floor over ground floor (RDC), rather than a plan of the ground-floor slab.
Semelles remains flagged: footings and beam flanges require drawing context.

Additional representative sources:
- Prefer, asselets under concentrated beam/lintel loads:
  https://www.prefer.be/0191/fr/51/Asselets-en-beton-apparent
- OTEP, bilingual floor beams and infill blocks:
  https://www.otep-sa.com/catalogues/poutrelles.pdf
- Wallonia CCTB, concrete-filled foundation shafts:
  https://batiments.wallonie.be/files/unzip/html_CCTB_01.12/Content/13-22-Faux-puits-en-beton-arme.html


## Expanded catalogue in version 1.3

There are 1,524 explicit source entries (French 586, Dutch 477, German 461),
excluding automatically recognized German transliterations and product names.
The additional catalogue groups terminology into 13 subjects:

- Drawing conventions and construction instructions
- Structural design, actions, stresses and limit states
- Concrete, reinforcement, formwork and precast floor systems
- Steel members, welds, bolts, anchors and connections
- Foundations, ground and drainage around foundations
- Masonry, wall ties, cavity walls, facade supports and cladding
- Architecture, openings, frames, stairs, balconies and levels
- Roofs, timber structures and rainwater components
- Envelope, waterproofing, airtightness and insulation
- Finishes, screeds, plaster, stone and glazing
- Fire protection and acoustics
- Drainage and building services
- Execution, specifications and technical assessments

The source catalogue is src/engineering_terms.psv (UTF-8, pipe-delimited).
It is bundled inside the EXE. Existing core meanings take precedence over
more general catalogue entries. Longer qualified phrases take precedence
over shorter ambiguous words. Every explicit added alias is tested in all
three languages without machine-model fallback. The Windows executable also
checks that its embedded catalogue and built-in terminology browser load.

Examples of protected distinctions: window sill / door threshold; screed /
structural slab; vapour barrier / vapour retarder; fire resistance / reaction
to fire; beam web / beam flange; sill back upstand / underside drip groove.
An unknown project abbreviation must still be checked against its legend.
No finite vocabulary can establish every engineering or architectural meaning,
and terminology coverage does not add scanned-PDF OCR.

Additional references checked for representative distinctions:
- Leviat wall ties, English:
  https://www.plaka-solutions.com/en/02-05-08-wall-tie-for-glued-brickwork
- Halfen cavity wall ties, German:
  https://www.halfen.com/de-DE/produkte/fassadenbefestigungen-verstaerkungen/verblendmauerwerk/luftschichtanker
- Buildwise timber guide, air/vapour control terminology:
  https://www.buildwise.be/media/4axn13yf/bw-gids-hout-fr.pdf
- European Commission JRC glossary:
  https://eurocodes.jrc.ec.europa.eu/glossary

These sources were consulted for representative terminology only; they do not
certify the whole catalogue or endorse the software. The wider vocabulary is
an independently authored practical glossary.

## German drawing labels in version 1.4

Additional parts-list, title-block and pipe-support vocabulary includes Teileliste,
Stückliste, Pos., Baugr., Werkstoff, Festpunkt, Gleitpunkt and Fallrohrstütze.
Prüfung is translated as check and flagged for context: inspection or testing
may be intended. Complete alphanumeric identifiers, including suffixes and
underscores, are protected before inference. Short unknown acronym references
are retained conservatively; all-caps prose and recognized glossary terms still
translate. The report records the app version and selected source language.
