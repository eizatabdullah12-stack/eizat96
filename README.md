# Engineering PDF Translator

Native Windows desktop PDF translator: French/Dutch to English. After a
successful build, open EngineeringPDFTranslator.exe; no installation, browser,
API key or translation internet connection is required. Models are embedded.

Choose a PDF, select the source language and output mode, then save a new PDF.
The original is retained. A translation text list is saved alongside the PDF.

## Status

Source and local PDF-engine checks are prepared. The Windows build has NOT
run yet. Do not describe this source package as a ready-to-run application.
GitHub Actions builds and runs the compiled executable's self-test before
making the executable and portable ZIP available as workflow artifacts.

## Building

Use GitHub Actions in a repository with Actions enabled. A change to source,
tests or build configuration triggers the Windows workflow. It can also be
started manually. The build requires internet access to PyPI, the official
Argos model index, and the published language-model download URLs.

The build fetches the French and Dutch models, runs real inference checks,
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

## Third-party notices

See THIRD_PARTY.md and the notices/license files in the exact dependency and
model versions downloaded. Models use the official Argos index and direct
CTranslate2/SentencePiece inference. This source package contains no model
binaries or Windows executable. Review license terms before distributing a
populated binary bundle.
