from girder import plugin
from girder import events
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.constants import AccessType, TokenScope
from girder.exceptions import RestException
from girder.plugin import GirderPlugin
from girder.models.item import Item
from girder.models.file import File
from girder.utility import search
from girder.utility.progress import setResponseTimeLimit
import girder_client

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'NewRoutes'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        routes = MakeRoutes()
        info['apiRoot'].item.route(
            'POST', (':id', 'SpamMetadata'), routes.makeSpamMetadata)
        info['apiRoot'].item.route(
            'POST', (':id', 'SpamFile'), routes.makeSpamFile)
        info['apiRoot'].item.route(
            'POST', (':id', 'SpamEmail'), routes.makeSpamEmail)
        pass

class MakeRoutes(Resource):

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('spam metadata')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.READ, paramType='path')
        .param('metadataKey', 'Pass the key',
               required=True)
        .param('metadataValue', 'Pass the value',
               required=True)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def makeSpamMetadata(self, item, metadataKey, metadataValue):
        user = self.getCurrentUser()
        itemObj = Item().load(item['_id'], force=True, user=user)
        Item().setMetadata(itemObj, {metadataKey: metadataValue})
        print("Metadata ajouté dans l\'item avec succès.")
        pass

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('It Does Something')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.READ)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def makeSpamFile(self, item):
        user = self.getCurrentUser()
        itemObj = Item().load(item['_id'], force=True, user=user)
        file = File().createFile(creator,
                item=item,
                name='emptyFile.txt',
                size=0,
                assetstore=item['assetstoreId']
        )
        print("Fichier texte vide ajouté dans l\'item.")
        pass

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('It Does Something')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.WRITE, paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def makeSpamEmail(self, item):
        print("I was here")
        pass
