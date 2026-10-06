# Dependencies and distribution review

This source package imports PyMuPDF, CTranslate2, SentencePiece and their dependencies.
It does not vendor their binaries or model archives.

Before distributing a compiled bundle, retain the full license/notice files
for all bundled dependencies and language models. In particular, PyMuPDF is
available under AGPL or a commercial license; review the applicable terms.
Argos Translate is open source; its dependencies and model data can have
separate license requirements. Consult the licenses from the exact versions
and archives used by the completed Windows build.

Official projects:
https://github.com/pymupdf/PyMuPDF
https://github.com/argosopentech/argos-translate
https://github.com/pyinstaller/pyinstaller
https://github.com/OpenNMT/CTranslate2
https://github.com/google/sentencepiece

The build retains installed dependency license files in the licenses folder,
alongside license/README files shipped inside the bundled model archives.
Application source is available at https://github.com/eizatabdullah12-stack/eizat96
