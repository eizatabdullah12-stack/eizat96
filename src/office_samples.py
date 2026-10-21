"""Small editable Office fixtures for compiled-app smoke checks (no Office SDK)."""
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def make_sample(path, text, extra_parts=None):
    """Return a minimal readable DOCX or PPTX, including split styled runs."""
    text = escape(text)
    if path.suffix.lower() == '.docx':
        parts = {
            '[Content_Types].xml': f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>',
            '_rels/.rels': f'<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>',
            'word/_rels/document.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="rIdHeader" Type="{R}/header" Target="header1.xml"/><Relationship Id="rIdFooter" Type="{R}/footer" Target="footer1.xml"/></Relationships>',
            'word/document.xml': f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{text}</w:t></w:r><w:r><w:t xml:space="preserve"> 200 mm - HEA200 - B500B</w:t></w:r></w:p><w:tbl><w:tblPr/><w:tblGrid><w:gridCol w:w="2400"/></w:tblGrid><w:tr><w:tc><w:tcPr/><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:sectPr><w:headerReference w:type="default" r:id="rIdHeader"/><w:footerReference w:type="default" r:id="rIdFooter"/></w:sectPr></w:body></w:document>',
            'word/header1.xml': f'<w:hdr xmlns:w="{W}"><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:hdr>',
            'word/footer1.xml': f'<w:ftr xmlns:w="{W}"><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:ftr>',
        }
    else:
        parts = {
            '[Content_Types].xml': f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/><Override PartName="/ppt/notesSlides/notesSlide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>',
            '_rels/.rels': f'<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
            'ppt/presentation.xml': f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="9144000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>',
            'ppt/_rels/presentation.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/slide" Target="slides/slide1.xml"/></Relationships>',
            'ppt/slides/_rels/slide1.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="rIdNotes" Type="{R}/notesSlide" Target="../notesSlides/notesSlide1.xml"/></Relationships>',
        }
        def shape_tree():
            return f'<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/><p:sp><p:nvSpPr><p:cNvPr id="2" name="Text"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="1000" y="1000"/><a:ext cx="8000000" cy="2000000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr b="1"/><a:t>{text}</a:t></a:r><a:r><a:t> 200 mm - HEA200 - B500B</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp></p:spTree>'
        parts['ppt/slides/slide1.xml'] = f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld>{shape_tree()}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
        parts['ppt/notesSlides/notesSlide1.xml'] = f'<p:notes xmlns:p="{P}" xmlns:a="{A}"><p:cSld>{shape_tree()}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
    parts.update(extra_parts or {})
    with ZipFile(path, 'w', ZIP_DEFLATED) as package:
        for name, content in parts.items():
            package.writestr(name, content)
