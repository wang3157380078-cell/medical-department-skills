#!/usr/bin/env python3
"""Package the same skill as one portable private-plugin archive; never include cases."""
import argparse
import json
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

sys.dont_write_bytecode = True
from validate_installation import validate


def package(root, output):
    result = validate(root)
    if not result['passed']:
        raise ValueError(result['errors'])
    manifest = json.loads((root / 'manifest.json').read_text())
    paths = ['SKILL.md', 'agents/openai.yaml', 'manifest.json',
             'scripts/convert_modules.py', 'scripts/validate_installation.py',
             'scripts/package_plugin.py']
    for module in manifest['modules']:
        paths.extend([module['asset'], module['reference']])
    plugin = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
              'name': 'orthopedic-medical-records', 'version': manifest['version'],
              'description': '骨科AI病历书写助手V2.0：基于真实资料、按需调用20个完整模块并进行最终质控。',
              'extensions': {'com.openai': {'interface': {
                  'displayName': '骨科AI病历书写助手V2.0',
                  'shortDescription': '真实资料驱动的骨科医学文书与最终质控',
                  'longDescription': '个人骨科病历模板库，包含2026年10月25日V2.0全部20份Word及完整可检索参考模块。仅保存模板和规则，不包含实际患者病例。',
                  'category': 'Productivity',
                  'defaultPrompt': ['请使用骨科AI病历书写助手V2.0，根据我提供的真实病例资料完成所需医学文书。']}}}}
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = 'skills/write-orthopedic-medical-records/'
    with ZipFile(output, 'w', ZIP_DEFLATED) as z:
        z.writestr('plugin.json', json.dumps(plugin, ensure_ascii=False, indent=2) + '\n')
        for relative in paths:
            path = root / relative
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'Invalid package member: {relative}')
            z.write(path, prefix + relative)
    with ZipFile(output) as z:
        names = z.namelist()
        if z.testzip() is not None or len(names) != 47:
            raise ValueError('Plugin archive validation failed')
        for relative in paths:
            if z.read(prefix + relative) != (root / relative).read_bytes():
                raise ValueError(f'Plugin byte mismatch: {relative}')
    return {'archive': str(output.resolve()), 'files': len(names), 'word_files': 20,
            'reference_files': 20, 'skill_count': 1, 'bytes': output.stat().st_size,
            'created_on_service': False}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output', type=Path)
    ap.add_argument('--skill-dir', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    print(json.dumps(package(args.skill_dir, args.output), ensure_ascii=False, indent=2))
