from unittest import TestCase

from servey.action.util import (
    get_marshaller_for_params,
    get_schema_for_params,
    move_ref_items_to_components,
)


class TestUtil(TestCase):
    def test_params_missing_annotation(self):
        # noinspection PyUnusedLocal
        def dummy(foo):
            """Dummy"""

        with self.assertRaises(TypeError):
            get_marshaller_for_params(dummy, set())
        with self.assertRaises(TypeError):
            get_schema_for_params(dummy, set())

    def test_move_ref_items_to_components(self):
        root = {
            "anyOf": [
                {
                    "type": "object",
                    "name": "Node",
                    "properties": {
                        "name": {"type": "string"},
                        "child": {
                            "anyOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "a": {"$ref": "#/anyOf/0"},
                                        "b": {"$ref": "#/anyOf/0"},
                                    },
                                },
                                {"type": "null"},
                            ]
                        },
                    },
                },
                {"type": "null"},
            ]
        }
        components = {}
        result = move_ref_items_to_components(root, root, components)
        self.assertEqual(
            {
                "Node": {
                    "name": "Node",
                    "properties": {
                        "child": {
                            "anyOf": [
                                {
                                    "properties": {
                                        "a": {"$ref": "#/components/Node"},
                                        "b": {"$ref": "#/components/Node"},
                                    },
                                    "type": "object",
                                },
                                {"type": "null"},
                            ]
                        },
                        "name": {"type": "string"},
                    },
                    "type": "object",
                }
            },
            components,
        )
        self.assertEqual(
            {"anyOf": [{"$ref": "#/components/Node"}, {"type": "null"}]}, result
        )
