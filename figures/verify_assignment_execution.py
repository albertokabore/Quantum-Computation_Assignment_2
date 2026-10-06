"""Execute notebook cells directly and save their genuine captured outputs."""
import base64
import contextlib
import io
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import nbformat
import IPython.display
from nbconvert import HTMLExporter

root = Path(__file__).resolve().parent.parent
notebook_path = root / 'Assignment2_Quantum_Circuits.ipynb'
nb = nbformat.read(notebook_path, as_version=4)
scope = {}
outputs = []
buffer = io.StringIO()

def flush():
    value = buffer.getvalue()
    if value:
        outputs.append(nbformat.v4.new_output('stream', name='stdout', text=value))
        buffer.seek(0)
        buffer.truncate(0)

def capture(figure):
    flush()
    blob = io.BytesIO()
    figure.savefig(blob, format='png', dpi=100, bbox_inches='tight')
    outputs.append(nbformat.v4.new_output('display_data', data={
        'image/png': base64.b64encode(blob.getvalue()).decode('ascii')}, metadata={}))

IPython.display.display = capture
execution = 0
for index, cell in enumerate(nb.cells):
    if cell.cell_type != 'code':
        continue
    execution += 1
    outputs = []
    with contextlib.redirect_stdout(buffer):
        exec(compile(cell.source, f'notebook-cell-{index}', 'exec'), scope)
    flush()
    cell.outputs = outputs
    cell.execution_count = execution
    for output in outputs:
        if output.output_type == 'stream':
            print(output.text)

assert scope['counts_h'] == {'0': 526, '1': 498}
assert scope['counts_y'] == {'0': 0, '1': 1024}
assert scope['counts_z'] == {'0': 1024, '1': 0}
nbformat.write(nb, notebook_path)
templates = str(Path(sys.base_prefix) / 'share' / 'jupyter' / 'nbconvert' / 'templates')
html, _ = HTMLExporter(extra_template_basedirs=[templates], extra_template_paths=[templates]).from_notebook_node(nb)
# Compact Markdown typography for screenshots of the exported notebook.
compact_style = """<style>
.jp-MarkdownCell .jp-RenderedHTMLCommon { font-size: 12px; line-height: 1.35; }
.jp-MarkdownCell .jp-RenderedHTMLCommon h3 { font-size: 18px; }
.jp-MarkdownCell .jp-RenderedHTMLCommon h4 { font-size: 15px; }
.jp-MarkdownCell .jp-RenderedHTMLCommon mjx-container { font-size: 95% !important; }
</style>"""
html = html.replace('</head>', compact_style + '\n</head>')
(root / 'figures' / 'Assignment2_Executed_Notebook.html').write_text(html, encoding='utf-8')
print('All notebook cells executed; actual outputs saved and report counts verified.')
