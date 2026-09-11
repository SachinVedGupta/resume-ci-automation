import tempfile
import unittest
from pathlib import Path
import yaml
from resume_ci_automation.latex_generator import latex_escape, latex_url, read_yaml, resolve_resume, resolve_variant, variant_path
class ResumeTests(unittest.TestCase):
    def test_special_characters(self):
        self.assertEqual(latex_escape('R&D 21% $10 **C++**'),r'R\&D 21\% \$10 \textbf{C++}')
        self.assertEqual(latex_escape('a\\b'),r'a\textbackslash{}b')
        self.assertIn(r'\href{https://example.com}{Link}',latex_escape('[Link](https://example.com)'))
    def test_latex_injection_is_text(self):
        self.assertEqual(latex_escape(r'\input{secret}'),r'\textbackslash{}input\{secret\}')
        with self.assertRaises(ValueError):latex_url(r'https://example.com/}\input{x}')
    def test_traversal_rejected(self):
        for name in ('../secret','/tmp/foo','a/../../b','UPPER'):
            with self.assertRaises(ValueError):variant_path(name)
    def test_shared_source_not_mutated(self):
        general,_=resolve_resume()
        swe,_=resolve_resume('swe')
        again,_=resolve_resume()
        self.assertEqual(general,again)
        self.assertEqual(swe['experiences']['shopify']['details'][0],general['experiences']['shopify']['details'][2])
    def test_duplicate_yaml_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.yaml';p.write_text('name: A\nname: B\n')
            with self.assertRaises(ValueError):read_yaml(p)
    def test_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'variants').mkdir()
            for a,b in [('a','b'),('b','a')]:
                (root/f'variants/{a}.yaml').write_text(f'label: {a}\nextends: {b}\n')
            with self.assertRaisesRegex(ValueError,'cycle'):resolve_variant('a',root)
    def test_invalid_selection_and_unknown_fields(self):
        from resume_ci_automation.latex_generator import ROOT
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'data',root/'data');shutil.copytree(ROOT/'variants',root/'variants')
            p=root/'variants/bad.yaml'
            for content in ['label: Bad\nexperiences: [missing]\n','label: Bad\noverrides:\n  typo: value\n','label: Bad\nbullet_order:\n  microsoft: [-1]\n']:
                p.write_text(content)
                with self.assertRaises(ValueError):resolve_resume('bad',root)
if __name__=='__main__':unittest.main()
