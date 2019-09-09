from pprint import pprint
import importlib.util


def load_config_from_file(config_module_path):
    spec = importlib.util.spec_from_file_location("config", config_module_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def print_config(config):
    res = {}
    for k, v in config.__dict__.items():
        if not k.startswith('__') and not callable(v):
            res[k] = v
    pprint(res)
