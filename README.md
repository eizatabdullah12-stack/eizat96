# Engineering PDF Translator

Native Windows desktop PDF translator: French/Dutch/German to English. After a
successful build, open EngineeringPDFTranslator.exe; no installation, browser,
API key or translation internet connection is required. Models are embedded.

Choose a PDF, select the source language and output mode, then save a new PDF.
The original is retained. A translation text list is saved alongside the PDF.

[Download version 1.1 for Windows](https://github.com/eizatabdullah12-stack/eizat96/actions/runs/37428590026/artifacts/11395588344).
Extract the ZIP and double-click EngineeringPDFTranslator.exe.
Download size is about 334 MiB. Available until 2026-10-20.
Version 1.1 adds German and 365 engineering glossary entries.

## Status

Version 1.1 passed all 10 regression tests and the Windows compiled-app tests
on 2026-10-06. Checks exercised the actual GUI, all three offline models,
engineering terminology, PDF replacement/notes, ambiguous-label reports and
protected dimensions/codes/grades. The complete test report is in the download.

## Building

Use GitHub Actions in a repository with Actions enabled. A change to source,
tests or build configuration triggers the Windows workflow. It can also be
started manually. The build requires internet access to PyPI, the official
Argos model index, and the published language-model download URLs.

The build fetches the French, Dutch and German models, runs real inference checks,
runs PDF tests, bundles a single executable with PyInstaller, then runs a
compiled-app self-test for GUI startup, both language models and PDF output.
Failed checks prevent the finished artifact from being uploaded. Account
Actions quotas and repository permissions govern availability.

A manual Windows x64 build requires Python 3.11 and build_windows.ps1. End
users do not need Python. The one-file app extracts its own runtime to a
Windows temporary folder on launch; the executable will be fairly large.

## Supported

Selectable-text PDFs; original images/vector lines retained during text
replacement; protected numeric dimensions, common units and simple codes;
translation notes for labels that do not fit or are rotated; notes-only mode;
page progress and cancellation between translation operations.

## Engineering glossary

Structural and masonry terminology takes priority over general translation.
Longer phrases, accent variants and German transliterations are supported.
Ambiguous terms are retained or flagged in the companion translation list.
See TERMINOLOGY.md and the exported EngineeringGlossary.tsv. This layer does
not interpret drawing geometry or guarantee project-specific terminology.

## Limitations

No scanned-PDF OCR, Office files, automatic language detection or target
languages other than English. Machine translation quality on engineering
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
