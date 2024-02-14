import yaml
import re


def load_config(file_path):
    def subst(match):
        var_name = match.group(1)
        keys = var_name.split('.')
        value = data
        for key in keys:
            value = value[key]
        return str(value)

    with open(file_path, 'r') as file:
        content = file.read()

    data = yaml.safe_load(content)
    pattern = re.compile(r'\$\{([^}]+)}')  # matches ${var_name}, including nested keys like ${var_name.key1.key2}
    new_content = pattern.sub(subst, content)

    parsed_yaml = yaml.safe_load(new_content)
    return parsed_yaml
