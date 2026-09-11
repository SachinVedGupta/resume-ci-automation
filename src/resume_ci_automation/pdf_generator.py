"""Build PDFs, visible previews and traceable resolved YAML snapshots."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import fitz
import yaml
from .latex_generator import ROOT, generate_latex_resume, resolve_resume, variant_path

def variants():
    return sorted(p.relative_to(ROOT/'variants').with_suffix('').as_posix() for p in (ROOT/'variants').rglob('*.yaml'))

def generate_pdf(variant='general', output_dir=None):
    variant_path(variant)
    data, label = resolve_resume(variant)
    out = Path(output_dir) if output_dir else ROOT/'out'/variant
    out.mkdir(parents=True, exist_ok=True)
    tex = generate_latex_resume(variant)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp/'resume.tex').write_text(tex)
        tectonic = shutil.which('tectonic') or (str(ROOT/'.tools/tectonic') if (ROOT/'.tools/tectonic').exists() else None)
        if shutil.which('pdflatex'):
            command = ['pdflatex','-no-shell-escape','-halt-on-error','-interaction=nonstopmode','resume.tex']
        elif tectonic:
            command = [tectonic,'--keep-logs','resume.tex']
        else:
            raise RuntimeError('Install pdflatex or tectonic, or use docker compose up --build')
        result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError(f'{variant}: LaTeX failed\n{result.stdout}\n{result.stderr}')
        pdf = tmp/'resume.pdf'
        with fitz.open(pdf) as doc:
            if len(doc) != 1:
                raise ValueError(f'{variant}: expected one page, got {len(doc)}. Shorten content in YAML.')
            page = doc[0]
            if data['name'] not in page.get_text():
                raise ValueError(f'{variant}: PDF text extraction failed')
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    x0,y0,x1,y1 = line['bbox']
                    if x0 < 15 or y0 < 8 or x1 > page.rect.width-15 or y1 > page.rect.height-8:
                        raise ValueError(f'{variant}: text exceeds safe page bounds: {line["bbox"]}')
            page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False).save(str(tmp/'preview.png'))
            (tmp/'resume.txt').write_text(page.get_text())
        source = os.environ.get('SOURCE_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        manifest = {'variant':variant,'label':label,'source_commit':source,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':1}
        (tmp/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        (tmp/'resolved.yaml').write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
        for file in ('resume.pdf','resume.tex','preview.png','resume.txt','manifest.json','resolved.yaml'):
            shutil.copy2(tmp/file,out/file)
    (out/'README.md').write_text(f'# {label}\n\nSource commit: `{source}`\n\n[Download PDF](resume.pdf) · [Resolved YAML](resolved.yaml)\n\n![Resume preview](preview.png)\n')
    print(f'{variant}: one page, text verified → {out / "resume.pdf"}')
    return manifest

def build_all():
    # Clean staging prevents removed variants from lingering in published output.
    out=ROOT/'out'
    if out.exists():
        for child in out.iterdir():
            if child.is_dir() and not child.is_symlink(): shutil.rmtree(child)
            else: child.unlink()
    manifests=[generate_pdf(name) for name in variants()]
    lines=['# Resume previews','','These files are generated. Edit data/resume.yaml or variants/ in the source branch.','','| Version | Preview | PDF |','|---|---|---|']
    for m in manifests:
        name=m['variant'];lines.append(f'| {m["label"]} | [View]({name}/README.md) | [PDF]({name}/resume.pdf) |')
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    return manifests
