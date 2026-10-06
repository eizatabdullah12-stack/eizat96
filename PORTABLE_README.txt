Engineering PDF Translator 1.5 - portable Windows x64 application

Double-click EngineeringPDFTranslator.exe. No Python installation, browser,
API key or internet connection is required. The first launch can take a while
because the bundled translation models unpack into Windows temporary storage.

1. Choose a PDF with selectable text.
2. Select French, Dutch or German as the source language. The output is English.
3. Select text replacement or translation notes.
4. Click Translate and save, and choose a new filename.

Engineering and architectural terminology is enabled automatically. The 1,601
entries cover 13 subject areas: French 611, Dutch 501 and German 489.
Click Browse terminology to search source terms, English meanings and categories.
The bundled glossary takes priority over the offline translation models. Ambiguous
labels are marked REVIEW CONTEXT in the .translations.txt list. Review these
against the detail and project legend. See TERMINOLOGY.txt and EngineeringGlossary.tsv.

Your original PDF is retained. The app saves the translated PDF and a companion
.translations.txt list. Open the PDF in a reader that supports annotations to
view translation notes. Notes-only mode keeps original labels visible.

Version 1.2 supports right-angle labels and rotated CAD pages, including small
legend text. The list distinguishes replacements, notes and unchanged labels.
Drawing references, dimensions and units remain unchanged. A note explains when
a translated label cannot fit its original space or uses unsupported characters.

This version does not recognize scanned image-only PDFs (OCR), translate
Office files, or support other target languages. Review machine translations
of engineering terminology and compare the translated drawing with its source.

Source and reproducible Windows build:
https://github.com/eizatabdullah12-stack/eizat96

The bundle contains third-party notices and dependency/model license files.
The windows-selftest.json file records checks run against the compiled app.

Version 1.3 expands architecture, structural design, reinforcement, steel fixings,
foundations, masonry/facades, roofs, insulation, finishes, fire/acoustics, drainage,
services and specifications. Unknown terms still use the offline models.
This is broad practical coverage, not an exhaustive dictionary or engineering
interpretation of geometry. Project abbreviations and ambiguous terms need context.

Version 1.4 requires an explicit source-language choice and records the version
and language in the PDF metadata and translation report. It warns if no labels
change. Complete alphanumeric product identifiers and short reference acronyms
are retained; additional parts-list and pipe-support terms are included.

Version 1.5 reopens the saved PDF and checks the replacement labels and notes
before reporting success. The report identifies its matching PDF by filename
and SHA256. Default output names include a timestamp to avoid reusing a cached
filename. Click Open verified PDF after translation to open the exact output;
the button checks that the PDF has not changed since it was verified.

Input PDFs are normalized in memory before translation to prevent edits being
lost when saving certain compressed object/xref-stream PDFs. The original file
is retained. This applies to French, Dutch and German equally.
