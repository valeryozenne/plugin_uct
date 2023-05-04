import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('newroutes')
def test_import(server):
    assert 'newroutes' in loadedPlugins()
