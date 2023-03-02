import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('plugin_uct')
def test_import(server):
    assert 'plugin_uct' in loadedPlugins()
