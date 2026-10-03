from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md','QUICKSTART.md','CITATION.cff','LICENSE','THIRD_PARTY_LICENSES.md',
    'requirements.txt','environment.yml','pytest.ini','REPOSITORY_MANIFEST.csv',
    'config/study_config.yaml','docs/METHOD_PROTOCOL.md','docs/FROZEN_RESULTS.md',
    'docs/REPRODUCIBILITY.md','docs/CLAIM_BOUNDARIES.md','docs/COMPUTATIONAL_VALIDATION.md',
    'docs/DATA_PROVENANCE.md','docs/LITERATURE_CONTEXT.md','docs/SUBMISSION_METADATA.md',
    'docs/assets/repository-banner.svg','docs/assets/claim-evidence-framework.svg',
    'docs/assets/certificate-anatomy.svg','docs/assets/complexity-landscape.svg',
    'examples/illustrative_instance.json','src/automata_support.py','src/domain_pruning.py',
    'src/tree_dp.py','src/treewidth_dp.py','src/fvs.py','src/evidence_cover.py','src/certificates.py',
    'src/experiments.py','tests/test_algorithms.py','results/frozen/summary.json',
    'results/frozen/tree_validation.csv','results/frozen/fvs_validation.csv',
    'results/frozen/correction_validation.csv','results/frozen/tree_scalability.csv',
    'results/frozen/cover_results.csv','.github/workflows/repository-validation.yml'
]
PRIVATE_PATTERNS = ['main.tex','main.pdf','cover_letter','cover-letter','author_photo','graphical_abstract.tiff']

def rows(path):
    with (ROOT/path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main():
    missing=[p for p in REQUIRED if not (ROOT/p).is_file()]
    assert not missing, f'Missing required files: {missing}'
    manifest=rows('REPOSITORY_MANIFEST.csv')
    listed={r['path'] for r in manifest}
    public=[]
    for p in ROOT.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in {'REPOSITORY_MANIFEST.csv'} or rel.startswith('.git/') or '__pycache__' in rel or rel.startswith('.pytest_cache/') or rel.startswith('figures/'):
            continue
        public.append(rel)
    unlisted=sorted(set(public)-listed)
    assert not unlisted, f'Public files missing from manifest: {unlisted}'
    lower_paths=[p.relative_to(ROOT).as_posix().lower() for p in ROOT.rglob('*') if p.is_file()]
    forbidden=[p for p in lower_paths for token in PRIVATE_PATTERNS if token in p and p != 'manuscript/readme.md']
    assert not forbidden, f'Journal-private file leaked into public repository: {forbidden}'
    summary=json.loads((ROOT/'results/frozen/summary.json').read_text(encoding='utf-8'))
    assert summary['seed']==20260712
    assert sum(x['instances'] for x in summary['tree_validation'].values())==100
    assert all(abs(x['agreement']-1.0)<1e-12 for x in summary['tree_validation'].values())
    assert sum(x['instances'] for x in summary['fvs_validation'].values())==60
    assert all(abs(x['agreement']-1.0)<1e-12 for x in summary['fvs_validation'].values())
    assert sum(x['instances'] for x in summary['correction_validation'].values())==60
    assert max(x['max_abs_error'] for x in summary['correction_validation'].values()) < 1e-15
    assert sum(x['instances'] for x in summary['cover'].values())==180
    assert any(k.startswith('5000-') for k in summary['scalability'])
    assert len(rows('results/frozen/tree_validation.csv'))==100
    assert len(rows('results/frozen/fvs_validation.csv'))==60
    assert len(rows('results/frozen/correction_validation.csv'))==60
    print('PASS: curated public artifact structure')
    print('PASS: journal-private submission files excluded')
    print('PASS: frozen seed and numerical invariants')
    print('PASS: tree 100/100; FVS 60/60; correction 60/60; cover 180 instances')

if __name__=='__main__':
    main()
