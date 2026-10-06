# Engineering terminology in version 1.2

French, Dutch and German terminology overrides general machine translation.
The bundled EngineeringGlossary.tsv lists the source labels, English terms
and context notes. This export is a reference, not an editable settings file.

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
