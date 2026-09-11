import argparse
import shutil
from .latex_generator import ROOT, resolve_resume, variant_path
from .pdf_generator import build_all, generate_pdf, variants

def main():
    parser=argparse.ArgumentParser(description='Build, validate, or create resume variants')
    parser.add_argument('--variant', default='general')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--new', metavar='companies/acme-swe')
    parser.add_argument('--from', dest='parent', default='swe')
    args=parser.parse_args()
    if args.new:
        resolve_resume(args.parent)
        path=variant_path(args.new)
        if path.exists(): parser.error('Variant already exists; choose another name')
        path.parent.mkdir(parents=True,exist_ok=True)
        import yaml
        path.write_text(yaml.safe_dump({'label':args.new.split('/')[-1].replace('-',' ').title(),'extends':args.parent},sort_keys=False))
        print(f'Created {path}')
    elif args.validate:
        for name in variants() if args.all else [args.variant]:
            resolve_resume(name)
            print(f'{name}: valid')
    elif args.all:
        build_all()
    else:
        generate_pdf(args.variant)
        if args.variant=='general':
            shutil.copy2(ROOT/'out/general/resume.pdf',ROOT/'out/resume.pdf')
if __name__=='__main__': main()
