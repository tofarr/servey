from enum import Enum


class ActionType(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
