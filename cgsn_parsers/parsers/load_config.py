#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.load_config
@file cgsn_parsers/parsers/load_config.py
@author Christopher Wingard
@brief Utility to load a YAML configuration file and replace any variables with
    values from the configuration file.
"""
import yaml
import re


def load_config(file_path):
    """
    Load a YAML configuration file and replace any variables with values from the
    configuration file. Variables are defined as ${var_name} and can include nested
    keys like ${var_name.key1.key2}.

    :param file_path:
    :return parsed_yaml: YAML configuration file with variables replaced by values
        defined in the configuration file.
    """
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
