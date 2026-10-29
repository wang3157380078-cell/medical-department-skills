#!/usr/bin/env python3
"""Complete searchable DOCX text conversion using only the standard library."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
EXPECTED = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
            '101', '102', '103', '104', '105', '106', '107', '108']
TEXT_TAGS = {W + 't', W + 'delText', W + 'instrText',
             '{http://schemas.openxmlformats.org/drawingml/2006/main}t'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parts(archive):
    return ['word/document.xml'] + sorted(n for n in archive.namelist() if
        (re.fullmatch(r'word/(header|footer)\d+\.xml', n) or
         n in ('word/footnotes.xml', 'word/endnotes.xml', 'word/comments.xml')))


def paragraph_text(p):
    out = []
    for e in p.iter():
        if e.tag in TEXT_TAGS:
            out.append(e.text or '')
        elif e.tag == W + 'tab':
            out.append('\t')
        elif e.tag in (W + 'br', W + 'cr'):
            out.append('\n')
    return ''.join(out)


def render_docx(path):
    lines = [f'# {path.stem}', '',
        '> 原始Word完整文本转换，非摘要。编号、段落和表格顺序保留；Word原始版式以assets内原文件为准。',
        '> 文内模拟病例和变量仅作示例，不属于任何当前患者。Word页码域保留其域代码及缓存值。', '']
    stats = {'paragraphs': 0, 'tables': 0, 'text_nodes': 0, 'text_characters': 0,
             'media_files': 0, 'parts': []}
    token_stream = []
    with ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError(f'Corrupt DOCX: {path.name}')
        stats['media_files'] = sum(n.startswith('word/media/') for n in z.namelist())
        if stats['media_files']:
            raise ValueError('Embedded media requires separate inspection before conversion')
        for part in parts(z):
            root = ET.fromstring(z.read(part))
            stats['parts'].append(part)
            tokens = [e.text or '' for e in root.iter() if e.tag in TEXT_TAGS]
            token_stream.extend(tokens)
            stats['text_nodes'] += len(tokens)
            stats['text_characters'] += sum(map(len, tokens))
            lines.extend([f'## 原文部件 `{part}`', ''])
            def visit(e):
                if e.tag == W + 'tbl':
                    stats['tables'] += 1
                    lines.append('<!-- 原文表格开始 -->')
                    for child in e:
                        visit(child)
                    lines.append('<!-- 原文表格结束 -->')
                elif e.tag in (W + 'tr', W + 'tc'):
                    label = '行' if e.tag == W + 'tr' else '单元格'
                    lines.append(f'<!-- 表格{label}开始 -->')
                    for child in e:
                        visit(child)
                    lines.append(f'<!-- 表格{label}结束 -->')
                elif e.tag == W + 'p':
                    if any(x.tag == W + 'p' for x in list(e.iter())[1:]):
                        raise ValueError('Nested Word paragraphs require a reviewed conversion')
                    stats['paragraphs'] += 1
                    lines.append(paragraph_text(e))
                else:
                    for child in e:
                        visit(child)
            visit(root)
            lines.append('')
    stats['text_stream_sha256'] = sha(json.dumps(token_stream, ensure_ascii=False).encode())
    return '\n'.join(lines) + '\n', stats


def convert(source, target):
    by_id = {}
    for p in source.glob('*.docx'):
        mid = p.stem.split('_', 1)[0]
        if mid in by_id:
            raise ValueError(f'Duplicate module {mid}')
        by_id[mid] = p
    if set(by_id) != set(EXPECTED):
        raise ValueError(f'Module mismatch: {sorted(by_id)}')
    manifest = {'skill_name': 'write-orthopedic-medical-records', 'version': '2.0.1',
                'source_date': '2026-10-25', 'conversion': 'complete-word-xml-text-v1',
                'source_directory': str(source.resolve()), 'modules': []}
    for mid in EXPECTED:
        src = by_id[mid]
        content, stats = render_docx(src)
        if '2026年10月25日' not in content or 'V2.0' not in content:
            raise ValueError(f'Unexpected edition: {src.name}')
        asset = target / 'assets' / src.name
        ref = target / 'references' / (src.stem + '.md')
        asset.parent.mkdir(parents=True, exist_ok=True)
        ref.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != asset.resolve():
            shutil.copy2(src, asset)
        ref.write_text(content, encoding='utf-8')
        manifest['modules'].append({'id': mid, 'level': 1 if mid in ('00', '01') else
            3 if len(mid) == 3 else 2, 'title': src.stem.split('_', 1)[1],
            'asset': str(asset.relative_to(target)), 'reference': str(ref.relative_to(target)),
            'asset_sha256': sha(asset.read_bytes()), 'reference_sha256': sha(ref.read_bytes()),
            'bytes': asset.stat().st_size, **stats})
    (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source_dir', type=Path)
    ap.add_argument('--skill-dir', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    m = convert(args.source_dir, args.skill_dir)
    print(f"Converted {len(m['modules'])} complete modules; originals copied byte-for-byte.")
