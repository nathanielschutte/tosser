from enum import Enum
import dataclasses


class TosserSchemaType(Enum):
    """Schema type enum"""

    STRING = 'string'
    INTEGER = 'integer'
    DECIMAL = 'decimal'
    BOOLEAN = 'boolean'
    NULL = 'null'
    TIME = 'time'
    DATE = 'date'
    DATETIME = 'datetime'
    OBJECT = 'object'
    ARRAY = 'array'
    UNKNOWN = 'unknown'


@dataclasses.dataclass
class TosserSchemaTypeVar:
    """Wrap schema types with metadata"""
    
    type: TosserSchemaType
    length: int | None = None

    def __str__(self) -> str:
        """Return the string representation of the type"""

        if self.length is None:
            return self.type.value
        else:
            return f'{self.type.value}({self.length})'

    @staticmethod
    def from_string(type_str: str) -> 'TosserSchemaTypeVar':
        """Create a TosserSchemaTypeVar from a string"""

        length = None
        length_part = type_str.split('(')
        if len(length_part) > 1:
            type_str = length_part[0]
            length = int(length_part[1].split(')')[0])

        return TosserSchemaTypeVar(
            type=TosserSchemaType(type_str),
            length=length,
        )
