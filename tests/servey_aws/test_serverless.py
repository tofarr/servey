import os
from dataclasses import field, dataclass
from io import StringIO
from os.path import exists
from pathlib import Path
from typing import Dict
from unittest import TestCase
from unittest.mock import patch

from servey.__main__ import generate_serverless_scaffold
from servey.action.action import get_action
from servey.errors import ServeyError
from servey.servey_aws.serverless.trigger_handler.fixed_rate_trigger_handler import (
    FixedRateTriggerHandler,
)
from servey.servey_aws.serverless.yml_config.subscription_function_config import (
    SubscriptionFunctionConfig,
)
from servey.servey_aws.serverless.yml_config.yml_config_abc import ensure_ref_in_file
from servey.trigger.fixed_rate_trigger import FixedRateTrigger
from tests.specs.number_spec.actions import integer_stats_publisher


class TestServerless(TestCase):
    def test_generate(self):
        mock_file_system = MockFileSystem()
        # noinspection SpellCheckingInspection
        with (
            patch("os.path.exists", mock_file_system.exists),
            patch("builtins.open", mock_file_system.open),
            patch("pathlib.PosixPath.mkdir", mock_file_system.mkdir),
            patch.dict(os.environ, {"SERVEY_MAIN": "tests.specs.number_spec"}),
        ):
            generate_serverless_scaffold()
        generated_files = [
            "serverless.yml",
            "serverless_servey/kms_resource.yml",
            "serverless_servey/kms_role_statement.yml",
            "serverless_servey/subscriptions_handlers.yml",
            "serverless_servey/subscriptions_resources.yml",
            "serverless_servey/subscriptions_role_statement.yml",
            "serverless_servey/schema.graphql",
            "serverless_servey/appsync.yml",
            "serverless_servey/actions.yml",
        ]
        for generated_file in generated_files:
            self.assertIn(generated_file, mock_file_system.contents)
        # More checks on the content of the files would be appropriate here

    def test_fixed_rate_trigger_handler(self):
        with self.assertRaises(ServeyError):
            FixedRateTriggerHandler().handle_trigger(
                get_action(integer_stats_publisher), FixedRateTrigger(30), {}
            )

    def test_subscription_function_config_no_subscriptions(self):
        config = SubscriptionFunctionConfig(subscriptions=[])
        config.configure("")

    def test_ensure_ref_in_files_not_yet_existing(self):
        mock_file_system = MockFileSystem(
            {
                "main.yml": ResetOnCloseStringIO(
                    """
    foo:
        ping: 1         
                    """
                )
            }
        )
        with (patch("builtins.open", mock_file_system.open),):
            ensure_ref_in_file(
                main_serverless_yml_file="main.yml",
                insertion_point=["foo", "bar", "zap"],
                referenced_serverless_yml_file="referenced.yml",
                referenced_path=None,
            )
        value = mock_file_system.contents["main.yml"].getvalue()
        expected_value = """foo:
  ping: 1
  bar:
    zap:
    - ${file(referenced.yml)}
"""
        self.assertEqual(expected_value, value)

    def test_ensure_ref_in_files_wrong_type(self):
        mock_file_system = MockFileSystem(
            {
                "main.yml": ResetOnCloseStringIO(
                    """
foo:
    bar: 1         
                """
                )
            }
        )
        with (patch("builtins.open", mock_file_system.open),):
            with self.assertRaises(ValueError):
                ensure_ref_in_file(
                    main_serverless_yml_file="main.yml",
                    insertion_point=["foo", "bar"],
                    referenced_serverless_yml_file="referenced.yml",
                    referenced_path=None,
                )

    def test_ensure_ref_in_files_already_exists(self):
        mock_file_system = MockFileSystem(
            {
                "main.yml": ResetOnCloseStringIO(
                    """
foo:
    bar:
        zap:
        - ${file(referenced.yml)}
                """
                )
            }
        )
        with (patch("builtins.open", mock_file_system.open),):
            ensure_ref_in_file(
                main_serverless_yml_file="main.yml",
                insertion_point=["foo", "bar", "zap"],
                referenced_serverless_yml_file="referenced.yml",
                referenced_path=None,
            )
            value = mock_file_system.contents["main.yml"].getvalue()
            print(value)


_open = open
_mkdir = Path.mkdir
_exists = exists


@dataclass
class MockFileSystem:
    contents: Dict[str, StringIO] = field(default_factory=dict)

    def mkdir(self, parents: bool, exist_ok: bool):
        pass

    def exists(self, path):
        return path in self.contents

    def open(self, path: str, mode: str):
        if mode == "r":
            result = self.contents[path]
            return result
        elif mode == "w":
            result = self.contents[path] = ResetOnCloseStringIO()
            return result


class ResetOnCloseStringIO(StringIO):
    def close(self):
        self.seek(0)
