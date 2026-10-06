# Engineering terminology in version 1.3

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
