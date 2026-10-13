"""Export the API's OpenAPI specification to docs/openapi.json.

Usage: python export_openapi.py [output_path]
"""

import json
import sys
from pathlib import Path

from app.main import app

out = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/openapi.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"OpenAPI exported to {out}")
