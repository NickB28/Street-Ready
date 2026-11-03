"""Put week-04 on the import path so the tests can import lotbook."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))