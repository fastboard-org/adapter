from src.lib.parameters import replace_parameters


def test_replace_string_parameters_on_string():
    parameters = {"name": "ditto"}
    string = "pokemon/{{name}}"
    assert replace_parameters(string, parameters) == "pokemon/ditto"


def test_replace_int_parameters_on_string():
    parameters = {"number": 25}
    string = "pokemon/{{number}}"
    assert replace_parameters(string, parameters) == "pokemon/25"


def test_replace_string_parameters_on_string_with_multiple_parameters():
    parameters = {"name": "ditto", "type": "normal"}
    string = "pokemon/{{name}}/{{type}}"
    assert replace_parameters(string, parameters) == "pokemon/ditto/normal"


def test_string_without_parameters():
    parameters = {"name": "ditto"}
    string = "pokemon"
    assert replace_parameters(string, parameters) == "pokemon"


def test_string_parameters_on_dictionary():
    parameters = {"name": "ditto"}
    dictionary = {"body": ["something", "{{name}}"]}
    assert replace_parameters(dictionary, parameters) == {"body": ["something", "ditto"]}


def test_string_parameters_as_keys_and_values_on_dictionary():
    parameters = {"name": "ditto", "type": "normal"}
    dictionary = {"{{name}}": "{{type}}"}
    assert replace_parameters(dictionary, parameters) == {"ditto": "normal"}


def test_mixed_parameters_on_list_of_dicts():
    parameters = {"name": "ditto", "type": "normal"}
    list_of_dicts = [{"{{name}}": "{{type}}"}, {"{{type}}": "{{name}}"}]
    assert replace_parameters(list_of_dicts, parameters) == [
        {"ditto": "normal"},
        {"normal": "ditto"},
    ]
