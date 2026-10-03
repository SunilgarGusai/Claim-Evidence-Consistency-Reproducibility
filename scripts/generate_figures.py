from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import figures as F

out=ROOT/"figures"; out.mkdir(exist_ok=True)
F.framework(out/"claim-evidence-framework.svg")
F.complexity_map(out/"complexity-landscape.svg")
F.certificate_anatomy(out/"certificate-anatomy.svg")
F.runtime_validation(out/"runtime-validation.pdf", ROOT)
F.scalability(out/"tree-scalability.pdf", ROOT)
F.cover_ratio(out/"evidence-cover-ratio.pdf", ROOT)
print("PASS: reviewer-facing scientific figures regenerated")
