import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('pfa_pluging')
def test_import(server):
    assert 'pfa_pluging' in loadedPlugins()
