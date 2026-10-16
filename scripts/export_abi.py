from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
OUTPUT = ROOT / "static" / "contracts"


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in ("RoleRegistry", "CertificateRegistry", "CertificateMarket"):
        artifact = json.loads((ARTIFACTS / f"{name}.json").read_text(encoding="utf-8"))
        (OUTPUT / f"{name}.json").write_text(json.dumps(artifact["abi"], indent=2), encoding="utf-8")
        print(f"Exported {name} ABI")
