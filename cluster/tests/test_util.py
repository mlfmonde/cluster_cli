import unittest
from cluster import util


class TestUtils(unittest.TestCase):

    def test_json2object(self):
        obj = util.json2obj(
            """{
                "dict_var": {
                    "dict-var2": {
                        "string.var": "a string",
                        "int_var": 123,
                        "string-list": [
                            "el1",
                            "el2",
                            "el3"
                        ]
                    }
                },
                "int-array": [
                    1, 2, 3
                ]
            }"""
        )
        self.assertEqual(
            obj.dict_var.dict_var2.string_var,
            "a string"
        )
        self.assertEqual(
            obj.dict_var.dict_var2.int_var,
            123
        )
        self.assertEqual(
            obj.dict_var.dict_var2.string_list,
            ["el1", "el2", "el3"]
        )
        self.assertEqual(
            obj.int_array,
            [1, 2, 3]
        )

    def test_json2object_no_data(self):
        self.assertFalse(util.json2obj(None))
