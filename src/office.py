"""Translate native Office text without rebuilding the Office package.

Only text nodes in selected parts change. Relationships, media, layout, styles,
equations, fields and other package parts retain their original bytes.
"""
from bisect import bisect_right
from difflib import SequenceMatcher
from pathlib import Path
import hashlib
import os
import re
import tempfile
from zipfile import ZipFile, BadZipFile

from lxml import etree
from engine import protected_translate, reference_label
from version import VERSION

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WS = 'http://purl.oclc.org/ooxml/wordprocessingml/main'
AS = 'http://purl.oclc.org/ooxml/drawingml/main'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
PARAGRAPHS = {f'{{{ns}}}p' for ns in (W, A, WS, AS)}
TEXT = {f'{{{ns}}}t' for ns in (W, A, WS, AS)}


def parse_xml(data):
    # Never resolve external entities or fetch document resources.
    parser = etree.XMLParser(resolve_entities=False, no_network=True,
                             remove_blank_text=False, strip_cdata=False)
    root = etree.fromstring(data, parser)
    if root.getroottree().docinfo.doctype:
        raise ValueError('Office XML with a document type declaration is unsupported.')
    return root


def selected_part(name, extension):
    if extension == '.docx':
        return bool(re.fullmatch(r'word/(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml', name))
    return bool(re.fullmatch(r'ppt/(?:slides/slide\d+|notesSlides/notesSlide\d+|diagrams/(?:data|drawing)\d+)\.xml', name))


def text_groups(root):
    """Paragraph text across styled runs, split at fields, tabs and line breaks.

    Field state is computed across the entire part, since Word fields can span
    multiple paragraphs. Nested text boxes are handled once in their own p.
    """
    excluded = set()
    field_depth = 0
    for node in root.iter():
        if not isinstance(node.tag, str):
            continue
        tag = etree.QName(node)
        if tag.namespace in (W, WS) and tag.localname == 'fldChar':
            kind = node.get(f'{{{tag.namespace}}}fldCharType')
            if kind == 'begin':
                field_depth += 1
            elif kind == 'end':
                field_depth = max(0, field_depth - 1)
        if field_depth and node.tag in TEXT:
            excluded.add(node)

    def groups(paragraph):
        current = []
        def visit(node):
            if not isinstance(node.tag, str):
                return
            q = etree.QName(node)
            if node is not paragraph and node.tag in PARAGRAPHS:
                yield None
                return
            if (q.localname in ('fldSimple', 'fld', 'del', 'moveFrom', 'oMath', 'oMathPara',
                               'instrText', 'fldChar', 'br', 'cr', 'tab', 'ptab')
                    or node in excluded):
                yield None
                return
            if node.tag in TEXT:
                yield node
                return
            for child in node:
                yield from visit(child)
        for node in visit(paragraph):
            if node is None:
                if current:
                    yield current
                    current = []
            else:
                current.append(node)
        if current:
            yield current

    for paragraph in root.iter():
        if paragraph.tag in PARAGRAPHS:
            # Deleted text, equations and field containers can contain p nodes.
            if any(isinstance(a.tag, str) and etree.QName(a).localname in
                   ('del', 'moveFrom', 'fldSimple', 'fld', 'oMath', 'oMathPara')
                   for a in paragraph.iterancestors()):
                continue
            yield from groups(paragraph)


def replace_group(nodes, translated):
    """Keep matching text in its existing styled run; apportion changed spans.

    Translation changes word order, so styling within a translated phrase is
    approximate. No runs, properties, hyperlinks or surrounding elements drop.
    """
    original = ''.join(n.text or '' for n in nodes)
    ends, cursor = [], 0
    for node in nodes:
        cursor += len(node.text or '')
        ends.append(cursor)
    rendered = [''] * len(nodes)
    def owner(index):
        return min(bisect_right(ends, index), len(nodes) - 1)
    for kind, start, end, left, right in SequenceMatcher(None, original, translated, autojunk=False).get_opcodes():
        piece = translated[left:right]
        if kind == 'equal':
            for offset, character in enumerate(piece):
                rendered[owner(start + offset)] += character
        elif piece:
            for offset, character in enumerate(piece):
                position = start + min(max(0, end - start - 1), offset * max(1, end - start) // len(piece))
                rendered[owner(position)] += character
    for node, value in zip(nodes, rendered):
        node.text = value
        if value[:1].isspace() or value[-1:].isspace():
            node.set(XML_SPACE, 'preserve')


def verify_office_output(path, originals, replacements):
    """Check every saved ZIP member and each changed XML text node."""
    with ZipFile(path) as saved:
        if saved.testzip() or saved.namelist() != list(originals):
            raise RuntimeError('Saved Office verification failed: damaged or missing package parts.')
        for name, original in originals.items():
            content = saved.read(name)
            if name not in replacements:
                if content != original:
                    raise RuntimeError(f'Saved Office verification failed: unexpected change in {name}.')
                continue
            expected_bytes, expected_text = replacements[name]
            if content != expected_bytes:
                raise RuntimeError(f'Saved Office verification failed: changed text is missing in {name}.')
            root = parse_xml(content)
            if [n.text or '' for n in root.iter() if n.tag in TEXT] != expected_text:
                raise RuntimeError(f'Saved Office verification failed: text readback failed in {name}.')


def translate_office(source, destination, translate, progress=lambda *args: None,
                     cancel=lambda: False):
    source, destination = Path(source), Path(destination)
    extension = source.suffix.lower()
    if extension not in ('.docx', '.pptx'):
        raise ValueError('Use a .docx or .pptx file. Save older .doc/.ppt files in the newer format first.')
    if destination.suffix.lower() != extension:
        raise ValueError(f'The translated copy must use the same {extension} file extension.')
    if source.resolve() == destination.resolve() or (destination.exists() and os.path.samefile(source, destination)):
        raise ValueError('Choose a new output filename; the original document must be retained.')
    try:
        with ZipFile(source) as package:
            infos = package.infolist()
            if len({i.filename for i in infos}) != len(infos):
                raise ValueError('Office package contains duplicate parts. Save a fresh copy in Microsoft Office first.')
            originals = {i.filename: package.read(i) for i in infos}
            archive_comment = package.comment
    except BadZipFile as exc:
        raise ValueError('Cannot read this Office file. For password-protected or older files, save an unlocked .docx/.pptx copy first.') from exc
    required = 'word/document.xml' if extension == '.docx' else 'ppt/presentation.xml'
    if required not in originals or '[Content_Types].xml' not in originals:
        raise ValueError('This file is not a valid document of the selected Office format.')
    if any(name.startswith('_xmlsignatures/') for name in originals):
        raise ValueError('Digitally signed Office files are unsupported. Save an unsigned copy first.')
    parts = [name for name in originals if selected_part(name, extension)]
    replacements, entries = {}, []
    changed = unchanged = retained = glossary_hits = review_labels = extracted = 0
    for index, name in enumerate(parts):
        if cancel():
            raise InterruptedError('Translation cancelled; no output document was saved.')
        root = parse_xml(originals[name])
        part_changed = False
        for nodes in text_groups(root):
            if cancel():
                raise InterruptedError('Translation cancelled; no output document was saved.')
            original = ''.join(n.text or '' for n in nodes)
            if not re.search(r'[^\W\d_]', original):
                continue
            if reference_label(original.strip(), translate):
                retained += 1
                continue
            extracted += 1
            translated = protected_translate(original, translate)
            if not translated.strip():
                raise RuntimeError('Translation returned empty text. No output document was saved.')
            terms = getattr(translate, 'glossary_matches', lambda s: [])(original)
            reviews = getattr(translate, 'review_notes', lambda s: [])(original)
            glossary_hits += len(terms)
            review_labels += bool(reviews)
            entry = f'PART {name}\nOriginal: {original}\nEnglish: {translated}\n'
            if terms:
                entry += 'Glossary: ' + '; '.join(t['source'] + ' -> ' + t['english'] for t in terms) + '\n'
            if reviews:
                entry += 'REVIEW CONTEXT: ' + ' | '.join(reviews) + '\n'
            if translated == original:
                unchanged += 1
                reason = getattr(translate, 'unchanged_reason', lambda text: 'No change from the translator; check source language, spelling and context.')(original)
                entry += 'Status: UNCHANGED - ' + reason + '\n'
            else:
                replace_group(nodes, translated)
                changed += 1
                part_changed = True
                entry += 'Status: REPLACED in editable Office text.\n'
            entries.append(entry)
        if part_changed:
            data = etree.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
            replacements[name] = (data, [n.text or '' for n in root.iter() if n.tag in TEXT])
        progress(index + 1, len(parts))
    if not extracted:
        raise ValueError('No translatable editable text was found. Text inside pictures needs OCR, which this build does not include.')
    if cancel():
        raise InterruptedError('Translation cancelled; no output document was saved.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(suffix=extension, dir=destination.parent)
    os.close(descriptor)
    try:
        with ZipFile(temporary, 'w') as saved:
            saved.comment = archive_comment
            for info in infos:
                saved.writestr(info, replacements.get(info.filename, (originals[info.filename],))[0])
        verify_office_output(temporary, originals, replacements)
        if cancel():
            raise InterruptedError('Translation cancelled; no output document was saved.')
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    language = {'fr': 'French', 'nl': 'Dutch', 'de': 'German', 'auto': 'Auto / mixed languages'}.get(getattr(translate, 'language', None), 'Unspecified')
    report_path = destination.with_suffix('.translations.txt')
    warnings = ('Images and embedded objects are retained without OCR or translation. Fields, '
                'equations, chart caches and template/master text remain unchanged. '
                'Review text fit and styling in Microsoft Office; longer translations can reflow '
                'Word pages or overflow PowerPoint shapes. Mixed run styling is approximate.')
    report_path.write_text(
        f'Engineering Document Translator {VERSION} - English translation list\n'
        f'Source language: {language}; target: English; format: {extension}\n'
        f'Output file: {destination.name}\nFile SHA256: {digest}\n'
        f'Saved package reopened and checked: {changed} translated text groups; '
        f'{len(replacements)} changed parts. Other package parts match the original bytes.\n'
        f'Unchanged groups: {unchanged}; retained references/units: {retained}\n'
        f'Glossary matches: {glossary_hits}; groups needing context review: {review_labels}\n'
        f'{warnings}\n\n' + '\n'.join(entries), encoding='utf-8')
    return {'format': extension, 'translated': changed, 'unchanged': unchanged,
            'retained': retained, 'glossary_terms': glossary_hits, 'review_labels': review_labels,
            'verified_groups': changed, 'verified_parts': len(replacements),
            'file_sha256': digest, 'report': str(report_path), 'warnings': warnings}
