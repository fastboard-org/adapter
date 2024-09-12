from src.lib.object_id import replace_objectid_strings
from bson import ObjectId


def test_replace_empty_dict():
    assert replace_objectid_strings({}) == {}


def test_replace_objectid_strings_on_string():
    string = "ObjectId('5f6c6f6e6e656374696f6f6e')"
    replaced_string = replace_objectid_strings(string)
    assert replaced_string == ObjectId("5f6c6f6e6e656374696f6f6e")


def test_replace_objectid_strings_on_list_of_strings():
    list_of_strings = [
        "ObjectId('5f6c6f6e6e656374696f6f6e')",
        "ObjectId('5f6c6f6e6e656374696f6f6f')",
    ]
    replaced_list = replace_objectid_strings(list_of_strings)
    assert replaced_list == [
        ObjectId("5f6c6f6e6e656374696f6f6e"),
        ObjectId("5f6c6f6e6e656374696f6f6f"),
    ]


def test_replace_objectid_strings_on_dict():
    dictionary = {
        "id": "ObjectId('5f6c6f6e6e656374696f6f6e')",
        "name": "ditto",
    }
    replaced_dict = replace_objectid_strings(dictionary)
    assert replaced_dict == {
        "id": ObjectId("5f6c6f6e6e656374696f6f6e"),
        "name": "ditto",
    }


def test_replace_objectid_strings_on_nested_dict():
    dictionary = {
        "id": "ObjectId('5f6c6f6e6e656374696f6f6e')",
        "name": "ditto",
        "nested": {
            "id": "ObjectId('5f6c6f6e6e656374696f6f6f')",
            "name": "eevee",
        },
    }
    replaced_dict = replace_objectid_strings(dictionary)
    assert replaced_dict == {
        "id": ObjectId("5f6c6f6e6e656374696f6f6e"),
        "name": "ditto",
        "nested": {
            "id": ObjectId("5f6c6f6e6e656374696f6f6f"),
            "name": "eevee",
        },
    }


def test_replace_objectid_string_on_nested_dict_with_objectid_as_key_and_value():
    dictionary = {
        "id": "ObjectId('5f6c6f6e6e656374696f6f6e')",
        "name": "ditto",
        "nested": {
            "ObjectId('5f6c6f6e6e656374696f6f6f')": "ObjectId('5f6c6f6e6e656374696f6f6e')",
            "name": "eevee",
        },
        "ObjectId('5f6c6f6e6e656374696f6f6f')": ["ObjectId('5f6c6f6e6e656374696f6f6e')"],
    }
    replaced_dict = replace_objectid_strings(dictionary)
    assert replaced_dict == {
        "id": ObjectId("5f6c6f6e6e656374696f6f6e"),
        "name": "ditto",
        "nested": {
            ObjectId("5f6c6f6e6e656374696f6f6f"): ObjectId("5f6c6f6e6e656374696f6f6e"),
            "name": "eevee",
        },
        ObjectId("5f6c6f6e6e656374696f6f6f"): [ObjectId("5f6c6f6e6e656374696f6f6e")],
    }
