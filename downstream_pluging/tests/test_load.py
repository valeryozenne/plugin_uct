import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('downstream_pluging')
def test_import(server):
    assert 'downstream_pluging' in loadedPlugins()
