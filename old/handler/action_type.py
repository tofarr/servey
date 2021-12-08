from enum import Enum


class ActionType(Enum):
    QUERY = 'query'
    MUTATION = 'mutation'
    SUBSCRIPTION = 'subscription'
