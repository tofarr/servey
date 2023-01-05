import os
from dataclasses import replace
from unittest import TestCase

from servey.action.action import action
from servey.finder.module_action_finder import ModuleActionFinder


class TestModuleActionFinder(TestCase):
    def test_default_constructor(self):
        finder = ModuleActionFinder()
        self.assertEqual(ModuleActionFinder("servey_main.actions"), finder)
        os.environ["SERVEY_MAIN"] = "foobar"
        finder = ModuleActionFinder()
        self.assertEqual(ModuleActionFinder("foobar.actions"), finder)
        os.environ.pop("SERVEY_MAIN")

    def test_find_actions(self):
        finder = ModuleActionFinder("tests.finder.test_module_action_finder")
        actions = list(finder.find_actions())
        expected = [
            replace(foo.__servey_action__, fn=actions[0].fn),
            replace(bar.__servey_action__, fn=actions[1].fn),
        ]
        self.assertEqual(expected, actions)
        self.assertIsNone(actions[0].fn())
        self.assertEqual("Value: 5", actions[1].fn(5))

    def test_find_actions_not_found(self):
        finder = ModuleActionFinder("this.module.does.not.exist")
        self.assertEqual([], list(finder.find_actions()))


@action
def foo() -> type(None):
    pass


@action
def bar(value: int) -> str:
    return f"Value: {value}"


foo()
bar(10)
