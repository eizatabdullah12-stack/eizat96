"""Offline PDF translation; never modify the source file."""
from pathlib import Path
import os
import re
import tempfile
import fitz

PROTECTED = re.compile(
    r"\b(?:HEA|HEB|HEM|IPE|IPN|UPN|UPE|RHS|SHS|CHS)\s*\d+(?:[.,]\d+)?(?:\s*[x×]\s*\d+(?:[.,]\d+)?)*\b"
    r"|\b(?:RDC|REZ|R)\s*\+\s*\d+\b"
    r"|\b[A-Z]+[-.]?\d+[A-Z0-9]*(?:[./-]\d+[A-Z0-9]*)*\b"
    r"|[Øø⌀]\s*\d+(?:[.,]\d+)?"
    r"|\b\d+(?:[.,]\d+)?(?:\s*(?:mm|cm|m|MPa|kN|kg|N|kPa|%))?\b", re.I)


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


def fit_text(rect, text, size):
    # Test on a separate page so failed insertions cannot affect the output.
    for scale in (1, .9, .8, .7, .6):
        fs = max(5, size * scale)
        with fitz.open() as probe:
            page = probe.new_page(width=max(100, rect.x1 + 10), height=max(100, rect.y1 + 10))
            if page.insert_textbox(rect, text, fontsize=fs, fontname="helv") >= 0:
                return fs
    return None


def translate_pdf(source, destination, translate, mode="replace", progress=lambda *args: None, cancel=lambda: False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Choose a new output filename; the original PDF must be retained.")
    if mode not in ("replace", "notes"):
        raise ValueError("Unknown output mode")
    report = []
    count = fallback = extracted = 0
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
                    if cancel():
                        raise InterruptedError("Translation cancelled; no output PDF was saved.")
                    translated = protected_translate(original, translate).strip()
                    extracted += 1
                    terms = getattr(translate, 'glossary_matches', lambda text: [])(original)
                    reviews = getattr(translate, 'review_notes', lambda text: [])(original)
                    glossary_hits += len(terms)
                    review_labels += bool(reviews)
                    if translated != original or reviews:
                        entry = f"PAGE {number + 1}\nOriginal: {original}\nEnglish: {translated}\n"
                        if terms:
                            entry += 'Glossary: ' + '; '.join(t['source'] + ' -> ' + t['english'] for t in terms) + '\n'
                        if reviews:
                            entry += 'REVIEW CONTEXT: ' + ' | '.join(reviews) + '\n'
                        report.append(entry)
                    if translated == original:
                        continue
                    rect = fitz.Rect(line["bbox"])
                    size = max(s["size"] for s in spans)
                    horizontal = abs(line.get("dir", (1, 0))[0] - 1) < .01
                    # Base-14 font is limited; preserve the original and use a note
                    # when a translation cannot be represented reliably.
                    encodable = all(ord(c) < 256 for c in translated)
                    fs = fit_text(rect, translated, size) if horizontal and encodable and mode == "replace" else None
                    if fs is None:
                        note_position = fitz.Point(max(1, rect.x0 - 23), max(1, rect.y0))
                        note = page.add_text_annot(note_position, translated)
                        note.set_info(title="English translation", content=f"Original: {original}\nEnglish: {translated}")
                        fallback += 1
                    else:
                        color = spans[0].get("color", 0)
                        rgb = ((color >> 16 & 255)/255, (color >> 8 & 255)/255, (color & 255)/255)
                        # Transparent fill: retain the underlying vector drawing.
                        page.add_redact_annot(rect, fill=False, cross_out=False)
                        items.append((rect, translated, fs, rgb))
                    count += 1
            if not page_text:
                scanned_pages.append(number + 1)
            if items:
                # Remove text only. Do not remove images or vector lines.
                page.apply_redactions(images=0, graphics=0, text=0)
                for rect, translated, fs, rgb in items:
                    if page.insert_textbox(rect, translated, fontname="helv", fontsize=fs, color=rgb) < 0:
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
    report_path.write_text("Engineering PDF Translator - English translation list\nTechnical glossary takes priority; other text uses machine translation.\nREVIEW CONTEXT marks ambiguous labels. Check the drawing detail/legend.\n" + f"Glossary matches: {glossary_hits}; labels needing context review: {review_labels}\n" + warnings + "\n".join(report), encoding="utf-8")
    return {"translated": count, "notes": fallback, "scanned_pages": scanned_pages, "report": str(report_path), "glossary_terms": glossary_hits, "review_labels": review_labels}
