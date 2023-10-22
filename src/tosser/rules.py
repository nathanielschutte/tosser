
# Rules for seeking objects during traversal

import json
from pathlib import Path
from typing import List, Tuple, Generator
from enum import Enum
from dataclasses import dataclass


class TosserRuleState(Enum):
    UNKNOWN = -1
    AWAIT_NEXT_OBJECT = 0
    AWAIT_ANY_OBJECT = 1


@dataclass
class TosserRule():
    seek_path: List[str]
    seek_fields: List[str]
    state: TosserRuleState = TosserRuleState.UNKNOWN

    @property
    def seek_id(self) -> str | None:
        return self.seek_path[len(self.seek_path) - 1] if len(self.seek_path) > 0 else None

    @property
    def seek_path_is_absolute(self) -> bool:
        return self.seek_path[0] == '$' if len(self.seek_path) > 0 else False

    @property
    def seek_is_all_fields(self) -> bool:
        return len(self.seek_fields) == 1 and self.seek_fields[0] == '*'

    def __iter__(self):
        self._n = 0
        return self

    def next(self) -> str:
        if self._n < len(self.seek_path):
            return self.seek_path[self._n]
        else:
            raise StopIteration()
        
    def __repr__(self) -> str:
        return json.dumps({
            'seek_path': self.seek_path,
            'seek_fields': self.seek_fields,
            'state': self.state.value
        }, indent=4)


class TosserRuleSet:
    def __init__(self) -> None:
        self.rules: List[TosserRule] = []

    # Receive current context so we can trim the ruleset as we go
    # Return list of unmatched rules
    def _next_rules(self) -> Generator[List[TosserRule], Tuple[str, bool], List[TosserRule]]:
        root_identifier = True
        current_identifier = '$'

        matched_rules = self.rules

        for rule in self.rules:
            next_id = rule.seek_id
            print(f'{current_identifier=} {next_id=}')

        context: Tuple[str, bool] = yield matched_rules

        return self.rules


    # def _quick_load(self, path: Path) -> None:
    #     with open(path, 'r') as file:
    #         self.data = json.loads(file.read())

    def _demo_set(self) -> None:
        self.rules = [
            TosserRule(['$', 'users'], ['*'])
        ]

    def __repr__(self) -> str:
        return '\n'.join(list(map(lambda r: str(r), self.rules)))
