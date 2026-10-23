# Version 1.12 Belgian Dutch drawing corrections

Created by Eizat. Adds specific Belgian architectural vocabulary, including
vloerpas, onderz fund, polierbeton, hellingschape, potten en balken,
snelbouwsteen, raamborderel and joinery terminology. Longer window phrases such
as draai-kip raam take priority over the structural kip (buckling) entry.
Recorded phrases containing abbreviations such as cfr. are kept together.
PDF labels wrapped over nearby aligned lines are combined only when a known
phrase crosses the line break. Distant columns and unrelated prose stay separate.

Version 1.12 Windows build and installation verification pending. The v1.11
installer below remains the previous verified release until v1.12 passes.

# Engineering Document Translator 1.12

Created by **Eizat**. Version 1.11 adds a new custom E speech-bubble logo and a
**Conversation / natural sentences** text mode. It keeps a whole sentence's context
instead of translating fragments around individual engineering glossary terms.
The bundled models translate unlisted sentences; the phrasebook is not a word limit.

The conversation phrasebook covers over 1,000 concepts, with thousands of forms in
English, French, Dutch and German: daily conversation, travel, food, work, family,
feelings, informal speech, idioms and uncensored mild/strong profanity. Exact phrases
use recorded equivalents in all twelve directions. Common chat spellings and a few
clear agreement errors are normalized. This is not a complete grammar checker.
Ambiguous isolated words may need a source-language choice or sentence context.
Profanity equivalents vary by region and tone.

Choose **Engineering terminology** for the existing technical text workflow.
Document translation continues to prioritize engineering terms. Both phrasebook
and technical entries are searchable in the glossary window. A new Windows release
is published automatically only after the compiled app and installation checks pass.

[Download verified Windows Setup v1.11 (615 MB)](https://github.com/eizatabdullah12-stack/eizat96/releases/download/v1.11/EngineeringTranslator-1.11-Setup.exe)

All 68 Windows tests, compiled GUI/model checks, and installation/file verification
passed. The published installer checksum matches the tested binary. Download and
run the installer; no GitHub Actions build is needed.

Native Windows app for direct text, PDF, Word and PowerPoint translation,
fully offline in English, French, Dutch and German. Both display and output
default to English. Automatic source-language detection supports mixed text.

Run EngineeringTranslator-1.11-Setup.exe to install for the current user, then
open the Start menu shortcut. All six language models are included. No Python,
API key or network connection is needed during installation or use.

The **Text translator** tab opens first. Type or paste and pause for automatic
translation, or click Translate / Ctrl+Enter. Paste, Copy and Clear are available.
The latest text and language selection always take priority over obsolete work.
Long text over 4,000 characters requires the button; the limit is 50,000.
The **Documents** tab retains the PDF/.docx/.pptx translation workflow.

The glossary now has 5,100 source entries (French 1,771 / Dutch 1,696 / German
1,633), adding 963 general, office, engineering and KORBO/PLAKA entries.
See TERMINOLOGY.md for scope, source checks and context limitations.

The Windows workflow runs the regression tests and the compiled GUI/model/file
checks, creates a four-language Inno Setup installer, installs it in an isolated
folder and checks every installed file against the verified application bundle.
Build and install evidence is recorded only after those checks finish.

## Version 1.9 interface and output languages

The app starts in English and outputs English by default. The **App language**
selector switches labels, buttons, progress, common dialogs and glossary headings
between English, Français, Nederlands and Deutsch. This is independent of the
**Output language** selector, which chooses the translated document's language.

Input can be automatic/mixed or manually set to any of the four languages.
All 12 translation directions are supported. Six bundled models cover translation
to and from English; other language pairs use English as an intermediate.
Text already in the selected output language is retained when detected.
Engineering vocabulary is used in both directions, and numeric dimensions,
product names and references remain protected. Review translation semantics,
especially when using an intermediate language or ambiguous source terminology.

Interface changes apply immediately and do not change the output language.
The reference glossary remains a source/English terminology reference; its
entries and context content are not interface translations. Native Windows
file-picker controls follow Windows' own language settings. Unexpected technical
error details can appear in their original language.

The package is larger because it includes all six offline translation models.
No API key, Python installation or internet connection is needed to translate.

## Version 1.8 automatic / mixed-language mode

Select **Auto / mixed languages** (the default) to translate French, Dutch and
German passages within one PDF, Word or PowerPoint file to English. Detection
works offline using bundled langid data and the engineering glossary. Each label
or sentence is routed to its corresponding model; existing English is retained.
Models load only when a language is encountered. Manual language selection is
still available.

Short or ambiguous labels and unsupported languages are retained and flagged in
the translation list. Detection is probabilistic; language switches within one
sentence, abbreviations and very short text may need a manual source-language
choice. Auto mode does not add OCR or additional translation languages. The
report lists detected language segments and language-review counts.

The catalogue now has 4,137 source entries after separating greeting terms.

## Version 1.7 vocabulary update

The built-in glossary has 4,137 explicit source entries: French 1,446, Dutch
1,372 and German 1,319, excluding automatic German transliterations and retained
product names. This expands the previous 1,601 entries and covers 25 catalogue
subjects plus the original core vocabulary. Every explicit catalogue alias is
checked against its glossary mapping without model fallback.

New subjects include KORBO masonry support hardware, adjustment/shim/thermal-break
plates, angle profiles, brick hangers, cavity closures, substrate and anchor design,
PLAKA reinforcement continuity boxes, shear connectors, couplers, anchor channels,
lifting and waterproofing components, site tolerances, calculation reports and
general project/office vocabulary. Product names and alphanumeric references stay
unchanged. These are translation terms, not product selection or installation rules.

Matching now handles additional typographic apostrophes/hyphens and discretionary
soft hyphens. Known multiword phrases such as Dutch `RVS hoeklijn` translate as
a phrase rather than having their acronym split off as an unknown reference.
The companion report distinguishes deliberately retained ambiguous terms,
already-English/product labels and unchanged model results. Adding vocabulary
does not add OCR: text embedded only in pictures remains untranslated.

## Version 1.6 update

Word: paragraphs, tables, headers, footers, text boxes, footnotes, endnotes and
comments. PowerPoint: slide text, tables, grouped text boxes, speaker notes and
native SmartArt text in diagram data/drawing parts. The same offline models,
engineering glossary and dimension/product-code protection apply to all formats.

The Office path edits text XML inside the original package, retaining media,
relationships, slide geometry and styles. Paragraphs are translated across styled
runs; matching text keeps its run styling and changed phrases use approximate
style allocation. No Office installation or internet is needed to translate.
Every saved package part is reopened and checked before publishing the output.
The report records the output filename and SHA256; Open verified file checks
that identity before opening it in the computer's default application.

Longer translations may reflow Word pages or overflow PowerPoint text boxes.
Review layout and mixed formatting in Office. Images, embedded objects, equations,
fields, chart caches, slide masters and layouts remain unchanged. No OCR is
included. Older `.doc`/`.ppt` files must first be saved as `.docx`/`.pptx` in Office.
Macro-enabled and digitally signed Office files are unsupported.

## Version 1.5 update

Input PDFs are normalized and reopened before edits, avoiding lost edits in
compressed object/xref-stream documents. Saved output is reopened and checked
before success is reported. Every expected
replacement label and translation note must be readable in the saved PDF.
The report records the matching output filename and SHA256. Output filenames
include a timestamp by default, and Open verified PDF checks the file identity
before opening that exact copy in the default reader.

All 24 regression tests passed locally and on Windows, including a writer that reports success
without inserting text: the app rejects that output and preserves the previous
file. Missing notes, report identity, German terms, rotated labels and protected
values are also tested. These checks verify saved PDF content, not translation
semantics or every reader's visual rendering. The compiled Windows executable passed real model inference and saved-PDF
verification for French, Dutch and German, including compressed input PDFs.

## Building

Use GitHub Actions in a repository with Actions enabled. A change to source,
tests or build configuration triggers the Windows workflow. It can also be
started manually. The build requires internet access to PyPI, the official
Argos model index, and the published language-model download URLs.

The build fetches the French, Dutch and German models, runs real inference checks,
runs PDF and Office tests, bundles the app with PyInstaller, then runs a
compiled-app self-test for GUI startup, all three language models, PDF output and
native Word/PowerPoint translation in each language.
Failed checks prevent the finished artifact from being uploaded. Account
Actions quotas and repository permissions govern availability.

A manual Windows x64 build requires Python 3.11 and build_windows.ps1. End
users do not need Python. Inno Setup compresses the app and models into a Windows installer. The installed
app reads models directly from its installation folder.

## Supported

Selectable-text PDFs; original images/vector lines retained during text
replacement; protected numeric dimensions, common units and simple codes;
right-angle text replacement on rotated pages; translation notes for labels that do not fit; notes-only mode;
page progress and cancellation between translation operations.

## Engineering glossary

Structural and masonry terminology takes priority over general translation.
Longer phrases, accent variants and German transliterations are supported.
Ambiguous terms are retained or flagged in the companion translation list.
See TERMINOLOGY.md and the exported EngineeringGlossary.tsv. This layer does
not interpret drawing geometry or guarantee project-specific terminology.

## Limitations

No scanned-PDF/image OCR, legacy `.doc`/`.ppt` files or languages outside
English, French, Dutch and German. Machine translation quality on engineering
terminology still needs human review. Dense CAD text bounds, unusual fonts,
complex equations and overlapping labels need representative-file testing.
Notes-only mode preserves every original label. Original digital signatures
will not remain valid in translated copies. Long text is chunked into short
runs, which may reduce translation context.

## Validation

Local deterministic tests check geometry, source preservation, protected
values, notes fallback, no-text errors and cancellation. These checks do not
establish real model quality or Windows portability. The workflow's compiled
self-test supplies Windows evidence after it actually runs successfully.
A clean Windows computer should still be used for final launch verification.

## License

This application is distributed under GNU AGPL version 3. See LICENSE.
Third-party dependencies and models retain their respective license terms.

## Third-party notices

See THIRD_PARTY.md and the notices/license files in the exact dependency and
model versions downloaded. Models use the official Argos index and direct
CTranslate2/SentencePiece inference. This source package contains no model
binaries or Windows executable. Review license terms before distributing a
populated binary bundle.
