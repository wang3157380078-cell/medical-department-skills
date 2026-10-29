#!/usr/bin/env python3
"""Validate module identity, source hashes, complete text coverage and links."""
import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

sys.dont_write_bytecode = True
from convert_modules import EXPECTED, TEXT_TAGS, parts, render_docx, sha


def validate(root, source=None):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    m = json.loads((root / 'manifest.json').read_text())
    ids = [x['id'] for x in m['modules']]
    check(ids == EXPECTED, 'Manifest must contain exactly 20 unique modules in priority order')
    check(len(list((root / 'assets').glob('*.docx'))) == 20, 'Expected exactly 20 original Word files')
    check(len(list((root / 'references').glob('*.md'))) == 20, 'Expected exactly 20 reference modules')
    total_text = 0
    for entry in m['modules']:
        asset, ref = root / entry['asset'], root / entry['reference']
        if not asset.is_file() or not ref.is_file():
            errors.append(f"Missing module files: {entry['id']}")
            continue
        check(sha(asset.read_bytes()) == entry['asset_sha256'], f'Word changed: {asset.name}')
        check(sha(ref.read_bytes()) == entry['reference_sha256'], f'Reference changed: {ref.name}')
        expected, stats = render_docx(asset)
        actual = ref.read_text(encoding='utf-8')
        check(actual == expected, f'Complete reference cannot be reproduced: {ref.name}')
        for key, value in stats.items():
            check(entry.get(key) == value, f'Manifest statistics mismatch: {entry["id"]}/{key}')
        offset = 0
        with ZipFile(asset) as z:
            for part in parts(z):
                xml_root = ET.fromstring(z.read(part))
                for node in xml_root.iter():
                    if node.tag not in TEXT_TAGS or not node.text:
                        continue
                    at = actual.find(node.text, offset)
                    check(at >= 0, f'Original text missing/out of order: {entry["id"]}/{part}')
                    if at >= 0:
                        offset = at + len(node.text)
        if source is not None:
            original = source / asset.name
            check(original.is_file(), f'Original source missing: {asset.name}')
            if original.is_file():
                check(original.read_bytes() == asset.read_bytes(), f'Source byte mismatch: {asset.name}')
        total_text += entry['text_characters']
    skill = (root / 'SKILL.md').read_text(encoding='utf-8')
    check('name: write-orthopedic-medical-records' in skill, 'Wrong skill name')
    for path in re.findall(r'\]\(([^)]+)\)', skill):
        if '://' not in path:
            check((root / path.split('#')[0]).is_file(), f'Broken internal link: {path}')
    check((root / 'agents/openai.yaml').is_file(), 'Missing agents/openai.yaml')
    return {'passed': not errors, 'modules': len(ids), 'original_word_files':
            len(list((root / 'assets').glob('*.docx'))), 'complete_reference_files':
            len(list((root / 'references').glob('*.md'))),
            'original_text_characters': total_text, 'errors': errors,
            'limits': 'Integrity validation only; not clinical validation or proof of model behavior.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skill-dir', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--source-dir', type=Path)
    args = ap.parse_args()
    try:
        result = validate(args.skill_dir, args.source_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['passed'] else 1)
