"""Protect company isolation and last-successful preview behavior."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from resume_ci_automation import pdf_generator as pdf
from resume_ci_automation.latex_generator import ROOT, resolve_resume

class CompanyWorkflowTests(unittest.TestCase):
    def test_company_overrides_preserve_shared_fields_and_other_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ('data', 'variants'):
                shutil.copytree(ROOT/folder, root/folder)
            before, _ = resolve_resume('swe', root)
            (root/'variants/companies/test.yaml').write_text(
                'label: Test company\nextends: swe\nprojects: [nki]\n'
                'overrides:\n  experiences:\n    microsoft:\n'
                '      details: ["Tailored test bullet"]\n')
            company, _ = resolve_resume('companies/test', root)
            after, _ = resolve_resume('swe', root)
            self.assertEqual(before, after)
            self.assertEqual(company['experiences']['microsoft']['details'], ['Tailored test bullet'])
            self.assertEqual(company['experiences']['microsoft']['company'], 'Microsoft')
            self.assertEqual(company['experiences']['shopify'], before['experiences']['shopify'])
            self.assertEqual(list(company['projects']), ['nki'])

    def test_failed_batch_keeps_previous_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root/'out'; out.mkdir()
            (out/'previous.pdf').write_bytes(b'previous successful PDF')
            with patch.object(pdf, 'ROOT', root), patch.object(pdf, 'variants', return_value=['good', 'bad']), patch.object(pdf, 'generate_pdf', side_effect=[{}, ValueError('overflow')]):
                with self.assertRaisesRegex(ValueError, 'overflow'):
                    pdf.build_all()
            self.assertEqual((out/'previous.pdf').read_bytes(), b'previous successful PDF')

    def test_successful_batch_removes_obsolete_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root/'out'; out.mkdir()
            (out/'obsolete.pdf').write_bytes(b'old')
            def generate(name, destination):
                destination.mkdir(parents=True)
                (destination/'resume.pdf').write_bytes(b'new')
                return {'variant': name, 'label': 'New'}
            with patch.object(pdf, 'ROOT', root), patch.object(pdf, 'variants', return_value=['companies/test']), patch.object(pdf, 'generate_pdf', side_effect=generate):
                pdf.build_all()
            self.assertFalse((out/'obsolete.pdf').exists())
            self.assertEqual((out/'companies/test/resume.pdf').read_bytes(), b'new')
            self.assertIn('companies/test/README.md', (out/'README.md').read_text())
