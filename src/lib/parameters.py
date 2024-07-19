def replace_parameters(string, parameters):
    for parameter, parameter_value in parameters.items():
        parameter_to_replace = "{{" + parameter + "}}"
        if parameter_to_replace in string:
            string = string.replace(parameter_to_replace, parameter_value)
    return string
