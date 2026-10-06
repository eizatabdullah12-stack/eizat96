"""Offline PDF translation; never modify the source file."""
from pathlib import Path
import os
import re
import tempfile
import fitz

PROTECTED = re.compile(
    r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b|\b(?:https?://|www\.)[^\s]+"
    r"|\b(?:HEA|HEB|HEM|IPE|IPN|UPN|UPE|RHS|SHS|CHS)\s*\d+(?:[.,]\d+)?(?:\s*[x×]\s*\d+(?:[.,]\d+)?)*\b"
    r"|\b(?:RDC|REZ|R)\s*\+\s*\d+\b"
    r"|\b[A-Z]+[-.]?\d+[A-Z0-9]*(?:[./-]\d+[A-Z0-9]*)*\b"
    r"|[Øø⌀]\s*\d+(?:[.,]\d+)?"
    r"|\b\d+(?:[.,]\d+)?(?:\s*[x×]\s*\d+(?:[.,]\d+)?)+(?:\s*(?:mm|cm|m))?\b"
    r"|\b\d+(?:[.,]\d+)?(?:\s*(?:N/mm[²2]|kN/m[²2]?|mm|cm|μm|m|MPa|kN|kg|N|kPa|%))?\b", re.I)

DRAWING_CODES = re.compile(r"\b(?:NI|NS|BA|HBA|HBP|PE|DCSP|PD|BAP|BNA|BF|BP|TS|PF|SEM|FP|MP|AD|AO|LP|BM|LC|BES|NBN|REI|EI|EE|HEA|HEB|HEM|IPE|IPN|UPN|UPE|RHS|SHS|CHS)\b")
PROTECTED = re.compile(PROTECTED.pattern + r"|\b(?:N/mm[²2]|kN/m[²2]?|μm|mm|cm|MPa|kPa)\b|(?-i:" + DRAWING_CODES.pattern + r")", re.I)
LABEL_FONT = fitz.Font('helv')
LABEL_FONT_NAME = 'engineeringlabel'


def reference_label(text):
    """Retain drawing references, units and contact identifiers, not prose."""
    if re.fullmatch(r"[A-Z]\.[A-Z]{2,}|[A-Z]{1,4}\s+\d+[a-z]", text):
        return True
    if re.match(r"^(?:Rue|Avenue|Chaussée|Boulevard|Straat|Straße)\b", text) or re.match(r"^\d{4,6}\s+[^\W\d_]", text):
        return True
    remaining = PROTECTED.sub("", text)
    remaining = DRAWING_CODES.sub("", remaining)
    remaining = re.sub(r"\b(?:mm|cm|m|MPa|kN|kg|N|kPa|μm|Fb|Fm)\b|[x×Øø⌀□]", "", remaining)
    remaining = re.sub(r"\b[A-Z](?:\.[A-Z])?\b", "", remaining)
    return not re.search(r"[^\W\d_]", remaining)


def text_rotation(direction):
    for vector, angle in (((1, 0), 0), ((0, -1), 90), ((-1, 0), 180), ((0, 1), 270)):
        if all(abs(a - b) < .01 for a, b in zip(direction, vector)):
            return angle
    return None


def protected_translate(text, translate):
    # Translate only words between dimensions/codes: no fragile placeholder tokens.
    parts, cursor = [], 0
    for match in PROTECTED.finditer(text):
        parts.append(translate(text[cursor:match.start()]) if re.search(r"[^\W\d_]", text[cursor:match.start()]) else text[cursor:match.start()])
        parts.append(match.group())
        cursor = match.end()
    tail = text[cursor:]
    parts.append(translate(tail) if re.search(r"[^\W\d_]", tail) else tail)
    return "".join(parts)


def fit_text(rect, text, size, rotation=0):
    # Test on a separate page so failed insertions cannot affect the output.
    for scale in (1, .9, .8, .7, .6, .55, .5):
        # CAD fonts can be smaller than 5pt. A fixed 5pt minimum prevented
        # translations fitting their original label boxes on large sheets.
        fs = size * scale
        with fitz.open() as probe:
            page = probe.new_page(width=max(100, rect.x1 + 10), height=max(100, rect.y1 + 10))
            page.insert_font(fontname=LABEL_FONT_NAME,fontbuffer=LABEL_FONT.buffer)
            if page.insert_textbox(rect, text, fontsize=fs, fontname=LABEL_FONT_NAME, rotate=rotation) >= 0:
                return fs
    return None


def translate_pdf(source, destination, translate, mode="replace", progress=lambda *args: None, cancel=lambda: False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Choose a new output filename; the original PDF must be retained.")
    if mode not in ("replace", "notes"):
        raise ValueError("Unknown output mode")
    report = []
    count = fallback = extracted = unchanged = retained = 0
    glossary_hits = review_labels = 0
    scanned_pages = []
    destination.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(source) as doc:
        if doc.needs_pass:
            raise ValueError("This PDF is password-protected. Save an unlocked copy first.")
        for number, page in enumerate(doc):
            if cancel():
                raise InterruptedError("Translation cancelled; no output PDF was saved.")
            items = []
            page_text = 0
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    spans = line["spans"]
                    original = "".join(s["text"] for s in spans).strip()
                    if not original:
                        continue
                    page_text += len(original)
                    if not re.search(r"[^\W\d_]", original):
                        continue
                    if reference_label(original):
                        retained += 1
                        continue
                    if cancel():
                        raise InterruptedError("Translation cancelled; no output PDF was saved.")
                    translated = protected_translate(original, translate).strip()
                    extracted += 1
                    terms = getattr(translate, 'glossary_matches', lambda text: [])(original)
                    reviews = getattr(translate, 'review_notes', lambda text: [])(original)
                    glossary_hits += len(terms)
                    review_labels += bool(reviews)
                    entry = f"PAGE {number + 1}\nOriginal: {original}\nEnglish: {translated}\n"
                    if terms:
                        entry += 'Glossary: ' + '; '.join(t['source'] + ' -> ' + t['english'] for t in terms) + '\n'
                    if reviews:
                        entry += 'REVIEW CONTEXT: ' + ' | '.join(reviews) + '\n'
                    if translated == original:
                        unchanged += 1
                        report.append(entry + 'Status: UNCHANGED - check whether translation is needed.\n')
                        continue
                    rect = fitz.Rect(line["bbox"])
                    size = max(s["size"] for s in spans)
                    # Extraction and insertion both use unrotated coordinates.
                    # A page displayed at 270 degrees commonly has (0, 1)
                    # text directions; that text can be replaced at rotate=270.
                    rotation = text_rotation(line.get("dir", (1, 0)))
                    # Embed the font rather than Base-14 Latin-1 insertion, which
                    # silently turns engineering symbols such as μ into '?'.
                    encodable = all(c.isspace() or LABEL_FONT.has_glyph(ord(c)) for c in translated)
                    fs = fit_text(rect, translated, size, rotation) if rotation is not None and encodable and mode == "replace" else None
                    if fs is None:
                        note_position = fitz.Point(max(1, rect.x0 - 23), max(1, rect.y0))
                        note = page.add_text_annot(note_position, translated)
                        note.set_info(title="English translation", content=f"Original: {original}\nEnglish: {translated}")
                        fallback += 1
                        reason = 'notes-only mode' if mode == 'notes' else 'oblique text' if rotation is None else 'font character support' if not encodable else 'translation exceeds label space'
                        report.append(entry + f'Status: NOTE - {reason}.\n')
                    else:
                        color = spans[0].get("color", 0)
                        rgb = ((color >> 16 & 255)/255, (color >> 8 & 255)/255, (color & 255)/255)
                        # Transparent fill: retain the underlying vector drawing.
                        page.add_redact_annot(rect, fill=False, cross_out=False)
                        items.append((rect, translated, fs, rgb, rotation))
                        report.append(entry + 'Status: REPLACED on drawing.\n')
                    count += 1
            if not page_text:
                scanned_pages.append(number + 1)
            if items:
                # Remove text only. Do not remove images or vector lines.
                page.apply_redactions(images=0, graphics=0, text=0)
                page.insert_font(fontname=LABEL_FONT_NAME,fontbuffer=LABEL_FONT.buffer)
                for rect, translated, fs, rgb, rotation in items:
                    if page.insert_textbox(rect, translated, fontname=LABEL_FONT_NAME, fontsize=fs, color=rgb, rotate=rotation) < 0:
                        raise RuntimeError("Text layout changed unexpectedly. Output was not saved.")
            progress(number + 1, len(doc))
        if not extracted:
            raise ValueError("No translatable text was found. Scanned/image-only PDFs need OCR, which this build does not include.")
        if cancel():
            raise InterruptedError("Translation cancelled; no output PDF was saved.")
        fd, temp = tempfile.mkstemp(suffix=".pdf", dir=destination.parent)
        os.close(fd)
        try:
            doc.save(temp, garbage=4, deflate=True)
            os.replace(temp, destination)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    warnings = f"\nPages without extractable text (not translated): {scanned_pages}\n" if scanned_pages else ""
    report_path = destination.with_suffix(".translations.txt")
    report_path.write_text("Engineering PDF Translator - English translation list\nTechnical glossary takes priority; other text uses machine translation.\nREVIEW CONTEXT marks ambiguous labels. Check the drawing detail/legend.\nUNCHANGED may include proper names, already-English text or untranslated words.\n" + f"Replaced on drawing: {count-fallback}; notes: {fallback}; unchanged labels to check: {unchanged}; retained references/units: {retained}\nGlossary matches: {glossary_hits}; labels needing context review: {review_labels}\n" + warnings + "\n".join(report), encoding="utf-8")
    return {"translated": count, "replaced": count-fallback, "notes": fallback, "unchanged": unchanged, "retained": retained, "scanned_pages": scanned_pages, "report": str(report_path), "glossary_terms": glossary_hits, "review_labels": review_labels}
