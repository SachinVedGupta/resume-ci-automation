"""Validated shared YAML + inherited variants, rendered as escaped LaTeX."""
from copy import deepcopy
from pathlib import Path
import re
from urllib.parse import urlparse
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')
class Link(Model):
    label: str
    url: str
class Education(Model):
    institution: str
    dates: str
    degree: str
    location: str
    details: list[str]
class Experience(Model):
    title: str
    dates: str
    company: str
    location: str
    details: list[str]
    url: str = ''
class Project(Model):
    title: str
    technologies: str
    details: list[str]
    url: str = ''
class Resume(Model):
    name: str
    citizenship: str = ''
    email: str
    phone: str
    links: list[Link]
    education: list[Education]
    experiences: dict[str, Experience]
    projects: dict[str, Project]
    skills: dict[str, str]
class Variant(Model):
    label: str
    extends: str | None = None
    experiences: list[str] | None = None
    projects: list[str] | None = None
    bullet_order: dict[str, list[int]] = Field(default_factory=dict)
    overrides: dict = Field(default_factory=dict)

class UniqueLoader(yaml.SafeLoader):
    pass
def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
def read_yaml(path):
    value = yaml.load(path.read_text(), Loader=UniqueLoader)
    if not isinstance(value, dict):
        raise ValueError(f'{path}: expected a YAML mapping')
    return value

def merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else deepcopy(value)
    return result

def variant_path(name, root=ROOT):
    if not re.fullmatch(r'[a-z0-9-]+(?:/[a-z0-9-]+)*', name):
        raise ValueError('Variant names use lowercase letters, numbers, hyphens and folders')
    path = root / 'variants' / f'{name}.yaml'
    if not path.resolve().is_relative_to((root / 'variants').resolve()):
        raise ValueError('Variant must stay inside variants/')
    return path

def resolve_variant(name, root=ROOT, seen=()):
    if name in seen:
        raise ValueError(f'Variant inheritance cycle: {" -> ".join((*seen, name))}')
    raw = Variant.model_validate(read_yaml(variant_path(name, root))).model_dump(exclude_none=True)
    parent = raw.pop('extends', None)
    # Defaults must not erase the inherited dictionaries.
    if parent:
        return merge(resolve_variant(parent, root, (*seen, name)), raw)
    return raw

def resolve_resume(name='general', root=ROOT):
    base = Resume.model_validate(read_yaml(root / 'data/resume.yaml')).model_dump()
    variant = resolve_variant(name, root)
    data = Resume.model_validate(merge(base, variant.get('overrides', {}))).model_dump()
    for kind in ('experiences', 'projects'):
        order = variant.get(kind, list(data[kind]))
        if len(order) != len(set(order)):
            raise ValueError(f'Duplicate IDs in {kind}')
        missing = set(order) - data[kind].keys()
        if missing:
            raise ValueError(f'Unknown {kind}: {sorted(missing)}')
        data[kind] = {key: data[kind][key] for key in order}
    for key, order in variant.get('bullet_order', {}).items():
        entry = data['experiences'].get(key) or data['projects'].get(key)
        if entry is None:
            raise ValueError(f'Unknown bullet_order ID: {key}')
        if len(order) != len(set(order)) or any(i < 0 or i >= len(entry['details']) for i in order):
            raise ValueError(f'Invalid bullet indices for {key}')
        entry['details'] = [entry['details'][i] for i in order]
    return data, variant['label']

ESCAPES = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','<':r'\textless{}','>':r'\textgreater{}','×':r'\ensuremath{\times}'}
def escape_plain(text):
    text = str(text).replace('–', '--').replace('—', '---').replace('’', "'").replace('“', '``').replace('”', "''")
    return ''.join(ESCAPES.get(c,c) for c in text)
def latex_url(url):
    if urlparse(url).scheme not in {'https','http','mailto'} or any(c in url for c in '{}\\\n\r'):
        raise ValueError(f'Invalid URL: {url}')
    return escape_plain(url)
def latex_escape(text):
    # Tokenize before escaping: never re-escape generated LaTeX commands.
    parts = re.split(r'(\*\*[^*]+\*\*|\[[^\]]+\]\(https?://[^\s)]+\))', str(text))
    output = []
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            output.append(r'\textbf{' + escape_plain(part[2:-2]) + '}')
        elif re.fullmatch(r'\[[^\]]+\]\(https?://[^\s)]+\)',part):
            label,url = re.fullmatch(r'\[([^\]]+)\]\((.+)\)',part).groups()
            output.append(r'\href{' + latex_url(url) + '}{' + escape_plain(label) + '}')
        else:
            output.append(escape_plain(part))
    return ''.join(output)

def generate_latex_resume(variant='general', root=ROOT):
    data, _ = resolve_resume(variant, root)
    env = Environment(loader=FileSystemLoader(root/'templates'), undefined=StrictUndefined,
                      block_start_string='<BLOCK>', block_end_string='</BLOCK>',
                      variable_start_string='<VAR>', variable_end_string='</VAR>',
                      comment_start_string='<#', comment_end_string='#>', trim_blocks=True,
                      autoescape=False)
    env.filters.update(latex_escape=latex_escape, latex_url=latex_url)
    return env.get_template('resume_template.tex.j2').render(**data)
