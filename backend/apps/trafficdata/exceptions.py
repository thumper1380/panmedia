class TrafficDataException(Exception):
    ...


class RotationNotFound(TrafficDataException):
    ...


class PushLeadException(TrafficDataException):
    ...


class InvalidSecret(TrafficDataException):
    ...


class InvalidToken(TrafficDataException):
    ...

