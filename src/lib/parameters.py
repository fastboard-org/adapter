import ast


def replace_parameters_in_string(string, parameters, used_parameters):
    for parameter, parameter_value in parameters.items():
        parameter_to_replace = "{{" + parameter + "}}"
        if parameter_to_replace in string:
            string = string.replace(parameter_to_replace, str(parameter_value))
            used_parameters.add(parameter)
    return string


def replace_parameters(obj, parameters, used_parameters=set()):
    if isinstance(obj, str):
        replaced_string = replace_parameters_in_string(obj, parameters, used_parameters)
        try:
            eval = ast.literal_eval(replaced_string)
            return eval
        except (ValueError, SyntaxError):
            return replaced_string
    elif isinstance(obj, list):
        return [replace_parameters(item, parameters, used_parameters) for item in obj]
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = replace_parameters(key, parameters, used_parameters)
            new_value = replace_parameters(value, parameters, used_parameters)
            new_dict[new_key] = new_value
        return new_dict
    else:
        return obj
