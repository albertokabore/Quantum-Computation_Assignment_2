"""Make the PDF's gate-specific subsection headings self-contained."""
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "Kabore_Albert_Module_2_Assignment.pdf"
doc = pymupdf.open(REPORT)
heading_font = ROOT / "figures" / "report_heading_font.otf"
math_font = next(entry for entry in doc[6].get_fonts() if entry[1] == "otf")
heading_font.write_bytes(doc.extract_font(math_font[0])[3])

changes = 0
for first_page, gate in ((4, "H"), (7, "Y"), (10, "Z")):
    state = gate + "|0⟩"
    replacements = {
        "(i) Measure the output — histogram screenshot":
            f"(i) Measurement histogram for {state}",
        "(ii) Circuit screenshot after running draw()":
            f"(ii) Circuit diagram for {state} from draw()",
        "(iii) Output state, probabilities, and histogram veriﬁcation":
            f"(iii) {state}: output state, probabilities, and verification",
        "Predicted probabilities":
            f"Predicted measurement probabilities for {state}",
        "Veriﬁcation against the histogram in (i)":
            f"Verification against the {state} histogram on page {first_page + 1}",
    }
    for page in list(doc)[first_page:first_page + 3]:
        pending = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"] in replacements:
                        pending.append((span, replacements[span["text"]]))
                        page.add_redact_annot(span["bbox"], fill=(1, 1, 1))
        if not pending:
            continue
        page.apply_redactions(images=0, graphics=0)
        for span, replacement in pending:
            font_path = heading_font
            font = pymupdf.Font(fontfile=str(font_path))
            size = min(span["size"], 514 / font.text_length(replacement, fontsize=1))
            page.insert_font(fontname="clearheading", fontfile=str(font_path))
            page.insert_text(span["origin"], replacement, fontsize=size,
                             fontname="clearheading", color=(0, 0, 0))
            changes += 1

assert changes == 15, changes
temporary = REPORT.with_suffix(".clarified.pdf")
doc.save(temporary, garbage=4, deflate=True)
doc.close()
with pymupdf.open(temporary) as check:
    assert len(check) == 14
    for index, gate in ((6, "H"), (9, "Y"), (12, "Z")):
        text = check[index].get_text()
        assert f"(iii) {gate}|0⟩: output state, probabilities, and verification" in text
        assert "Predicted measurement probabilities for" in text
temporary.replace(REPORT)
heading_font.unlink()
print(f"Updated and verified {changes} subsection headings in {REPORT.name}.")
