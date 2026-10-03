from pathlib import Path
import json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiments import run
out=ROOT/'results'/'reproduced'
if out.exists(): shutil.rmtree(out)
summary=run(out)
print(json.dumps(summary, indent=2))
print(f'Fresh deterministic results written to {out.relative_to(ROOT)}')
