from girder import plugin
from girder import events
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.constants import AccessType, TokenScope
from girder.exceptions import RestException
from girder.plugin import GirderPlugin
from girder.models.item import Item
from girder.utility import mail_utils
from girder.models.file import File
from girder.models.user import User
from girder.utility import search
from girder.utility.progress import setResponseTimeLimit
import girder_client

class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'NewRoutes'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        routes = MakeRoutes()
        info['apiRoot'].item.route(
            'POST', (':id', 'createMetadata'), routes.createMetadata)
        info['apiRoot'].item.route(
            'POST', (':id', 'runJob'), routes.runJob)
        info['apiRoot'].item.route(
            'POST', (':id', 'sendEmail'), routes.sendEmail)
        pass

class MakeRoutes(Resource):

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('create metaddata')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.READ, paramType='path')
        .param('metadataKey', 'Pass the key',
               required=True)
        .param('metadataValue', 'Pass the value',
               required=True)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def createMetadata(self, item, metadataKey, metadataValue):
        user = self.getCurrentUser()
        itemObj = Item().load(item['_id'], force=True, user=user)
        Item().setMetadata(itemObj, {metadataKey: metadataValue})
        print("Metadata ajouté dans l\'item avec succès.")
        pass

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('Running the job')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.READ)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def runJob(self, item):
        for file in Item().childFiles(item):
            events.trigger('Run job', file)
        message = "job that you launched ended successfuly"
        user = self.getCurrentUser()
        user_email = user['email']
        mail_utils.sendMail(subject='My mail from girder', text=message, to=user_email)

        pass

    @access.user(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('Send Email to user')
        .modelParam('id', 'The item ID',
                    model='item', level=AccessType.WRITE, paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the item.', 403)
    )
    def sendEmail(self, item):
        message = ""
        user = self.getCurrentUser()
        user_email = user['email']
        mail_utils.sendMail(subject='My mail from girder', text=message, to=user_email) 
        pass
