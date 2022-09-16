from abc import ABC, abstractmethod
from typing import List

from marshy.factory.impl_marshaller_factory import get_impls
from ruamel.yaml import YAML


class YmlConfigABC(ABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    @abstractmethod
    def configure(self, main_serverless_yml_file: str):
        """ Configure the serverless env """


def configure(main_serverless_yml_file: str = 'serverless.yml'):
    for impl in get_impls(YmlConfigABC):
        impl().configure(main_serverless_yml_file)


def ensure_ref_in_file(main_serverless_yml_file: str, insertion_point: List[str], referenced_serverless_yml_file: str):
    yaml = YAML()
    with open(main_serverless_yml_file, 'r') as reader:
        root = yaml.load(reader)
        reference = "${file(" + referenced_serverless_yml_file + ")}"
        parent = _follow_path(root, insertion_point[:-1])
        references = parent.get(insertion_point[-1])
        if not references:
            parent[insertion_point[-1]] = [reference]
        elif not isinstance(references, list):
            raise ValueError(f"{main_serverless_yml_file} : {'.'.join(insertion_point)} should be a list!")
        elif reference in references:
            return  # Already exists - no action needed
        else:
            references.append(reference)
    with open(main_serverless_yml_file, 'w') as writer:
        yaml.dump(root, writer)


def _follow_path(root, path: List[str]):
    node = root
    for key in path:
        child = node.get(key)
        if child is None:
            child = node[key] = {}
        node = child
    return node