import pytest
from types import SimpleNamespace
from vareq import vaconfig
from vareq.vaengine import EngineConfig
from vareq.vaserver import ServerConfig


def test_find_parent_for_attribute_retrieves_parent():
    obj = SimpleNamespace()
    obj.a = SimpleNamespace()
    obj.a.b = SimpleNamespace()
    obj.a.b.c = "test"
    path = ["a", "b", "c"]
    parent = vaconfig.find_parent_for_attribute(obj, path)
    assert hasattr(parent, "c")
    assert parent is obj.a.b


def test_find_parent_for_attribute_returns_none_when_search_fails():
    obj = SimpleNamespace()
    obj.a = SimpleNamespace()
    obj.a.b = SimpleNamespace()
    obj.a.b.c = "test"
    path = ["a", "z", "c"]
    parent = vaconfig.find_parent_for_attribute(obj, path)
    assert parent is None


def test_update_nested_object_attribute_from_json_succeeds():
    obj = SimpleNamespace()
    obj.x = 0
    obj.a = SimpleNamespace()
    obj.a.b = SimpleNamespace()
    obj.a.b.c = "test"
    json_data = {"a": {"b": {"c": "tested"}}, "x": 10}
    vaconfig.update_nested_object_attribute_from_json(obj, json_data)
    assert "tested" == obj.a.b.c
    assert 10 == obj.x


def test_update_nested_object_attribute_from_json_silently_ignores_non_json():
    obj = SimpleNamespace()
    obj.a = SimpleNamespace()
    obj.a.b = SimpleNamespace()
    obj.a.b.c = "test"
    vaconfig.update_nested_object_attribute_from_json(obj, "something")
    assert "test" == obj.a.b.c


def test_update_engine_configuration_from_json_succeeds():
    config = EngineConfig()
    config.batch_query_context_size = 10
    config.chat_config.query_template = "dummy"
    config_json = {
        "batch_query_context_size": 32,
        "chat_config": {"query_template": "tested"},
    }
    updated = vaconfig.update_engine_configuration_from_json(config, config_json)
    assert 32 == updated.batch_query_context_size
    assert "tested" == updated.chat_config.query_template


def test_update_engine_configuration_from_json_returns_new_if_no_default_is_provided():
    updated = vaconfig.update_engine_configuration_from_json(
        None, {"batch_query_context_size": 16}
    )
    assert isinstance(updated, EngineConfig)
    assert updated.batch_query_context_size == 16


def test_update_engine_configuration_from_json_returns_config_if_json_none():
    config = EngineConfig()
    result = vaconfig.update_engine_configuration_from_json(config, None)
    assert result is config


def test_update_server_configuration_from_json_succeeds():
    config = ServerConfig()
    config.host = "localhost"
    config.port = 8000
    config_json = {
        "host": "1.2.3.4",
        "port": 9000,
    }
    updated = vaconfig.update_server_configuration_from_json(config, config_json)
    assert "1.2.3.4" == updated.host
    assert 9000 == updated.port


def test_update_server_configuration_from_json_returns_new_if_no_default_is_provided():
    updated = vaconfig.update_server_configuration_from_json(
        None, {"host": "example.com", "port": 5000}
    )
    assert isinstance(updated, ServerConfig)
    assert "example.com" == updated.host
    assert 5000 == updated.port


def test_update_server_configuration_from_json_returns_config_if_json_none():
    config = ServerConfig()
    config.host = "example.com"
    result = vaconfig.update_server_configuration_from_json(config, None)
    assert result is config
    assert "example.com" == result.host
