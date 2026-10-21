Engineering Document Translator 1.10 - Windows x64 application

Auto / mixed languages is now the default. French, Dutch and German text in the
same document is detected per label or sentence and translated to the selected
output language. Text already in that output language is retained. Detection and translation work offline.
Uncertain short labels and unsupported languages are retained for review.
Use a manual source language when necessary; switches within one sentence may
not be recognized reliably. The translation list includes a language summary.

Download and run EngineeringTranslator-1.10-Setup.exe. The installer works offline,
installs into your user profile and provides a Start menu shortcut. Administrator
access is not needed. Optional desktop shortcut and Windows uninstaller included.
No Python installation, browser, API key or internet connection is required.

DIRECT TEXT TRANSLATION
The Text translator tab opens by default. Type or paste text and pause briefly:
the app detects English/French/Dutch/German and translates automatically into the
selected output language. Paste, Copy translation and Clear buttons are provided.
Ctrl+Enter or Translate runs manually. Automatic translation applies up to 4,000
characters; longer text uses the button, up to 50,000 characters. Paragraphs,
dimensions and product codes are retained. Changing text or language immediately
clears the old result; obsolete background results are discarded. Context notes
identify uncertain or ambiguous text. Choose a manual source language if needed.

DOCUMENT TRANSLATION
Select the Documents tab to use the existing file translation features.

1. Choose a PDF with selectable text, a Word .docx or a PowerPoint .pptx file.
2. App language: English by default; choose Français, Nederlands or Deutsch
   to change the software display. This does not change the output language.
3. Source language: Auto / mixed languages, or manually choose a language.
4. Output language: English by default; choose French, Dutch or German if wanted.
5. For PDF, select text replacement or translation notes. Office files save
   editable translated text in the same format as the source.
6. Click Translate and save, and choose a new filename.

Engineering, product and general project terminology is enabled automatically.
The 5,100 source entries include French 1,771, Dutch 1,696 and German 1,633.
Click Browse terminology to search source terms, English meanings and categories.
The bundled glossary takes priority over the offline translation models. Ambiguous
labels are marked REVIEW CONTEXT in the .translations.txt list. Review these
against the detail and project legend. See TERMINOLOGY.txt and EngineeringGlossary.tsv.

Your original document is retained. The app saves a translated copy and a companion
.translations.txt list. Open the PDF in a reader that supports annotations to
view translation notes. Notes-only mode keeps original labels visible.

Version 1.2 supports right-angle labels and rotated CAD pages, including small
legend text. The list distinguishes replacements, notes and unchanged labels.
Drawing references, dimensions and units remain unchanged. A note explains when
a translated label cannot fit its original space or uses unsupported characters.

This version does not recognize scanned image-only PDFs or text in pictures (OCR),
read older .doc/.ppt formats, or support languages beyond English, French, Dutch and German. Review machine translations
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

Version 1.6 adds native Word (.docx) and PowerPoint (.pptx) translation using the
same offline models and engineering glossary. Word paragraphs, tables, headers,
footers, text boxes, footnotes, endnotes and comments are supported. PowerPoint
slides, tables, grouped text boxes, speaker notes and native diagram text are
supported. Images, relationships, shapes, styles and other package parts remain.
Saved Office files are reopened and their package contents checked. Open verified
file checks the saved file's SHA256 before opening that exact translated copy.

Review text fit in Office: longer English text can reflow Word pages or overflow
PowerPoint boxes. Styling inside translated mixed-format phrases is approximate.
Fields, equations, chart caches, master/layout text and embedded objects are
retained without translation. Text in images requires OCR and is not supported.
Save legacy .doc/.ppt files as .docx/.pptx first. Macro-enabled and digitally signed
Office files are unsupported. Microsoft Office is not required for translation;
use an appropriate installed reader/editor to open the resulting Office copy.

Version 1.7 expands the glossary from 1,601 to 4,137 source entries, including
KORBO brackets, angles, adjustment parts, brick hangers and cavity details;
PLAKA reinforcement/anchor/connection terminology; site execution, calculations,
steelwork and general project language. Typographic lookup and known phrases
containing acronyms are improved. Product names, dimensions and codes are retained.
The translation list now explains ambiguous retained terms and unchanged model
results. Text inside pictures still needs OCR. Review the translation for context.

Version 1.9: separate App language and Output language controls. Both default to
English on launch. App labels, buttons, progress and common dialogs are localized.
The source/English reference glossary keeps its original terminology content.
Output supports all four languages using six bundled offline models. French,
Dutch and German pairs use English as an intermediate when needed. Review
engineering context and terminology; automatic detection is probabilistic.

Version 1.10 adds direct text translation and 963 source entries covering everyday
conversation, office messages, drawing instructions, masonry details, KORBO
installation vocabulary, PLAKA reinforcement joints, fixings and fabrication.
