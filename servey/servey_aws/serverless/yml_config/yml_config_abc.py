from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import List, Optional, Callable, Set

from injecty import get_impls
from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.errors import ServeyError

GENERATED_HEADER = """
This file was auto generated by servey. Manual modifications may be lost.
""".strip()


class YmlConfigABC(ABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    @abstractmethod
    def configure(self, main_serverless_yml_file: str):
        """Configure the serverless env"""


def configure(main_serverless_yml_file: str, skip: Set[str]):
    skip = set(skip)
    for impl in get_impls(YmlConfigABC):
        if impl.__name__ in skip:
            skip.remove(impl.__name__)
        else:
            impl().configure(main_serverless_yml_file)
    if skip:
        raise ServeyError(f"unknown_skip:{skip}")


def ensure_ref_in_file(
    main_serverless_yml_file: str,
    insertion_point: List[str],
    referenced_serverless_yml_file: str,
    referenced_path: Optional[str] = None,
):
    yaml = YAML()
    with open(main_serverless_yml_file, "r") as reader:
        root = yaml.load(reader)
        reference = "${file(" + referenced_serverless_yml_file + ")"
        if referenced_path:
            reference = reference + ":" + referenced_path + ", ''"
        reference += "}"
        parent = _follow_path(root, insertion_point[:-1])
        references = parent.get(insertion_point[-1])
        if not references:
            parent[insertion_point[-1]] = [reference]
        elif not isinstance(references, list):
            raise ValueError(
                f"{main_serverless_yml_file} : {'.'.join(insertion_point)} should be a list!"
            )
        elif reference in references:
            return  # Already exists - no action_ needed
        else:
            references.append(reference)
    with open(main_serverless_yml_file, "w") as writer:
        yaml.dump(root, writer)


def _follow_path(root, path: List[str]):
    node = root
    for key in path:
        child = node.get(key)
        if child is None:
            child = node[key] = {}
        node = child
    return node


def create_yml_file(
    file_name: str,
    content: ExternalItemType,
    str_mutate: Optional[Callable[[str], str]] = None,
):
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)
    with open(file_name, "w") as writer:
        writer.write("# ")
        writer.write(GENERATED_HEADER.replace("\n", "\n# "))
        writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
        yaml = YAML()
        sio = StringIO()
        yaml.dump(content, sio)
        result = sio.getvalue()
        if str_mutate:
            result = str_mutate(result)
        writer.write(result)
