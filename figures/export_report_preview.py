"""Export the prepared report for layout checks using a private, hidden Word instance."""
from pathlib import Path
import win32com.client

root = Path(__file__).resolve().parent.parent
source = root / "Kabore_Albert_Module_2_Assignment.docx"
target = root / "figures" / "report_export_review" / "word_layout_preview.pdf"
word = None
document = None
try:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    word.AutomationSecurity = 3
    document = word.Documents.Open(
        str(source), ConfirmConversions=False, ReadOnly=True,
        AddToRecentFiles=False, Visible=False,
    )
    document.Repaginate()
    document.Fields.Update()
    pages = document.ComputeStatistics(2)
    document.ExportAsFixedFormat(str(target), 17, OpenAfterExport=False)
    print(f"Word layout preview exported: {pages} pages.")
    print(target)
finally:
    if document is not None:
        document.Close(SaveChanges=0)
    if word is not None:
        word.Quit(SaveChanges=0)
