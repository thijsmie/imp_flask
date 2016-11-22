import importlib

from flask import Blueprint
import pytest

from imp_flask.blueprints import _factory, all_blueprints


def test_blueprint_instances():
    assert all([isinstance(bp, Blueprint) for bp in all_blueprints])
    assert len(all_blueprints) == len(set([bp.url_prefix for bp in all_blueprints if bp.url_prefix]))
    assert all([b.import_name.startswith('imp_flask.views.') for b in all_blueprints])


def test_importable():
    for bp in all_blueprints:
        importlib.import_module(bp.import_name)


def test_factory_bad():
    with pytest.raises(ImportError):
        _factory('test.123', '/test/123')


def test_factory():
    bp = _factory('home.index', '/test/123')
    assert 'imp_flask.views.home.index' == bp.import_name
    assert '/test/123' == bp.url_prefix
