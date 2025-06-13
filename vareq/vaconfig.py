from typing import List
from .vaengine import EngineConfig
from .vaserver import ServerConfig
import logging


def find_parent_for_attribute(obj: object, path: List[str]) -> object:
    current_obj = obj
    for i, element in enumerate(path[:-1]):
        if hasattr(current_obj, element):
            current_obj = getattr(current_obj, element)
        else:
            return None
    return current_obj


def update_nested_object_attribute_from_json(
    obj: object, json_data: dict, path: str = ""
):
    # Safety measure when descending the JSON
    if not isinstance(json_data, dict):
        return

    for key, value in json_data.items():
        item_path = f"{path}.{key}" if path else key
        logging.debug(f"Setting value for {item_path}: {value}")

        path_elements = item_path.split(".")
        parent = find_parent_for_attribute(obj, path_elements)

        if hasattr(parent, key):
            if isinstance(value, dict):
                update_nested_object_attribute_from_json(
                    getattr(parent, key), value, ""
                )
            else:
                setattr(parent, key, value)


def update_engine_configuration_from_json(
    config: EngineConfig, config_json=None
) -> EngineConfig:
    if config is None:
        config = EngineConfig()

    if config_json is None:
        return config

    update_nested_object_attribute_from_json(config, config_json)
    return config

def update_server_configuration_from_json(
    config: ServerConfig, config_json=None
) -> ServerConfig:
    if config is None:
        config = ServerConfig()

    if config_json is None:
        return config

    update_nested_object_attribute_from_json(config, config_json)
    return config