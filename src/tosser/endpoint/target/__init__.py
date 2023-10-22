from tosser.endpoint.target.target import ITarget, TargetDriver, TargetCall, TargetCallDynamic
from tosser.endpoint.target.detail import DetailTarget

TARGET_DRIVERS = {
    'detail': DetailTarget,
    'mysql': None
}

__all__ = ['ITarget', 'TargetDriver', 'DetailTarget' 'TARGET_DRIVERS']
