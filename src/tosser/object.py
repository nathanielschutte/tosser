import json
from pathlib import Path
from typing import Dict, List, Any
import dataclasses

@dataclasses.dataclass
class TosserObject:
    metadata: Dict[str, Any]
    data: Dict[str, Any]

    def _quick_load(self, path: Path) -> None:
        with open(path, 'r') as file:
            self.data = json.loads(file.read())

    def __repr__(self) -> str:
        metadata = json.dumps(self.metadata, indent=4)
        data = json.dumps(self.data, indent=4)
        return f'<TosserObject metadata={metadata} data={data}>'
