import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('plugin_ihu_uct_newroutes')
def test_import(server):
    assert 'plugin_ihu_uct_newroutes' in loadedPlugins()
