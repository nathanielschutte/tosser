from typing import Dict, Type

from tosser.endpoint.target.target import ITarget, TargetDriver, TargetCall, TargetCallDynamic
from tosser.endpoint.target.detail import DetailTarget

TARGET_DRIVERS: Dict[str, Type[ITarget]] = {
    'detail': DetailTarget
}

__all__ = ['ITarget', 'TargetDriver', 'DetailTarget' 'TARGET_DRIVERS']
