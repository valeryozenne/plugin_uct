from girder import plugin


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'plugin_uct'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here
        pass
