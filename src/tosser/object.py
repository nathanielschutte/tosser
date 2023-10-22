
import json
from pathlib import Path
from typing import Dict, List, Any

class TosserObject:
    def __init__(self) -> None:
        self.metadata: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}

    def _quick_load(self, path: Path) -> None:
        with open(path, 'r') as file:
            self.data = json.loads(file.read())

    def __repr__(self) -> str:
        return json.dumps(self.data, indent=4)
