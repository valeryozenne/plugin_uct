import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('plugin_ihu_uct_main')
def test_import(server):
    assert 'plugin_ihu_uct_main' in loadedPlugins()
